
from django.db import models, connection
from django.contrib.gis.db import models
from django.contrib.gis.maps.google import GoogleMap, GMarker, GEvent, GPolygon, GIcon
from django.template.loader import render_to_string, TemplateDoesNotExist
import settings
from django import forms
from django.core.mail import send_mail, EmailMessage, EmailMultiAlternatives
import md5
import urllib
import time
from mainapp import emailrules
from datetime import datetime as dt
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy, ugettext as _
from transmeta import TransMeta
from stdimage import StdImageField
from django.utils.encoding import iri_to_uri
from django.contrib.gis.geos import fromstr
from django.http import Http404
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.contrib.sites.models import Site
      

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

    name = models.CharField(verbose_name=_('Name'),max_length=100)
    hint = models.TextField(verbose_name=_('Hint'),blank=True, null=True)
    category_class = models.ForeignKey(ReportCategoryClass,verbose_name=_('Category group'), help_text="The category group container")
    def __unicode__(self):      
        return self.category_class.name + ":" + self.name
 
    class Meta:
        verbose_name = "category"
        verbose_name_plural = "categories"
        translate = ('name', 'hint', )

#class ReportCategorySet(models.Model):
    #''' A category group for a particular city '''
    #name = models.CharField(max_length=100)
    #categories = models.ManyToManyField(ReportCategory)

    #def __unicode__(self):      
        #return self.name
                 
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
        return "/cities/" + str(self.id)

    def get_rule_descriptions(self):
        rules = EmailRule.objects.filter(city=self)
        describer = emailrules.EmailRulesDesciber(rules,self)
        return( describer.values() )

    class Meta:
        verbose_name_plural = "cities"

class Councillor(models.Model):
    help_text = """
    Represent a public authority that can resolve a problem from a fix my street report. 
    When a report if filled in the website, a notification mail will be sent to the corresponding 
    councillors that is able to resolve it.
    """
    
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    
    # this email addr. is the destination for reports
    # if the 'Councillor' email rule is enabled
    email = models.EmailField(blank=True, null=True)
    # city = models.ForeignKey(City,null=True)

    def __unicode__(self):      
        return self.first_name + " " + self.last_name

        
class Ward(models.Model):
    name = models.CharField(max_length=100)
    number = models.IntegerField()
    councillor = models.ForeignKey(Councillor,null=True,blank=True)
    city = models.ForeignKey(City)
    # geom = models.MultiPolygonField( null=True)
    objects = models.GeoManager()

    # this email addr. is the destination for reports
    # if the 'Ward' email rule is enabled
    # email = models.EmailField(blank=True, null=True)

    def get_absolute_url(self):
        return "/wards/" + str(self.id)

    def __unicode__(self):      
        return self.city.name + " " + self.name

    def get_rule_descriptions(self):
        rules = EmailRule.objects.filter(city=self.city)
        describer = emailrules.EmailRulesDesciber(rules,self.city, self)
        return( describer.values() )

class ZipCode(models.Model):
    __metaclass__ = TransMeta
    
    ward = models.ForeignKey(Ward)
    code = models.CharField(max_length=4)
    name = models.CharField(max_length=100)
    hide = models.BooleanField()

    class Meta:
        translate = ('name', )

# Override where to send a report for a given city.        
#
# If no rule exists, the email destination is the 311 email address 
# for that city.
#
# Cities can have more than one rule.  If a given report matches more than
# one rule, more than one email is sent.  (Desired behaviour for cities that 
# want councillors CC'd)

class EmailRule(models.Model):
    help_text = """
    Declare that an extra Councillors has authority for resolving a problem and need to recieve notifiaction.
    """
    TO_COUNCILLOR = 0
    MATCHING_CATEGORY_CLASS = 1
    NOT_MATCHING_CATEGORY_CLASS = 2
    #TO_WARD = 3
    
    RuleChoices = [   
        (TO_COUNCILLOR, 'All the time'),
        (MATCHING_CATEGORY_CLASS, 'Category group is selected'),
        (NOT_MATCHING_CATEGORY_CLASS, 'Category group is not selected'), 
        #(TO_WARD, 'Send Reports to Ward Email Address'),
    ]
    
    RuleBehavior = { 
        TO_COUNCILLOR: emailrules.ToCouncillor,
        MATCHING_CATEGORY_CLASS: emailrules.MatchingCategoryClass,
        NOT_MATCHING_CATEGORY_CLASS: emailrules.NotMatchingCategoryClass,
        #TO_WARD: emailrules.ToWard 
    }
    
    rule = models.IntegerField(
        choices=RuleChoices,
        verbose_name='Send a notification when',
        help_text="Depending to the report's category and this selected category."
    )

    # the city this rule applies to 
    ward = models.ForeignKey(
        Ward,
        help_text="The ward where the rule apply."
    )
    
    # filled in if this is a category class rule
    category_class = models.ForeignKey(
        ReportCategoryClass,null=True, blank=True,
        verbose_name='Category Group',
        help_text="Only set for 'Category Group' rule types."
    )
    
       
    # filled in if an additional email address is required for the rule type
    councillor = models.ForeignKey(Councillor)

    # is this a 'to' email or a 'cc' email
    is_cc = models.BooleanField(default=False,
        help_text="Send notifications in copy"
    )


    def label(self):
        rule_behavior = EmailRule.RuleBehavior[ self.rule ]()
        return( rule_behavior.report_group(self) )
    
    def value(self, ward = None):
        rule_behavior = EmailRule.RuleBehavior[ self.rule ]()
        if ward:
            return( rule_behavior.value_for_ward(self,ward) )
        else:
            return( rule_behavior.value_for_city(self))
        
    def resolve_email(self,report):
        rule_behavior = EmailRule.RuleBehavior[ self.rule ](self, report)
        rule_behavior.resolve_email()
    
    def __str__(self):
        return( "%s: %s %s - %s %s (%s)" % ("CC" if self.is_cc else "TO", self.councillor.first_name, self.councillor.last_name, (self.category_class.name if self.category_class else ''), self.RuleChoices[self.rule][1], self.ward.name) )
        

class Report(models.Model):
    title = models.CharField(max_length=100, verbose_name = ugettext_lazy("Subject"))
    category = models.ForeignKey(ReportCategory,null=True)
    ward = models.ForeignKey(Ward,null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    # last time report was updated
    updated_at = models.DateTimeField(auto_now_add=True)
    
    # time report was marked as 'fixed'
    fixed_at = models.DateTimeField(null=True,blank=True)
    is_fixed = models.BooleanField(default=False)
    is_hate = models.BooleanField(default=False)
    
    # last time report was sent to city
    sent_at = models.DateTimeField(null=True)
    
    # email where the report was sent
    email_sent_to = models.EmailField(null=True)
    
    # last time a reminder was sent to the person that filed the report.
    reminded_at = models.DateTimeField(auto_now_add=True)
    
    point = models.PointField(null=True, srid=31370)

    photo = StdImageField(upload_to="photos", blank=True, verbose_name = ugettext_lazy("* Photo"), size=(380, 380), thumbnail_size=(66,50))
    desc = models.TextField(blank=True, null=True, verbose_name = ugettext_lazy("Details"))
    author = models.CharField(max_length=255,verbose_name = ugettext_lazy("Name"))
    address = models.CharField(max_length=255,verbose_name = ugettext_lazy("Location"))
    postalcode = models.CharField(max_length=4,verbose_name = ugettext_lazy("Postal Code"))

    # true if first update has been confirmed - redundant with
    # one in ReportUpdate, but makes aggregate SQL queries easier.
    
    is_confirmed = models.BooleanField(default=False)

    objects = models.GeoManager()
    
    def is_subscribed(self, email):
        if len( self.reportsubscriber_set.filter(email=email)) != 0:
            return( True )
        return( self.first_update().email == email )
    
    def sent_at_diff(self):
        if not self.sent_at:
            return( None )
        else:
            return(  self.sent_at - self.created_at )

    def first_update(self):
        return( ReportUpdate.objects.get(report=self,first_update=True))

    def get_absolute_url(self):
        return 'http://%s%s' % (Site.objects.get_current().domain, reverse("report_show", args=[self.id]))

    def get_mobile_absolute_url(self):
        return reverse("mobile_report_show", args=[self.id])

    def thumbnail_photo(self):
        return self.photo.url.replace(".jpeg", ".thumbnail.jpeg")

    # return a list of email addresses to send new problems in this ward to.
    def get_emails(self):
        self.to_emails = []
        self.cc_emails = []
        self.excluded = []
        if self.ward.councillor:
            self.to_emails.append(self.ward.councillor.email)
        
        # check for rules for this city.
        rules = EmailRule.objects.filter(ward=self.ward)
        for rule in rules:
            rule.resolve_email(self)
        
        #print self.to_emails
        #print self.cc_emails
        return( self.to_emails,self.cc_emails )

    def flagAsOffensive(self):
        report_url= self.get_absolute_url(), 

        msg = HtmlTemplateMail('flag_report', { 'report_url': report_url, 'report': self }, [settings.EMAIL_ADMIN])
        msg.send()
        


class ReportCount(object):        
    def __init__(self, interval):
        self.interval = interval
    
    def dict(self):
        return({ "recent_new": "count( case when age(clock_timestamp(), reports.created_at) < interval '%s' THEN 1 ELSE null end )" % self.interval,
          "recent_fixed": "count( case when age(clock_timestamp(), reports.fixed_at) < interval '%s' AND reports.is_fixed = True THEN 1 ELSE null end )" % self.interval,
          "recent_updated": "count( case when age(clock_timestamp(), reports.updated_at) < interval '%s' AND reports.is_fixed = False and reports.updated_at != reports.created_at THEN 1 ELSE null end )" % self.interval,
          "old_fixed": "count( case when age(clock_timestamp(), reports.fixed_at) > interval '%s' AND reports.is_fixed = True THEN 1 ELSE null end )" % self.interval,
          "old_unfixed": "count( case when age(clock_timestamp(), reports.fixed_at) > interval '%s' AND reports.is_fixed = False THEN 1 ELSE null end )" % self.interval } )  
 
class ReportUpdate(models.Model):   
    report = models.ForeignKey(Report)
    desc = models.TextField(blank=True, null=True, verbose_name = ugettext_lazy("Details"))
    created_at = models.DateTimeField(auto_now_add=True)
    is_confirmed = models.BooleanField(default=False)
    is_fixed = models.BooleanField(default=False)
    confirm_token = models.CharField(max_length=255, null=True)
    email = models.EmailField(max_length=255, verbose_name = ugettext_lazy("Email"))
    author = models.CharField(max_length=255,verbose_name = ugettext_lazy("Name"))
    phone = models.CharField(max_length=255, verbose_name = ugettext_lazy("Phone"), blank=True,null=True )
    first_update = models.BooleanField(default=False)
    
    def notify(self):
        """
        Tell whoever cares that there's been an update to this report.
         -  If it's the first update, tell city officials
         -  Anything after that, tell subscribers
        """
        if self.first_update:
            self.notify_on_new()
        else:
            self.notify_on_update()
            
    def notify_on_new(self):        
        to_addrs,cc_addrs = self.report.get_emails()

        msg = HtmlTemplateMail('send_report_to_city', {'update': self }, to_addrs, cc=cc_addrs)
        if self.report.photo:
            msg.attach_file( self.report.photo.file.name )
        msg.send()

        email_addr_str = ','.join(to_addrs)
        #for email in to_addrs:
            #if email_addr_str != "":
                #email_addr_str += ", "
            #email_addr_str += email
		
        # update report to show time sent to city.
        self.report.sent_at=dt.now()
        self.report.email_sent_to = email_addr_str
        self.report.save()

    def notify_on_update(self):
        subject = render_to_string("emails/report_update/subject.txt", 
                    { 'update': self })

        # tell our subscribers there was an update.
        for subscriber in self.report.reportsubscriber_set.all():
            if subscriber.is_confirmed:
                unsubscribe_url = 'http://%s%s' % (Site.objects.get_current().domain, reverse("unsubscribe",args=[subscriber.confirm_token]))
                msg = HtmlTemplateMail('report_update', {'update': self, 'unsubscribe_url': unsubscribe_url}, [subscriber.email])
                msg.send()

        # tell the original problem reporter there was an update
        msg = HtmlTemplateMail('report_update', {'update': self}, [self.report.first_update().email])
        msg.send()

            
    def save(self):
        # does this update require confirmation?
        if not self.is_confirmed:
            self.request_confirmation()
        else:
            self.notify()
        super(ReportUpdate,self).save()
            
            
    def request_confirmation(self):
        """ Send a confirmation email to the user. """        
        if not self.confirm_token or self.confirm_token == "":
            m = md5.new()
            m.update(self.email)
            m.update(str(time.time()))
            self.confirm_token = m.hexdigest()
            
            confirm_url = 'http://%s%s' % (Site.objects.get_current().domain, reverse('confirm', args=[self.confirm_token]))
            tmpl_dir = 'confirm_report' if self.first_update else 'confirm_update'
            msg = HtmlTemplateMail(tmpl_dir,{'confirm_url': confirm_url, 'update': self},[self.email])
            msg.send()

    def title(self):
        if self.first_update :
            return self.report.title
        if self.is_fixed:
            return "Reported Fixed"
        return("Update")

class ReportSubscriber(models.Model):
    """ 
    Report Subscribers are notified when there's an update to an existing report.
    """
    report = models.ForeignKey(Report)    
    confirm_token = models.CharField(max_length=255, null=True)
    is_confirmed = models.BooleanField(default=False)    
    email = models.EmailField()

    def save(self):
        if not self.is_confirmed:
            self.request_confirmation()
        super(ReportSubscriber, self).save()

    def request_confirmation(self):
        """ Send a confirmation email to the user. """
        if not self.confirm_token or self.confirm_token == "":
            m = md5.new()
            m.update(self.email)
            m.update(str(time.time()))
            self.confirm_token = m.hexdigest()

            confirm_url = 'http://%s%s' % (Site.objects.get_current().domain, reverse('subscribe_confirm', args=[self.confirm_token]))
            #message = render_to_string("emails/subscribe/message.txt",
                    #{ 'confirm_url': confirm_url, 'subscriber': self })
            #send_mail('Subscribe to Fix My Street Report Updates', message,
                   #settings.EMAIL_FROM_USER,[self.email], fail_silently=False)
            
            msg = HtmlTemplateMail('subscribe',{ 'confirm_url': confirm_url, 'subscriber': self },[self.email])
            msg.send()


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
        self.base_query = """select count( case when age(clock_timestamp(), reports.created_at) < interval '%s' and reports.is_confirmed THEN 1 ELSE null end ) as recent_new,\
 count( case when age(clock_timestamp(), reports.fixed_at) < interval '%s' AND reports.is_fixed = True THEN 1 ELSE null end ) as recent_fixed,\
 count( case when age(clock_timestamp(), reports.updated_at) < interval '%s' AND reports.is_fixed = False and reports.updated_at != reports.created_at THEN 1 ELSE null end ) as recent_updated,\
 count( case when age(clock_timestamp(), reports.fixed_at) > interval '%s' AND reports.is_fixed = True THEN 1 ELSE null end ) as old_fixed,\
 count( case when age(clock_timestamp(), reports.created_at) > interval '%s' AND reports.is_confirmed AND reports.is_fixed = False THEN 1 ELSE null end ) as old_unfixed   
 """ % (interval,interval,interval,interval,interval) 
        self.sql = self.base_query + " from mainapp_report as reports where reports.is_confirmed = true" 

class CityTotals(ReportCountQuery):

    def __init__(self, interval, city):
        ReportCountQuery.__init__(self,interval)
        self.sql = self.base_query 
        self.sql += """ from mainapp_report as reports left join mainapp_ward as wards on reports.ward_id = wards.id left join mainapp_city as cities on cities.id = wards.city_id 
        """ 
        self.sql += ' where reports.is_confirmed = True and wards.city_id = %d ' % city.id
        
class CityWardsTotals(ReportCountQuery):

    def __init__(self, city):
        ReportCountQuery.__init__(self,"1 month")
        self.sql = self.base_query 
        self.url_prefix = "/wards/"            
        self.sql +=  ", wards.name, wards.id, wards.number from mainapp_ward as wards "
        self.sql += """left join mainapp_report reports on wards.id = reports.ward_id join mainapp_city as cities on wards.city_id = cities.id join mainapp_province as province on cities.province_id = province.id
        """
        self.sql += "and cities.id = " + str(city.id)
        self.sql += " group by  wards.name, wards.id, wards.number order by wards.number" 
    
    def number(self):
        return(self.get_results()[self.index][7])

    def id(self):
        return(self.get_results()[self.index][6])
        
    def get_absolute_url(self):
        return( self.url_prefix + str(self.get_results()[self.index][6]))

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

class FaqEntry(models.Model):
    __metaclass__ = TransMeta

    q = models.CharField(_('Question'),max_length=100)
    a = models.TextField(_('Answere'),blank=True, null=True)
    slug = models.SlugField(null=True, blank=True)
    order = models.IntegerField(null=True, blank=True)
    
    def save(self):
        super(FaqEntry, self).save()
        if self.order == None: 
            self.order = self.id + 1
            super(FaqEntry, self).save()
    
    class Meta:
        verbose_name_plural = 'faq entries'
        translate = ('q', 'a', )
       

class FaqMgr(object):
        
    def incr_order(self, faq_entry ):
        if faq_entry.order == 1:
            return
        other = FaqEntry.objects.get(order=faq_entry.order-1)
        swap_order(other[0],faq_entry)
    
    def decr_order(self, faq_entry): 
        other = FaqEntry.objects.filter(order=faq_entry.order+1)
        if len(other) == 0:
            return
        swap_order(other[0],faq_entry)
        
    def swap_order(self, entry1, entry2 ):
        entry1.order = entry2.order
        entry2.order = entry1.order
        entry1.save()
        entry2.save()
 

class PollingStation(models.Model):
    """
    This is a temporary object.  Sometimes, we get maps in the form of
    polling stations, which have to be combined into wards.
    """
    number = models.IntegerField()
    station_name = models.CharField(max_length=100, null=True)
    ward_number = models.IntegerField()
    city = models.ForeignKey(City)
    geom = models.MultiPolygonField( null=True)
    objects = models.GeoManager()

    #class Meta:
        #db_table = u'polling_stations'
 
 
#class UserProfile(models.Model):
    #user = models.ForeignKey(User, unique=True)
    #
     #if user is a 'city admin' (is_staff=True),
     #this field lists all cities the user 
     #can edit through the admin 
     #panel.  
    #
    #cities = models.ManyToManyField(City, null=True)
    #
    #def __unicode__(self):
        #return self.user.username
    
    
class DictToPoint():
    
    def __init__(self, dict, exceptclass = Http404 ):
        if exceptclass and not dict.has_key('lat') or not dict.has_key('lon'):
            raise exceptclass
        
        self.lat = dict.get('lat',None)
        self.lon = dict.get('lon',None)
        self._pnt = None
        self.srid = 31370
        
    def __unicode__(self):
        return ("POINT(" + self.lon + " " + self.lat + ")" )
    
    def pnt(self, srid = None ):
        if srid:
            self.srid = srid
        if self._pnt:
            return self._pnt
        if not self.lat or not self.lon:
            return None
        pntstr = self.__unicode__()
        self._pnt = fromstr(pntstr, srid=self.srid)#, srid = self.srid) 
        return self._pnt
    
    def ward(self):
        pnt = self.pnt()
        if not pnt:
            return None
        wards = Ward.objects.filter(geom__contains=pnt)[:1]
        if wards:
            return(wards[0])
        else:
            return(None)

class HtmlTemplateMail(EmailMultiAlternatives):
    def __init__(self, template_dir, data, recipients, **kargs):
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


