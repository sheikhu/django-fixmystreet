from datetime import datetime as dt

from django.db import models, connection
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.template.loader import render_to_string, TemplateDoesNotExist
from django.core.mail import EmailMultiAlternatives
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy, ugettext as _
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.contrib.gis.geos import fromstr
from django.contrib.gis.db import models

from transmeta import TransMeta
from fixmystreet.utils import FixStdImageField

import settings

#class Report:
    #pass
#post_save.connect(fix_exif_data, sender=Report)

class Report(models.Model):
    title = models.CharField(max_length=100, verbose_name=ugettext_lazy("Subject"))
    category = models.ForeignKey('ReportCategory', null=True, verbose_name=ugettext_lazy("Category"))
    ward = models.ForeignKey('Ward', null=True)

    author = models.ForeignKey(User, null=False)

    created_at = models.DateTimeField(auto_now_add=True)
    # last time report was updated
    updated_at = models.DateTimeField(null=True)

    is_hate = models.BooleanField(default=False)
    
    is_fixed = models.BooleanField(default=False)
    # time report was marked as 'fixed'
    fixed_at = models.DateTimeField(null=True, blank=True)

    # email where the report was sent
    email_sent_to = models.EmailField(null=True)
    
    # last time a reminder was sent to the person that filed the report.
    reminded_at = models.DateTimeField(auto_now_add=True)
    
    point = models.PointField(null=True, srid=31370)

    photo = FixStdImageField(upload_to="photos", blank=True, size=(380, 380), thumbnail_size=(66, 50))
    desc = models.TextField(blank=True, null=True, verbose_name=ugettext_lazy("Details"))
    address = models.CharField(max_length=255, verbose_name=ugettext_lazy("Location"))
    postalcode = models.CharField(max_length=4, verbose_name=ugettext_lazy("Postal Code"))

    objects = models.GeoManager()

    def get_absolute_url(self):
        return reverse("report_show", args=[self.id])

    def flagAsOffensive(self):
        msg = HtmlTemplateMail('flag_report', {
            'report_url': 'http://%s%s' % (Site.objects.get_current().domain, self.get_absolute_url()), 
            'report': self 
        }, [settings.EMAIL_ADMIN])
        msg.send()

    class Meta:
        ordering = ['updated_at', 'created_at']


#signal on a report to notify public authority that a report has been filled
@receiver(post_save,sender=Report)
def report_notify(sender, instance, **kwargs):
    if kwargs['created'] and not kwargs['raw']:
        NotificationResolver(instance).resolve()

#signal on a report to register author as subscriber to his own report
@receiver(post_save,sender=Report)
def report_subscribe_author(sender, instance, **kwargs):
    if kwargs['created']:
        ReportSubscription(report=instance, subscriber=instance.author).save()

class ReportUpdate(models.Model):
    """A new version of the status of a report"""
    report = models.ForeignKey(Report)
    desc = models.TextField(blank=True, null=True, verbose_name=ugettext_lazy("Details"))
    created_at = models.DateTimeField(auto_now_add=True)
    is_fixed = models.BooleanField(default=False)
    author = models.ForeignKey(User, null=False)

    class Meta:
        ordering = ['created_at']
        #order_with_respect_to = 'report'

#update the report, set updated_at and is_fixed correctly
@receiver(pre_save, sender=ReportUpdate)
def update_report(sender, instance, **kwargs):
    instance.report.updated_at = instance.created_at
    instance.report.is_fixed = instance.is_fixed
    instance.report.save()

#notify subscribers that report has been updated
@receiver(pre_save, sender=ReportUpdate)
def notify(sender, instance, **kwargs):
    if not kwargs['raw']:
        for subscribe in instance.report.reportsubscription_set.all():
            unsubscribe_url = 'http://{0}{1}'.format(Site.objects.get_current().domain, reverse("unsubscribe", args=[instance.report.id]))
            msg = HtmlTemplateMail('report_update', {'update': instance, 'unsubscribe_url': unsubscribe_url}, [subscribe.subscriber.email])
            msg.send()


class ReportSubscription(models.Model):
    """ 
    Report Subscribers are notified when there's an update to an existing report.
    """
    report = models.ForeignKey(Report)
    subscriber = models.ForeignKey(User, null=False)
    class Meta:
        unique_together = (("report", "subscriber"),)


class ReportCategoryClass(models.Model):
    __metaclass__ = TransMeta
    help_text = """
    Manage the category container list (see the report form). Allow to group categories.
    """

    name = models.CharField(max_length=100)

    def __unicode__(self):      
        return self.name

    class Meta:
        verbose_name = "category group"
        verbose_name_plural = "category groups"
        translate = ('name', )


class ReportCategory(models.Model):
    __metaclass__ = TransMeta
    help_text = """
    Manage the report categories list (see the report form).
    When a category is selected in the website form, the hint field is loaded in ajax and displayed  in the form.
    """

    name = models.CharField(verbose_name=_('Name'), max_length=100)
    hint = models.TextField(verbose_name=_('Hint'), blank=True, null=True)
    category_class = models.ForeignKey(ReportCategoryClass, verbose_name=_('Category group'), help_text="The category group container")
    def __unicode__(self):      
        return self.category_class.name + ":" + self.name
 
    class Meta:
        verbose_name = "category"
        verbose_name_plural = "categories"
        translate = ('name', 'hint', )


class Councillor(models.Model):
    help_text = """
    Represent a public authority that can resolve a problem from a fix my street report. 
    When a report if filled in the website, a notification mail will be sent to the corresponding 
    councillors that is able to resolve it.
    """
    
    name = models.CharField(max_length=100)
    
    # this email addr. is the destination for reports
    # if the 'Councillor' email rule is enabled
    email = models.EmailField(blank=True, null=True)
    # city = models.ForeignKey(City,null=True)

    def __unicode__(self):
        return self.name


# Override where to send a report for a given city.        
#
# If no rule exists, the email destination is the 311 email address 
# for that city.
#
# Cities can have more than one rule.  If a given report matches more than
# one rule, more than one email is sent.  (Desired behaviour for cities that 
# want councillors CC'd)
class NotificationRule(models.Model):
    help_text = """
    Declare that an extra Councillors has authority for resolving a problem and need to recieve notifiaction.
    """
    TO_COUNCILLOR = 0
    MATCHING_CATEGORY_CLASS = 1
    NOT_MATCHING_CATEGORY_CLASS = 2
    
    RuleChoices = (
        (TO_COUNCILLOR, 'All the time'),
        (MATCHING_CATEGORY_CLASS, 'Report\'s category group is ...'),
        (NOT_MATCHING_CATEGORY_CLASS, 'Report\'s category group is not ...'), 
    )
    
    rule = models.IntegerField(
        choices=RuleChoices,
        verbose_name='Send a notification if',
        help_text="compare to the category of the report and this selected category."
    )
    # the city this rule applies to 
    ward = models.ForeignKey(
        'Ward',
        null=False,
        help_text="The ward where the rule apply."
    )
    # filled in if this is a category class rule
    category_class = models.ForeignKey(
        ReportCategoryClass,null=True, blank=True,
        verbose_name='Category Group',
        help_text="Only set for 'Category Group' rule types."
    )
    # filled in if an additional email address is required for the rule type
    councillor = models.ForeignKey(Councillor, null=False)

    def __str__(self):
        return "%s - %s %s (%s)" % ( 
                self.councillor.name,
                (self.category_class and self.category_class.name or ''),
                self.RuleChoices[self.rule][1],
                self.ward.name
        )


class ReportNotification(models.Model):
    report = models.ForeignKey(Report)
    to_councillor = models.ForeignKey(Councillor)
    sent_at = models.DateTimeField()
    #status error/success ?

    def send(self):
        msg = HtmlTemplateMail('send_report_to_city', {'report': self.report}, (self.to_councillor.email,))
        if self.report.photo:
            msg.attach_file(self.report.photo.file.name)
        msg.send()
        self.sent_at = dt.now()


class NotificationResolver(object):
    def __init__(self, report):
        self.report = report
        self.rules = NotificationRule.objects.filter(ward=self.report.ward)

    def send(self, councillor):
        notification = ReportNotification(report=self.report, to_councillor=councillor)
        notification.send()
        notification.save()

    def resolve(self):
        if self.report.ward.councillor:
            self.send(self.report.ward.councillor)
        for rule in self.rules:
            if rule.rule == NotificationRule.TO_COUNCILLOR:
                self.send(rule.councillor)

            if rule.rule == NotificationRule.MATCHING_CATEGORY_CLASS:
                if self.report.category.category_class == rule.category_class:
                    self.send(rule.councillor)

            if rule.rule == NotificationRule.NOT_MATCHING_CATEGORY_CLASS:
                if self.report.category.category_class != rule.category_class:
                    self.send(rule.councillor)


class Province(models.Model):
    name = models.CharField(max_length=100)
    abbrev = models.CharField(max_length=3)


class City(models.Model):
    province = models.ForeignKey(Province)
    name = models.CharField(max_length=100)
    # the city's 311 email, if it has one.
    #email = models.EmailField(blank=True, null=True)    
    #category_set = models.ForeignKey(ReportCategorySet, null=True, blank=True)
    objects = models.GeoManager()

    def __unicode__(self):      
        return self.name
    
    def get_categories(self):
        if self.category_set:
            return self.category_set.categories
        else:
            # the 'Default' group is defined in fixtures/initial_data
            default = ReportCategorySet.objects.get(name='Default')
            return default.categories
    
    def get_absolute_url(self):
        return reverse('city_show', args[self.id])

    def get_rule_descriptions(self):
        rules = EmailRule.objects.filter(city=self)
        describer = emailrules.EmailRulesDesciber(rules, self)
        return describer.values()

    class Meta:
        verbose_name_plural = "cities"


class Ward(models.Model):
    name = models.CharField(max_length=100)
    councillor = models.ForeignKey(Councillor, null=True, blank=True)
    city = models.ForeignKey(City)
    # geom = models.MultiPolygonField( null=True)
    objects = models.GeoManager()
    feature_id = models.CharField(max_length=25)


    # this email addr. is the destination for reports
    # if the 'Ward' email rule is enabled
    # email = models.EmailField(blank=True, null=True)

    def get_absolute_url(self):
        return reverse('ward_show', args=[self.id])

    def __unicode__(self):      
        return self.city.name + " " + self.name


class ZipCode(models.Model):
    __metaclass__ = TransMeta
    
    ward = models.ForeignKey(Ward)
    code = models.CharField(max_length=4)
    name = models.CharField(max_length=100)
    hide = models.BooleanField()

    class Meta:
        translate = ('name', )


class FaqEntry(models.Model):
    __metaclass__ = TransMeta

    q = models.CharField(_('Question'), max_length=100)
    a = models.TextField(_('Answere'), blank=True, null=True)
    slug = models.SlugField(null=True, blank=True)
    order = models.IntegerField(null=True, blank=True)

    class Meta:
        verbose_name_plural = 'faq entries'
        translate = ('q', 'a')

@receiver(pre_save,sender=FaqEntry)
def save(sender, instance, **kwargs):
    if instance.order == None: 
        instance.order = instance.id + 1
    

class FaqMgr(object):
        
    def incr_order(self, faq_entry):
        if faq_entry.order == 1:
            return
        other = FaqEntry.objects.get(order=faq_entry.order-1)
        swap_order(other[0], faq_entry)
    
    def decr_order(self, faq_entry): 
        other = FaqEntry.objects.filter(order=faq_entry.order+1)
        if len(other) == 0:
            return
        swap_order(other[0],faq_entry)
        
    def swap_order(self, entry1, entry2):
        entry1.order = entry2.order
        entry2.order = entry1.order
        entry1.save()
        entry2.save()
 

class ReportCount(object):        
    def __init__(self, interval):
        self.interval = interval
    
    def dict(self):
        return({ "recent_new": "count( case when age(clock_timestamp(), reports.created_at) < interval '%s' THEN 1 ELSE null end )" % self.interval,
          "recent_fixed": "count( case when age(clock_timestamp(), reports.fixed_at) < interval '%s' AND reports.is_fixed = True THEN 1 ELSE null end )" % self.interval,
          "recent_updated": "count( case when age(clock_timestamp(), reports.updated_at) < interval '%s' AND reports.is_fixed = False and reports.updated_at != reports.created_at THEN 1 ELSE null end )" % self.interval,
          "old_fixed": "count( case when age(clock_timestamp(), reports.fixed_at) > interval '%s' AND reports.is_fixed = True THEN 1 ELSE null end )" % self.interval,
          "old_unfixed": "count( case when age(clock_timestamp(), reports.fixed_at) > interval '%s' AND reports.is_fixed = False THEN 1 ELSE null end )" % self.interval } )  


class SqlQuery(object):
    """
    This is a workaround: django doesn't support our optimized 
    direct SQL queries very well.
    """
        
    def __init__(self):
        self.cursor = None
        self.index = 0
        self.results = None    

    def next(self):
        self.index = self.index + 1
    
    def get_results(self):
        if not self.cursor:
            self.cursor = connection.cursor()
            self.cursor.execute(self.sql)
            self.results = self.cursor.fetchall()
        return( self.results )

class ReportCountQuery(SqlQuery):
      
    def name(self):
        return self.get_results()[self.index][5]

    def recent_new(self):
        return self.get_results()[self.index][0]
    
    def recent_fixed(self):
        return self.get_results()[self.index][1]
    
    def recent_updated(self):
        return self.get_results()[self.index][2]
    
    def old_fixed(self):
        return self.get_results()[self.index][3]
    
    def old_unfixed(self):
        return self.get_results()[self.index][4]
            
    def __init__(self, interval = '1 month'):
        SqlQuery.__init__(self)
        self.base_query = """select count( case when age(clock_timestamp(), reports.created_at) < interval '%s' THEN 1 ELSE null end ) as recent_new,\
 count( case when age(clock_timestamp(), reports.fixed_at) < interval '%s' AND reports.is_fixed = True THEN 1 ELSE null end ) as recent_fixed,\
 count( case when age(clock_timestamp(), reports.updated_at) < interval '%s' AND reports.is_fixed = False and reports.updated_at != reports.created_at THEN 1 ELSE null end ) as recent_updated,\
 count( case when age(clock_timestamp(), reports.fixed_at) > interval '%s' AND reports.is_fixed = True THEN 1 ELSE null end ) as old_fixed,\
 count( case when age(clock_timestamp(), reports.created_at) > interval '%s' AND reports.is_fixed = False THEN 1 ELSE null end ) as old_unfixed   
 """ % (interval,interval,interval,interval,interval) 
        self.sql = self.base_query + " from fixmystreet_report as reports" 

class CityTotals(ReportCountQuery):

    def __init__(self, interval, city):
        ReportCountQuery.__init__(self,interval)
        self.sql = self.base_query 
        self.sql += """ from fixmystreet_report as reports left join fixmystreet_ward as wards on reports.ward_id = wards.id left join fixmystreet_city as cities on cities.id = wards.city_id 
        """ 
        self.sql += ' where wards.city_id = %d ' % city.id
        
class CityWardsTotals(ReportCountQuery):

    def __init__(self, city):
        ReportCountQuery.__init__(self,"1 month")
        self.sql = self.base_query 
        self.url_prefix = "/wards/"            
        self.sql +=  ", wards.name, wards.id from fixmystreet_ward as wards "
        self.sql += """left join fixmystreet_report reports on wards.id = reports.ward_id join fixmystreet_city as cities on wards.city_id = cities.id join fixmystreet_province as province on cities.province_id = province.id
        """
        self.sql += "and cities.id = " + str(city.id)
        self.sql += " group by  wards.name, wards.id order by wards.name" 
    
    def id(self):
        return(self.get_results()[self.index][6])
        
    def get_absolute_url(self):
        return reverse('ward_show', args=[self.get_results()[self.index][6]])

class AllCityTotals(ReportCountQuery):

    def __init__(self):
        ReportCountQuery.__init__(self,"1 month")
        self.sql = self.base_query         
        self.url_prefix = "/cities/"            
        self.sql +=  ", cities.name, cities.id, province.name from cities "
        self.sql += """left join wards on wards.city_id = cities.id join province on cities.province_id = province.id left join reports on wards.id = reports.ward_id 
        """ 
        self.sql += "group by cities.name, cities.id, province.name order by province.name, cities.name"
           
    def get_absolute_url(self):
        return( self.url_prefix + str(self.get_results()[self.index][6]))
    
    def province(self):
        return(self.get_results()[self.index][7])
        
    def province_changed(self):
        if (self.index ==0 ):
            return( True )
        return( self.get_results()[self.index][7] != self.get_results()[self.index-1][7] )


def dictToPoint(data):
    if not data.has_key('x') or not data.has_key('y'):
        raise HttpResponseNotFound('<h1>Location not found</h1>')
    px = data.get('x')
    py = data.get('y')

    return fromstr("POINT(" + px + " " + py + ")", srid=31370)


class HtmlTemplateMail(EmailMultiAlternatives):
    def __init__(self, template_dir, data, recipients, **kargs):
        site = Site.objects.get_current()
        data['SITE_URL'] = 'http://{0}'.format(site.domain)
        subject, html, text = '', '', ''
        try:
            subject = render_to_string('emails/' + template_dir + "/subject.txt", data)
        except TemplateDoesNotExist:
            pass
        try:
            text    = render_to_string('emails/' + template_dir + "/message.txt", data)
        except TemplateDoesNotExist:
            pass
        try:
            html    = render_to_string('emails/' + template_dir + "/message.html", data)
        except TemplateDoesNotExist:
            pass
        
        subject = subject.rstrip(' \n\t').lstrip(' \n\t')
        super(HtmlTemplateMail, self).__init__(subject, text, settings.EMAIL_FROM_USER, recipients, **kargs)
        if html:
            self.attach_alternative(html, "text/html")



