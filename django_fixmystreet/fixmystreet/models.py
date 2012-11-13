from datetime import datetime as dt
from django.shortcuts import get_object_or_404
from django.db import connection
from django.db.models import Q
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.template.loader import render_to_string, TemplateDoesNotExist
from django.core.mail import EmailMultiAlternatives
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy, ugettext as _
from django.contrib.auth.models import User, UserManager, Group
from django.contrib.sites.models import Site
from django.contrib.gis.geos import fromstr
from django.contrib.gis.db import models
from django.http import Http404
from django.contrib.sessions.models import Session
from transmeta import TransMeta
from django_fixmystreet.fixmystreet.utils import FixStdImageField
from django.core import serializers
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings

class Category (models.Model):
	__metaclass__ = TransMeta
	
	code = models.CharField(max_length=50,null=False)
	label = models.CharField(max_length=100,null=False)
	type = models.IntegerField()
	
	class Meta:
		translate=('label',)


        
class Type (models.Model):
    __metaclass__ = TransMeta

    code= models.CharField(max_length=50,null=False)
    label = models.CharField(max_length=100,null=False)
    public = models.BooleanField(default=True)
    mainCategory = models.ForeignKey(Category,related_name='mainCategory')
    secondCategory = models.ForeignKey(Category,related_name='secondCategory')

    class Meta:
        translate=('label',)


class FMSUser(User):
    telephone= models.CharField(max_length=20,null=True)
    active = models.BooleanField(default=True)
    lastUsedLanguage = models.CharField(max_length=10,null=True)
    hashCode = models.IntegerField(null=True)

    agent = models.BooleanField(default=True)
    manager = models.BooleanField(default=True)
    leader = models.BooleanField(default=True)

    impetrant=models.BooleanField(default=False)
    contractor=models.BooleanField(default=False)
    
    categories = models.ManyToManyField('ReportCategory',related_name='type')

    organisation = models.ForeignKey('OrganisationEntity', related_name='team',null=True)


    objects = UserManager()


class OrganisationEntity(models.Model):
    __metaclass__= TransMeta
    name = models.CharField(verbose_name=_('Name'), max_length=100, null=False)

    commune = models.BooleanField(default=True)
    region = models.BooleanField(default=True)
    subcontractor = models.BooleanField(default=True)
    applicant = models.BooleanField(default=True)
    dependency = models.ForeignKey('OrganisationEntity',related_name='parent', null=True)

    class Meta:
        translate = ('name', )


class Status(models.Model):
    __metaclass__=TransMeta
    name=models.CharField(verbose_name=_('Name'),max_length=100,null=False)
    code=models.CharField(max_length=50,null=False)
    parentStatus = models.ForeignKey('self',null=True)
    
    class Meta:
        translate = ('name', )

        
class Report(models.Model):
    status = models.ForeignKey(Status,null=False)
    point = models.PointField(null=True, srid=31370)
    address = models.CharField(max_length=255, verbose_name=ugettext_lazy("Location"))
    category = models.ForeignKey('ReportMainCategoryClass', null=True, verbose_name=ugettext_lazy("Category"))
    #main_category = models.ForeignKey('ReportMainCategoryClass', null=True, verbose_name=ugettext_lazy("Category"))
    secondary_category = models.ForeignKey('ReportCategory', null=True, verbose_name=ugettext_lazy("Category"))
    created_at = models.DateTimeField(auto_now_add=True)
    # last time report was updated
    updated_at = models.DateTimeField(null=True)
    is_hate = models.BooleanField(default=False)
    is_fixed = models.BooleanField(default=False)
    # time report was marked as 'fixed'
    fixed_at = models.DateTimeField(null=True, blank=True)
    commune = models.ForeignKey('Commune', null=True)
    hashCode = models.IntegerField(null=True)
    creator = models.ForeignKey(User,null=True, related_name='creator')
    
    citizen = models.ForeignKey(User,null=True, related_name='citizen')
    description = models.TextField(null=True)
    #responsible = models.ForeignKey(OrganisationEntity, related_name='in_charge_reports', null=False)
    subcontractor = models.ForeignKey(OrganisationEntity, related_name='assigned_reports', null=True)
    responsible_manager = models.ForeignKey(FMSUser, related_name='in_charge_reports', null=True)
    responsible_manager_validated = models.BooleanField(default=False)
#    report_type = models.ForeignKey(Type)
    valid = models.BooleanField(default=False)
    private = models.BooleanField(default=True)
    finished = models.BooleanField(default=False)
    photo = FixStdImageField(upload_to="photos", blank=True, size=(380, 380), thumbnail_size=(66, 50))
    close_date = models.DateTimeField(null=True, blank=True)

    objects = models.GeoManager()
    def get_absolute_url(self):
    #TODO determine when pro and no-pro url must be returned
        return reverse("report_show", args=[self.id])
    
    def get_absolute_url_pro(self):
    #TODO determine when pro and no-pro url must be returned
        return reverse("report_show_pro", args=[self.id])


class Exportable(models.Model):
    def asJSON():
        return
    def asXML():
        return

class Abonment(models.Model):
    report = models.ForeignKey(Report)

class Address(models.Model):
    __metaclass__= TransMeta
    
    street = models.CharField(max_length=100)
    city = models.CharField(max_length= 100)
    zipCode = models.IntegerField()
    streetNumber = models.CharField(max_length=100)
    geoX = models.FloatField()
    geoY = models.FloatField()
    
    class Meta:
        translate=('street','city',)

class AttachmentType(models.Model):
    code = models.CharField(max_length=50)
    url = models.CharField(max_length=50)
        

    

class Attachment(models.Model):
    report = models.ForeignKey(Report)
    validated=models.BooleanField(default=False)
    isVisible=models.BooleanField(default=False)
    title=models.CharField(max_length=250)
    
    class Meta:
        abstract=True


class Comment (Attachment):
    text = models.TextField()


class File(Attachment):
    file = models.FileField(upload_to="files")
    fileType= models.ForeignKey(AttachmentType)


class UserType(models.Model):
    __metaclass__= TransMeta

    code=models.CharField(max_length=50)
    name=models.CharField(max_length=100)
    creation_date = models.DateTimeField(auto_now_add=True, blank=True,default=dt.now())
    update_date = models.DateTimeField(auto_now=True, blank=True,default=dt.now())
    
    class Meta:
        translate = ('name', )

@receiver(pre_save,sender=Report)
def report_assign_responsible(sender, instance, **kwargs):
    """signal on a report to notify public authority that a report has been filled"""
    #Detect who is the responsible Manager for the given type
    fmsUser = FMSUser.objects.get(pk=instance.creator.id)
    userCandidates = FMSUser.objects.filter(organisation__id=fmsUser.organisation.id).filter(manager=True)
    for currentUser in userCandidates:
        userCategories = currentUser.categories.all()
        for currentCategory in userCategories:
            if (currentCategory == instance.secondary_category):
        	#import pdb
        	#pdb.set_trace()
                instance.responsible_manager = fmsUser
                #instance.save()

#signal on a report to notify public authority that a report has been filled
@receiver(post_save,sender=Report)
def report_notify(sender, instance, **kwargs):
    if kwargs['created'] and not kwargs['raw']:
        NotificationResolver(instance).resolve()

#signal on a report to register author as subscriber to his own report
#@receiver(post_save,sender=Report)
#def report_subscribe_author(sender, instance, **kwargs):
#    if kwargs['created']:
#        ReportSubscription(report=instance, subscriber=instance.author).save()

class ReportUpdate(models.Model):
    """A new version of the status of a report"""
    report = models.ForeignKey(Report)
    desc = models.TextField(blank=True, null=True, verbose_name=ugettext_lazy("Details"))
    created_at = models.DateTimeField(auto_now_add=True)
    is_fixed = models.BooleanField(default=False)
    author = models.ForeignKey(User,null=True)
    photo = FixStdImageField(upload_to="photos", blank=True, size=(380, 380), thumbnail_size=(66, 50)) 
    
    class Meta:
        ordering = ['created_at']
        #order_with_respect_to = 'report'

#update the report, set updated_at and is_fixed correctly
@receiver(post_save, sender=ReportUpdate)
def update_report(sender, instance, **kwargs):
    instance.report.updated_at = instance.created_at

    instance.report.is_fixed = instance.is_fixed
    if(instance.is_fixed and not instance.report.fixed_at):
        instance.report.fixed_at = instance.created_at

    instance.report.save()

#notify subscribers that report has been updated
@receiver(post_save, sender=ReportUpdate)
def notify(sender, instance, **kwargs):
    if not kwargs['raw']:
        for subscribe in instance.report.reportsubscription_set.exclude(Q(subscriber__email__isnull=True) | Q(subscriber__email__exact='')):
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


class ReportMainCategoryClass(models.Model):
    __metaclass__ = TransMeta
    help_text = """
    Manage the category container list (see the report form). Allow to group categories.
    """

    name = models.CharField(max_length=100)
    creation_date = models.DateTimeField(auto_now_add=True, blank=True,default=dt.now())
    update_date = models.DateTimeField(auto_now=True, blank=True,default=dt.now())
    def __unicode__(self):      
        return self.name

    class Meta:
        verbose_name = "category group"
        verbose_name_plural = "category groups"
        translate = ('name', )


class ReportSecondaryCategoryClass(models.Model):
    __metaclass__ = TransMeta
    help_text = """
    Manage the category container list (see the report form). Allow to group categories.
    """

    name = models.CharField(max_length=100)
    creation_date = models.DateTimeField(auto_now_add=True, blank=True,default=dt.now())
    update_date = models.DateTimeField(auto_now=True, blank=True,default=dt.now())
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
    #code     = models.CharField(max_length=32)
    #label_en = models.TextField(blank=True, null=True)
    #label_fr = models.TextField(blank=True, null=True)
    #label_nl = models.TextField(blank=True, null=True)
    #type     = models.CharField(max_length=32)
    creation_date = models.DateTimeField(auto_now_add=True, blank=True,default=dt.now())
    update_date = models.DateTimeField(auto_now=True, blank=True,default=dt.now())
    category_class = models.ForeignKey(ReportMainCategoryClass, verbose_name=_('Category group'), help_text="The category group container")
    secondary_category_class = models.ForeignKey(ReportSecondaryCategoryClass, verbose_name=_('Category group'), help_text="The category group container")
    public = models.BooleanField(default=True)
    def __unicode__(self):      
        return self.category_class.name + ":" + self.name
 
    class Meta:
        verbose_name = "category"
        verbose_name_plural = "categories"
        translate = ('name', 'hint', )



class GestType(models.Model):
    help_text="""
    Defines the relation of a user and a category
    """
    creation_date = models.DateTimeField(auto_now_add=True, blank=True,default=dt.now())
    update_date = models.DateTimeField(auto_now=True, blank=True,default=dt.now())
    category = models.ForeignKey(ReportCategory)
    user = models.ForeignKey(FMSUser)


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
    commune = models.ForeignKey(
        'Commune',
        null=False,
        help_text="The commune where the rule apply."
    )
    # filled in if this is a category class rule
    category_class = models.ForeignKey(
        ReportMainCategoryClass,null=True, blank=True,
        verbose_name='Category Group',
        help_text="Only set for 'Category Group' rule types."
    )
    # filled in if an additional email address is required for the rule type
    councillor = models.ForeignKey(FMSUser, null=False)

    def __str__(self):
        return "%s - %s %s (%s)" % ( 
                self.councillor.name,
                (self.category_class and self.category_class.name or ''),
                self.RuleChoices[self.rule][1],
                self.commune.name
        )


class ReportNotification(models.Model):
    report = models.ForeignKey(Report)
    to_manager = models.ForeignKey(FMSUser)
    sent_at = models.DateTimeField()
    success = models.BooleanField()
    message = models.TextField()

    def send(self):
        msg = HtmlTemplateMail('send_report_to_city', {'report': self.report}, (self.to_councillor.email,))
        if self.report.photo:
            msg.attach_file(self.report.photo.file.name)
        msg.send()
        self.sent_at = dt.now()


class NotificationResolver(object):
    def __init__(self, report):
        self.report = report
        self.rules = NotificationRule.objects.filter(commune=self.report.commune)

    def send(self, councillor):
        notification = ReportNotification(report=self.report, to_councillor=councillor)
        notification.send()
        notification.save()

    def resolve(self):
        if self.report.commune.default_manager:
            self.send(self.report.commune.default_manager)
        for rule in self.rules:
            if rule.rule == NotificationRule.TO_COUNCILLOR:
                self.send(rule.councillor)

            if rule.rule == NotificationRule.MATCHING_CATEGORY_CLASS:
                if self.report.category.category_class == rule.category_class:
                    self.send(rule.councillor)

            if rule.rule == NotificationRule.NOT_MATCHING_CATEGORY_CLASS:
                if self.report.category.category_class != rule.category_class:
                    self.send(rule.councillor)


class Commune(models.Model):
    __metaclass__ = TransMeta
    
    name = models.CharField(max_length=100)
    creation_date = models.DateTimeField(auto_now_add=True, blank=True,default=dt.now())
    update_date = models.DateTimeField(auto_now=True, blank=True,default=dt.now())
    feature_id = models.CharField(max_length=25)
    default_manager = models.ForeignKey(FMSUser, null=True)

    class Meta:
        translate = ('name', )


class Zone(models.Model):
    __metaclass__ = TransMeta
    
    name=models.CharField(max_length=100)
    creation_date = models.DateTimeField(auto_now_add=True, blank=True,default=dt.now())
    update_date = models.DateTimeField(auto_now=True, blank=True,default=dt.now())
    commune = models.ForeignKey(Commune)
    
    class Meta:
        translate = ('name', )




class FMSUserZone(models.Model):
    user = models.ForeignKey(FMSUser)
    zone = models.ForeignKey(Zone)
    creation_date = models.DateTimeField(auto_now_add=True, blank=True,default=dt.now())
    update_date = models.DateTimeField(auto_now=True, blank=True,default=dt.now())


class ZipCode(models.Model):
    __metaclass__ = TransMeta
    
    commune = models.ForeignKey(Commune)
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
        self.swap_order(other[0], faq_entry)
    
    def decr_order(self, faq_entry): 
        other = FaqEntry.objects.filter(order=faq_entry.order+1)
        if len(other) == 0:
            return
        self.swap_order(other[0], faq_entry)
        
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

class UsersAssignedToCategories(SqlQuery):
    def __init__(self,mainCategoryId,secondaryCategoryId,organisationId):
        SqlQuery.__init__(self)
        self.base_query = """ select FilterU.first_name, FilterU.last_name from(\
        select auth_user.first_name, auth_user.last_name, auth_user.id from(\
                select distinct fixmystreet_fmsuser_categories.fmsuser_id from(\
                        select id from fixmystreet_reportcategory where fixmystreet_reportcategory.category_class_id=%d and fixmystreet_reportcategory.secondary_category_class_id=%d) as RCat \
                join fixmystreet_fmsuser_categories on fixmystreet_fmsuser_categories.reportcategory_id = RCat.id ) as UserCat \
        join auth_user\
        on auth_user.id = UserCat.fmsuser_id \
    ) as FilterU \
join\
    (\
        select fixmystreet_fmsuser.user_ptr_id \
        from fixmystreet_fmsuser \
        where fixmystreet_fmsuser.organisation_id = %d \
    ) as FMSU \
on FMSU.user_ptr_id = FilterU.id """ % (mainCategoryId,secondaryCategoryId,organisationId)
        self.sql = self.base_query

class UserTypeForOrganisation(SqlQuery):
    def __init__(self,typeId,organisationId):
        SqlQuery.__init__(self)
        self.base_query="""select Cat.fmsuser_id,Cat.reportcategory_id \
from (select fmsuser_id,reportcategory_id from fixmystreet_fmsuser_categories where reportcategory_id=%d) as Cat \
join (select user_ptr_id from fixmystreet_fmsuser where fixmystreet_fmsuser.organisation_id=%d) as U \
on U.user_ptr_id = Cat.fmsuser_id """ % (typeId,organisationId) 
        self.sql=self.base_query


class TypesWithUsersOfOrganisation(SqlQuery):
    def __init__(self,organisationId):
        SqlQuery.__init__(self)
        self.base_query=""" select A.reportcategory_id, A.fmsuser_id \
from (select * from fixmystreet_fmsuser_categories) as A \
join (select user_ptr_id from fixmystreet_fmsuser where organisation_id=%d) as B \
on B.user_ptr_id = A.fmsuser_id""" % (organisationId)
        self.sql=self.base_query

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

        #5 years for pro, 1 month for citizens
        #if isUserAuthenticated() == True:
        #      interval = '60 month'
        #
        #interval = '1 day'

        self.base_query = """select count( case when age(clock_timestamp(), reports.created_at) < interval '%s' THEN 1 ELSE null end ) as recent_new,\
 count( case when age(clock_timestamp(), reports.fixed_at) < interval '%s' AND reports.is_fixed = True THEN 1 ELSE null end ) as recent_fixed,\
 count( case when age(clock_timestamp(), reports.updated_at) < interval '%s' AND reports.is_fixed = False and reports.updated_at != reports.created_at THEN 1 ELSE null end ) as recent_updated,\
 count( case when age(clock_timestamp(), reports.fixed_at) > interval '%s' AND reports.is_fixed = True THEN 1 ELSE null end ) as old_fixed,\
 count( case when age(clock_timestamp(), reports.created_at) > interval '%s' AND reports.is_fixed = False THEN 1 ELSE null end ) as old_unfixed   
 """ % (interval, interval, interval, interval, interval) 
        self.sql = self.base_query + " from fixmystreet_report as reports" 

class CityTotals(ReportCountQuery):

    def __init__(self, interval, city):
        ReportCountQuery.__init__(self, interval)
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
        raise Http404('<h1>Location not found</h1>')
    px = data.get('x')
    py = data.get('y')

    return fromstr("POINT(" + px + " " + py + ")", srid=31370)


def getLoggedInUserId(sessionKey):
    session = Session.objects.get(session_key=sessionKey)
    uid = session.get_decoded().get('_auth_user_id')
    if not uid:
        uid=1
    return uid

def getUserAuthenticated(sessionKey):
    session = Session.objects.get(session_key=sessionKey)
    uid = session.get_decoded().get('_auth_user_id')
    user = User.objects.get(pk=uid)
    return user.is_authenticated() == True


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

def exportUsers():
    XMLSerializer = serializers.get_serializer("xml")
    xml_serializer = XMLSerializer()
    with open("backup/pro/users.xml", "w") as out:
        xml_serializer.serialize(FMSUser.objects.all(), stream=out)

def exportReportsOfEntity(entityId):
    # TODO loop over all reports to get files and comments (Structure result data in correct manner)
    #define xml object serializer
    XMLSerializer = serializers.get_serializer("xml")
    xml_serializer = XMLSerializer()
    #Get reports
    data1 = Report.objects.filter(commune=entityId)
    #Starting tag
    d="<Reports>"
    #For each found report
    for report in data1:
        d = d+ "<Report>"
        #Get the info of the report
        d1= xml_serializer.serialize(Report.objects.filter(id=report.id),fields=('id','category', 'description', 'created_at', 'updated_at', 'status'))
        #Get comments of the report
        data2 = Comment.objects.filter(report_id=data1[0].id)
        d2 = xml_serializer.serialize(data2,fields=('title','text'))
        #Get files of the report
        data3 = File.objects.filter(report_id=data1[0].id)
        d3 = xml_serializer.serialize(data3,fields=('title','file'))
        #Concat serialized data
        d = d+ d1+"<Comments>"+d2+"</Comments><Files>"+d3+"</Files>"
        d = d + "</Report>"
    #Add closing tag
    d = d+"</Reports>"
    #open/create file to save data to
    f =  open("backup/pro/reportsOfEntity.xml","w")
    #write data to file
    f.write(d)
    #close file stream
    f.close()
