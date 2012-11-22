from datetime import datetime as dt

from django.shortcuts import get_object_or_404
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
from django.core import serializers
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings

from transmeta import TransMeta
from django_fixmystreet.fixmystreet.utils import FixStdImageField


class FMSUser(User):
    telephone = models.CharField(max_length=20,null=True)
    #active = models.BooleanField(default=True)
    last_used_language = models.CharField(max_length=10,null=True)
    #hash_code = models.IntegerField(null=True)# used by external app for secure sync, must be random generated

    agent = models.BooleanField(default=True)
    manager = models.BooleanField(default=True)
    leader = models.BooleanField(default=True)

    impetrant = models.BooleanField(default=False)
    contractor = models.BooleanField(default=False)
    
    categories = models.ManyToManyField('ReportCategory',related_name='type')

    organisation = models.ForeignKey('OrganisationEntity', related_name='team',null=True)


    objects = UserManager()


class OrganisationEntity(models.Model):
    __metaclass__= TransMeta
    name = models.CharField(verbose_name=_('Name'), max_length=100, null=False)

    commune = models.BooleanField(default=False)
    region = models.BooleanField(default=False)
    subcontractor = models.BooleanField(default=False)
    applicant = models.BooleanField(default=False)
    dependency = models.ForeignKey('OrganisationEntity',related_name='parent', null=True)
    feature_id = models.CharField(max_length=25)

    class Meta:
        translate = ('name', )


class Report(models.Model):

    #List of qualities
    RESIDENT = 0
    OTHER = 1
    TRADE = 2
    SYNDICATE = 3
    ASSOCIATION = 4
    REPORT_QUALITY_CHOICES = (
        (RESIDENT,_("Resident")), 
        (OTHER,_("Other")),
        (TRADE,_("Trade")),
        (SYNDICATE,_("Syndicate")),
        (ASSOCIATION,_("Association"))
    )

    # List of status
    CREATED = 0
    REFUSED = 9
    
    IN_PROGRESS           = 1
    MANAGER_ASSIGNED      = 4
    APPLICANT_RESPONSIBLE = 5
    CONTRACTOR_ASSIGNED   = 6
    SOLVED                = 7

    PROCESSED = 3
    DELETED   = 8

    REPORT_STATUS_IN_PROGRESS = (IN_PROGRESS, MANAGER_ASSIGNED, APPLICANT_RESPONSIBLE, CONTRACTOR_ASSIGNED, SOLVED)
    REPORT_STATUS_VIEWABLE    = (CREATED, IN_PROGRESS, MANAGER_ASSIGNED, APPLICANT_RESPONSIBLE, CONTRACTOR_ASSIGNED, PROCESSED, SOLVED)
    REPORT_STATUS_CLOSED      = (PROCESSED, DELETED)
    REPORT_STATUS_OFF         = (DELETED)

    REPORT_STATUS_CHOICES = (
        (_("Created"), (
            (CREATED,               _("Created")), # Aangemaakt, Cree
            (REFUSED,               _("Refused")), # Afgewezen, Refuse
        )),
        (_("In progress"), (
            (IN_PROGRESS,           _("In progress")),              # In behandeling, En progres
            (MANAGER_ASSIGNED,      _("Manager is assigned")),      # Gestionnaire is toegekend, Gestionnaire est assigne
            (APPLICANT_RESPONSIBLE, _("Applicant is responsible")), # Impetrant is verantwoordelijk, Impetrant est responsable
            (CONTRACTOR_ASSIGNED,   _("Contractor is assigned")),   # Executeur de travaux is toegekend, Executeur de travaux est assigne
            (SOLVED,                _("Solved")),                   # Opgelost, Resolu
        )),
        (_("Processed"), (
            (PROCESSED,             _("Processed")),# Afgehandeld, Precessed
            (DELETED,               _("Deleted")),  # Suprime, Verwijderd
        ))
    )

    status = models.IntegerField(choices=REPORT_STATUS_CHOICES, null=False)
    quality = models.IntegerField(choices=REPORT_QUALITY_CHOICES, null=True)
    point = models.PointField(null=True, srid=31370)
    address = models.CharField(max_length=255, verbose_name=ugettext_lazy("Location"))
    postalcode = models.CharField(max_length=4, verbose_name=ugettext_lazy("Postal Code"))
    description = models.TextField(null=True)
    category = models.ForeignKey('ReportMainCategoryClass', null=True, verbose_name=ugettext_lazy("Category"))
    secondary_category = models.ForeignKey('ReportCategory', null=True, verbose_name=ugettext_lazy("Category"))

    creator = models.ForeignKey(User,null=True, related_name='creator')
    created_at = models.DateTimeField(auto_now_add=True)
    # last time report was updated
    updated_at = models.DateTimeField(null=True)
    # time report was marked as 'fixed'
    fixed_at = models.DateTimeField(null=True, blank=True)

    hash_code = models.IntegerField(null=True) # used by external app for secure sync, must be random generated
    
    citizen = models.ForeignKey(User,null=True, related_name='citizen')
    #refusal_motivation = models.TextField(null=True)
    #responsible = models.ForeignKey(OrganisationEntity, related_name='in_charge_reports', null=False)
    responsible_entity = models.ForeignKey('OrganisationEntity', related_name='reports_in_charge', null=True)
    contractor = models.ForeignKey(OrganisationEntity, related_name='assigned_reports', null=True)
    responsible_manager = models.ForeignKey(FMSUser, related_name='reports_in_charge', null=True)
    responsible_manager_validated = models.BooleanField(default=False)

    valid = models.BooleanField(default=False)
    private = models.BooleanField(default=True)
    photo = FixStdImageField(upload_to="photos", blank=True, size=(380, 380), thumbnail_size=(66, 50))
    close_date = models.DateTimeField(null=True, blank=True)

    objects = models.GeoManager()
    def get_absolute_url(self):
        #TODO determine when pro and no-pro url must be returned
        return reverse("report_show", args=[self.id])
    
    def get_absolute_url_pro(self):
        #TODO determine when pro and no-pro url must be returned
        return reverse("report_show_pro", args=[self.id])

    def is_created(self):  	
        return self.status == Report.CREATED

    def is_in_progress(self):
        return self.status in Report.REPORT_STATUS_IN_PROGRESS

    def is_closed(self):
        return self.status in Report.REPORT_STATUS_CLOSED

    def to_object(self):
        return {
            "id": self.id,
            "point": {
                "x": self.point.x,
                "y": self.point.y,
            },
            "status": self.status,
            "status_label": self.get_status_display(),
            "close_date": self.close_date,
            "private": self.private,
            "valid": self.valid
        }


class Exportable(models.Model):
    def asJSON():
        return
    def asXML():
        return

    class Meta:
        abstract = True


class ReportAttachment(models.Model):
    report = models.ForeignKey(Report)
    validated=models.BooleanField(default=False)
    isVisible=models.BooleanField(default=False)
    title=models.CharField(max_length=250)
    
    class Meta:
        abstract=True


class ReportComment(ReportAttachment):
    text = models.TextField()


class ReportFile(ReportAttachment):
    PDF   = 1
    WORD  = 2
    EXCEL = 3
    IMAGE = 4
    attachment_type = (
        (PDF  , "pdf"),
        (WORD , "word"),
        (EXCEL, "excel"),
        (IMAGE, "image")
    )
    file = models.FileField(upload_to="files")
    file_type = models.IntegerField(choices=attachment_type)


@receiver(pre_save,sender=Report)
def report_assign_responsible(sender, instance, **kwargs):
    """signal on a report to notify public authority that a report has been filled"""
    if not instance.responsible_manager:
        #Detect who is the responsible Manager for the given type
        #When created by pro a creator exists otherwise a citizen object
        organizationSearchCriteria = -1
        #if instance.creator:
        #    fmsUser = FMSUser.objects.get(pk=instance.creator.id)
        #    organizationSearchCriteria = fmsUser.organisation
        #elif instance.citizen:
        instance.commune = OrganisationEntity.objects.get(zipcode__code=instance.postalcode)
        organizationSearchCriteria = instance.commune

        #Assign the entity.
        instance.responsible_entity = organizationSearchCriteria

        #Searcht the right responsible for the current organization.            
        userCandidates = FMSUser.objects.filter(organisation__id=organizationSearchCriteria.id).filter(manager=True)
        managerFound = False
        for currentUser in userCandidates:
            userCategories = currentUser.categories.all()
            for currentCategory in userCategories:
                if (currentCategory == instance.secondary_category):
                   managerFound = True
                   instance.responsible_manager = currentUser

        #If not manager found for the responsible commune, then reassign to the region
        if (managerFound == False):
            instance.responsible_entity  = OrganisationEntity.objects.get(region=True)
            userCandidates = FMSUser.objects.filter(organisation__id=organizationSearchCriteria.id).filter(manager=True)
            for currentUser in userCandidates:
                userCategories = currentUser.categories.all()
                for currentCategory in userCategories:
                    if (currentCategory == instance.secondary_category):
                        instance.responsible_manager = currentUser

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

# class ReportUpdate(models.Model):
    # """A new version of the status of a report"""
    # report = models.ForeignKey(Report)
    # desc = models.TextField(blank=True, null=True, verbose_name=ugettext_lazy("Details"))
    # created_at = models.DateTimeField(auto_now_add=True)
    # is_fixed = models.BooleanField(default=False)
    # author = models.ForeignKey(User,null=True)
    # photo = FixStdImageField(upload_to="photos", blank=True, size=(380, 380), thumbnail_size=(66, 50)) 
    # 
    # class Meta:
        # ordering = ['created_at']
        # #order_with_respect_to = 'report'
# 
# #update the report, set updated_at and is_fixed correctly
# @receiver(post_save, sender=ReportUpdate)
# def update_report(sender, instance, **kwargs):
    # instance.report.updated_at = instance.created_at
# 
    # instance.report.is_fixed = instance.is_fixed
    # if(instance.is_fixed and not instance.report.fixed_at):
        # instance.report.fixed_at = instance.created_at
# 
    # instance.report.save()

#notify subscribers that report has been updated
# @receiver(post_save, sender=ReportUpdate)
# def notify(sender, instance, **kwargs):
    # if not kwargs['raw']:
        # for subscribe in instance.report.reportsubscription_set.exclude(Q(subscriber__email__isnull=True) | Q(subscriber__email__exact='')):
            # unsubscribe_url = 'http://{0}{1}'.format(Site.objects.get_current().domain, reverse("unsubscribe", args=[instance.report.id]))
            # msg = HtmlTemplateMail('report_update', {'update': instance, 'unsubscribe_url': unsubscribe_url}, [subscribe.subscriber.email])
            # msg.send()


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
    hint = models.ForeignKey('ReportCategoryHint', null=True)
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
        translate = ('name', )


class ReportCategoryHint(models.Model):
    __metaclass__ = TransMeta
    label = models.TextField(verbose_name=_('Label'), blank=False, null=False)
    class Meta:
        translate = ('label', )


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
        'OrganisationEntity',
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
        #if self.report.commune.default_manager:
        #    self.send(self.report.commune.default_manager)
        for rule in self.rules:
            if rule.rule == NotificationRule.TO_COUNCILLOR:
                self.send(rule.councillor)

            if rule.rule == NotificationRule.MATCHING_CATEGORY_CLASS:
                if self.report.category.category_class == rule.category_class:
                    self.send(rule.councillor)

            if rule.rule == NotificationRule.NOT_MATCHING_CATEGORY_CLASS:
                if self.report.category.category_class != rule.category_class:
                    self.send(rule.councillor)


# class Zone(models.Model):
    # __metaclass__ = TransMeta
    # 
    # name=models.CharField(max_length=100)
    # creation_date = models.DateTimeField(auto_now_add=True, blank=True,default=dt.now())
    # update_date = models.DateTimeField(auto_now=True, blank=True,default=dt.now())
    # commune = models.ForeignKey(Commune)
    # 
    # class Meta:
        # translate = ('name', )
# 
# 
# class FMSUserZone(models.Model):
    # user = models.ForeignKey(FMSUser)
    # zone = models.ForeignKey(Zone)
    # creation_date = models.DateTimeField(auto_now_add=True, blank=True,default=dt.now())
    # update_date = models.DateTimeField(auto_now=True, blank=True,default=dt.now())
# 

class ZipCode(models.Model):
    __metaclass__ = TransMeta
    
    commune = models.ForeignKey(OrganisationEntity)
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
 

class ListItem(models.Model):
    """
    Only for sql selection purpose
    """
    __metaclass__= TransMeta
    label = models.CharField(verbose_name=_('Label'),max_length=100,null=False)
    model_class = models.CharField(verbose_name=_('Related model class name'),max_length=100,null=False)
    model_field = models.CharField(verbose_name=_('Related model field'),max_length=100,null=False)
    code = models.CharField(max_length=50,null=False)
    
    class Meta:
        translate = ('label', )


def dictToPoint(data):
    if not data.has_key('x') or not data.has_key('y'):
        raise Http404('<h1>Location not found</h1>')
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

