from django.utils import simplejson
from datetime import datetime as dt
from smtplib import SMTPException

from django.db.models.signals import pre_save, post_save, post_init
from django.dispatch import receiver
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy, ugettext as _
from django.contrib.auth.models import User, UserManager
from django.contrib.sites.models import Site
from django.contrib.gis.geos import fromstr
from django.contrib.gis.db import models
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.template import TemplateDoesNotExist
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.core import serializers
from django.conf import settings
from django.http import Http404

from transmeta import TransMeta
from simple_history.models import HistoricalRecords
from django_fixmystreet.fixmystreet.utils import FixStdImageField, get_current_user, save_file_to_server, autoslug_transmeta
from django_extensions.db.models import TimeStampedModel
from django_extensions.db.fields import AutoSlugField



class UserTrackedModel(TimeStampedModel):
    created_by = models.ForeignKey(User, null=True, editable=False, related_name='%(class)s_created')
    modified_by = models.ForeignKey(User, null=True, editable=False, related_name='%(class)s_modified')

    def save(self, *args, **kwargs):
        user = get_current_user()
        if user and user.is_authenticated():
            if self.id:
                self.modified_by = user
            else:
                self.created_by = user
            self._history_user = user # used by simple_history
        super(UserTrackedModel, self).save(*args, **kwargs)

    class Meta:
        abstract = True


class FMSUser(User):
    AGENT        = 1
    MANAGER      = 2
    LEADER       = 3
    CONTRACTOR   = 4
    APPLICANT    = 5

    telephone = models.CharField(max_length=20,null=True)
    #active = models.BooleanField(default=True)
    last_used_language = models.CharField(max_length=10,null=True)
    #hash_code = models.IntegerField(null=True)# used by external app for secure sync, must be random generated

    agent = models.BooleanField(default=False)
    manager = models.BooleanField(default=False)
    leader = models.BooleanField(default=False)

    impetrant = models.BooleanField(default=False) # todo rename to applicant
    contractor = models.BooleanField(default=False)
    
    logical_deleted = models.BooleanField(default=False)
    
    categories = models.ManyToManyField('ReportCategory',related_name='type')
    organisation = models.ForeignKey('OrganisationEntity', related_name='team',null=True)

    objects = UserManager()

    # history = HistoricalRecords()
    
    def display_category(self):
        return self.category.name+" / "+self.secondary_category.secondary_category_class.name+" : "+self.secondary_category.name

    def get_ticket_number(self):
        '''Return the report ticket as a usable string'''
        report_ticket_id = str(self.id)
        if (report_ticket_id.__len__() <= 8):
            for i in range(8-(report_ticket_id.__len__())):
                report_ticket_id = "0"+report_ticket_id;
        return report_ticket_id

    def get_ticket_as_string(self):   
        '''Return the report ticket as a displayable component'''
        return "#"+self.get_ticket_number()
    
    def get_display_name(self):
        if (self.first_name == None and self.last_name == None):
             return 'ANONYMOUS'
        else:
             return self.first_name+' '+self.last_name 

    def get_organisation(self):
        '''Return the user organisation and its dependency in case of contractor'''
        if self.contractor == True:
             return self.organisation.dependency
        else:
             return self.organisation

    def is_pro(self):
        return self.agent or self.manager or self.leader or self.impetrant or self.contractor

    def is_citizen(self):
        return not self.is_pro()

    def can_see_confidential(self):
        return self.leader or self.manager

    def get_langage(self):
        return self.last_used_language

    def get_user_type(self):
        if self.leader:
            return "leader"
        if self.manager:
            return "manager"
        if self.agent:
            return "agent"
        if self.impetrant:
            return "impetrant"
        if self.contractor:
            return "contractor"

    def toJSON(self):
        d = {}
        d['id'] = getattr(self, 'id')
        d['first_name'] = getattr(self, 'first_name')
        d['last_name'] = getattr(self, 'last_name')
        d['email'] = getattr(self, 'email')
        d['last_used_language'] = getattr(self, 'last_used_language')
        d['organisation'] = getattr(self.get_organisation(), 'id')
        return simplejson.dumps(d)


User._meta.get_field_by_name('email')[0]._unique = True
User._meta.get_field_by_name('email')[0].null = True


class OrganisationEntity(UserTrackedModel):
    __metaclass__= TransMeta
    name = models.CharField(verbose_name=_('Name'), max_length=100, null=False)
    slug = models.SlugField(verbose_name=_('Slug'), max_length=100)

    commune = models.BooleanField(default=False)
    region = models.BooleanField(default=False)
    subcontractor = models.BooleanField(default=False)
    applicant = models.BooleanField(default=False)
    dependency = models.ForeignKey('OrganisationEntity', related_name='parent', null=True, blank=True)
    feature_id = models.CharField(max_length=25, null=True, blank=True)

    history = HistoricalRecords()

    def is_commune(self):
        return self.commune == True 
    def is_region(self):
        return self.region == True 
    def is_subcontractor(self):
        return self.subcontractor == True 
    def is_applicant(self):
        return self.applicant == True 
    def get_organisation_having_a_manager(self):
        return OrganisationEntity.objects.filter()

    def get_absolute_url(self):
        return reverse("report_commune_index", kwargs={'commune_id':self.id, 'slug':self.slug})

    class Meta:
        translate = ('name', 'slug')

pre_save.connect(autoslug_transmeta('name', 'slug'), weak=False, sender=OrganisationEntity)


class Report(UserTrackedModel):

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

    REPORT_STATUS_SETTABLE_TO_SOLVED = (IN_PROGRESS, MANAGER_ASSIGNED, APPLICANT_RESPONSIBLE, CONTRACTOR_ASSIGNED)
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

    status = models.IntegerField(choices=REPORT_STATUS_CHOICES, default=CREATED, null=False)
    quality = models.IntegerField(choices=REPORT_QUALITY_CHOICES, null=True)
    point = models.PointField(null=True, srid=31370)
    address = models.CharField(max_length=255, verbose_name=ugettext_lazy("Location"))
    address_number = models.CharField(max_length=255, verbose_name=ugettext_lazy("Address Number"))
    postalcode = models.CharField(max_length=4, verbose_name=ugettext_lazy("Postal Code"))
    description = models.TextField(null=True)
    category = models.ForeignKey('ReportMainCategoryClass', null=True, verbose_name=ugettext_lazy("Category"))
    secondary_category = models.ForeignKey('ReportCategory', null=True, verbose_name=ugettext_lazy("Category"))

    fixed_at = models.DateTimeField(null=True, blank=True)

    hash_code = models.IntegerField(null=True) # used by external app for secure sync, must be random generated
    
    citizen = models.ForeignKey(User,null=True, related_name='citizen_reports')
    refusal_motivation = models.TextField(null=True)
    #responsible = models.ForeignKey(OrganisationEntity, related_name='in_charge_reports', null=False)
    responsible_entity = models.ForeignKey('OrganisationEntity', related_name='reports_in_charge', null=True)
    contractor = models.ForeignKey(OrganisationEntity, related_name='assigned_reports', null=True)
    responsible_manager = models.ForeignKey(FMSUser, related_name='reports_in_charge', null=True)
    responsible_manager_validated = models.BooleanField(default=False)

    valid = models.BooleanField(default=False)
    private = models.BooleanField(default=True)
    #photo = FixStdImageField(upload_to="photos", blank=True, size=(380, 380), thumbnail_size=(66, 50))
    photo = models.FileField(upload_to="photos")
    close_date = models.DateTimeField(null=True, blank=True)

    objects = models.GeoManager()

    history = HistoricalRecords()

    def display_category(self):
        return self.category.name+" / "+self.secondary_category.secondary_category_class.name+" : "+self.secondary_category.name

    def get_ticket_number(self):
        '''Return the report ticket as a usable string'''
        report_ticket_id = str(self.id)
        if (report_ticket_id.__len__() <= 8):
            for i in range(8-(report_ticket_id.__len__())):
                report_ticket_id = "0"+report_ticket_id;
        return report_ticket_id

    def get_ticket_as_string(self):   
        '''Return the report ticket as a displayable component'''
        return "#"+self.get_ticket_number()
    
    def get_absolute_url(self):
        #TODO determine when pro and no-pro url must be returned
        slug = self.secondary_category.slug  + '-' + self.secondary_category.secondary_category_class.slug + '-' + self.category.slug + '-' + self.responsible_entity.slug
        return reverse("report_show",kwargs={'report_id':self.id,'slug': slug })
    
    def get_absolute_url_pro(self):
        #TODO determine when pro and no-pro url must be returned
        slug = str(self.secondary_category.name).replace(' ', '_').replace('(','').replace(')','') + '-' + str(self.secondary_category.secondary_category_class.name).replace(' ', '_').replace('(','').replace(')','').replace('/','_') + '-' + str(self.category.name).replace(' ', '_').replace('(','').replace(')','') + '-' + self.responsible_entity.name + ''
        return reverse("report_show_pro", kwargs={'report_id':self.id,'slug': slug })

    def has_at_least_one_non_confidential_comment(self):
        return ReportComment.objects.filter(report__id=self.id).filter(is_visible=True).count() != 0    
    
    def has_at_least_one_non_confidential_file(self):
        return ReportFile.objects.filter(report__id=self.id).filter(is_visible=True).count() != 0    

    def get_comments(self):  	
        return ReportComment.objects.filter(report__id=self.id)
    
    def get_files(self):  	
        return ReportFile.objects.filter(report__id=self.id)
    
    def is_created(self):  	
        return self.status == Report.CREATED

    def is_in_progress(self):
        return self.status in Report.REPORT_STATUS_IN_PROGRESS

    def is_closed(self):
        return self.status in Report.REPORT_STATUS_CLOSED
    
    def is_markable_as_solved(self):
        return self.status in Report.REPORT_STATUS_SETTABLE_TO_SOLVED

    def attachments(self):
        return list(self.comments.all()) + list(self.files.all()) # order by created
    
    def to_full_JSON(self):
        """
        Method used to display the whole object content as JSON structure for website
        """
        return {
            "id": self.id,
            "point": {
                "x": self.point.x,
                "y": self.point.y,
            },
            "status": self.status,
            "quality": self.quality,
            "address": self.address,
            "postalcode": self.postalcode,
            "description": self.description,
            "category": self.category.id,
            "secondary_category": self.secondary_category.id,
            "fixed_at": self.fixed_at,
            "hash_code": self.hash_code,
            "citizen": self.citizen.email,
            "responsible_entity": self.responsible_entity.id,
            "contractor": self.contractor,
            "responsible_manager": self.responsible_manager.username,
            "close_date":  str(self.close_date),
            "private": self.private,
            "valid": self.valid
        }

    def to_JSON(self):
        """
        Method used to display the object as JSON structure for website
        """

        close_date_as_string = ""
        if (self.close_date):
            close_date_as_string = self.close_date.strftime("%Y-%m-%d %H:%M:%S")

        return {
            "id": self.id,
            "point": {
                "x": self.point.x,
                "y": self.point.y,
            },
            "status": self.status,
            "status_label": self.get_status_display(),
            "close_date": close_date_as_string,
            "private": self.private,
            "valid": self.valid
        }

    def to_mobile_JSON(self):
        """
        Method used to display the object as JSON structure
        id = unique id
        p = point
        p.x = x coordinate
        p.y = y coordinate
        s = status
        c_d = close date
        pr = private flag
        v = valid flag
        c = main category id
        m_c = first category
        s_c = second category
        """
        
        close_date_as_string = ""
        if (self.close_date):
            close_date_as_string = self.close_date.strftime("%Y-%m-%d %H:%M:%S")
        
        return {
            "id": self.id,
            "p": {
                "x": self.point.x,
                "y": self.point.y,
            },
            "s": self.status,
            "c_d": close_date_as_string,
            "pr": self.private,
            "v": self.valid,
            "c": self.secondary_category.id,
            "m_c": self.secondary_category.category_class.id,
            "s_c": self.secondary_category.secondary_category_class.id
        }


@receiver(pre_save,sender=Report)
def report_assign_responsible(sender, instance, **kwargs):
    if not instance.responsible_manager:
        #Detect who is the responsible Manager for the given type
        #When created by pro a creator exists otherwise a citizen object

        if instance.created_by and hasattr(instance.created_by, 'fmsuser') and instance.created_by.fmsuser.organisation:
            # assign entity of the creator
            instance.responsible_entity = instance.created_by.fmsuser.organisation
        else:
            instance.responsible_entity = OrganisationEntity.objects.get(zipcode__code=instance.postalcode)

        #Searcht the right responsible for the current organization.            
        userCandidates = FMSUser.objects.filter(organisation=instance.responsible_entity).filter(manager=True)
        # TODO: use filters instead of iteration...
        for currentUser in userCandidates:
            userCategories = currentUser.categories.all()
            for currentCategory in userCategories:
                if (currentCategory == instance.secondary_category):
                   instance.responsible_manager = currentUser

@receiver(post_init, sender=Report)
def track_former_value(sender, instance, **kwargs):
    """Save former data to compare with new data and track changed values"""
    instance.__former = dict((field.name, field.value_from_object(instance)) for field in Report._meta.fields)

@receiver(post_save, sender=Report)
def report_notify_author(sender, instance, **kwargs):
    """signal on a report to notify author that the status of the report has changed"""
    report = instance
    if not kwargs['raw'] and report.__former['status'] != report.status:
        if report.status == Report.REFUSED:
            notifiation = ReportNotification(
                content_template='send_report_refused_to_creator',
                recipient=report.citizen or report.created_by,
                related=report,
            )
            notifiation.save()
        elif report.status == Report.PROCESSED:
            for subscription in report.subscriptions.all():
                notifiation = ReportNotification(
                    content_template='send_report_closed_to_subscribers',
                    recipient=subscription.subscriber,
                    related=report,
                )
                notifiation.save()
        elif report.status == Report.SOLVED:
            notifiation = ReportNotification(
                content_template='send_report_fixed_to_gest_resp',
                recipient=report.responsible_manager,
                related=report,
            )
            notifiation.save()

@receiver(post_save, sender=Report)
def report_notify_manager(sender, instance, **kwargs):
    """signal on a report to notify manager that a report has been filled"""
    report = instance
    if not kwargs['raw'] and kwargs['created']:
        notifiation = ReportNotification(
            content_template='send_report_creation_to_gest_resp',
            recipient=report.responsible_manager,
            related=report,
        )
        notifiation.save()

@receiver(post_save,sender=Report)
def report_subscribe_author(sender, instance, **kwargs):
    """signal on a report to register author as subscriber to his own report"""
    if kwargs['created'] and not kwargs['raw']:
        if instance.created_by:
            ReportSubscription(report=instance, subscriber=instance.created_by).save()


class Exportable(models.Model):
    def asJSON():
        return
    def asXML():
        return

    class Meta:
        abstract = True


class ReportAttachment(UserTrackedModel):
    is_validated = models.BooleanField(default=False)
    is_visible = models.BooleanField(default=False)

    class Meta:
        abstract=True
    
    def is_confidential_visible(self):
        '''visible when not confidential'''
        current_user = get_current_user().fmsuser
        return (self.is_visible and (current_user.contractor or current_user.applicant) or (current_user.manager or current_user.leader))
    
    def is_citizen_visible(self):
        '''Visible when not confidential and public'''
        return self.is_validated and self.is_visible
    
    def get_display_name(self):
        if (not self.created_by or self.created_by.first_name == None and self.created_by.last_name == None):
             return 'ANONYMOUS'
        else:
             return self.created_by.first_name+' '+self.created_by.last_name 


class ReportComment(ReportAttachment):
    text = models.TextField()
    report = models.ForeignKey(Report, related_name="comments")
    
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
    report = models.ForeignKey(Report, related_name="files")
    title = models.CharField(max_length=250)
    file_creation_date= models.DateTimeField(null=True)

    def is_pdf(self):
        return self.file_type == ReportFile.PDF
    def is_word(self):
        return self.file_type == ReportFile.WORD
    def is_excel(self):
        return self.file_type == ReportFile.EXCEL
    def is_image(self):
        return self.file_type == ReportFile.IMAGE
    def is_a_document(self):
        return self.is_pdf() or self.is_word() or self.is_excel() 
    def is_an_image(self):
        return self.is_image()

@receiver(post_save,sender=FMSUser)
def create_matrix_when_creating_first_manager(sender, instance, **kwargs):
    """This method is used to create the security matrix when creating the first manager of the entity"""
    #If this is the first user created and of type gestionnaire then assign all reportcategories to him
    if (instance.manager == True):
       #if we have just created the first one, then apply all type to him
       if len(FMSUser.objects.filter(organisation_id=instance.organisation.id).filter(manager=True)) == 1:
          for type in ReportCategory.objects.all():
             instance.categories.add(type)


@receiver(post_save,sender=ReportFile)
def move_file(sender,instance,**kwargs):
    if kwargs['created']:
        file_type_string =ReportFile.attachment_type[instance.file_type-1][1]
        extension = {1:'pdf',2:'doc',3:'xls',4:'jpg'}[instance.file_type]
        new_destination = save_file_to_server(instance.file,file_type_string,extension,len(ReportFile.objects.filter(report_id=instance.report_id)), instance.report.id)
        instance.file = new_destination
        instance.save()

class ReportSubscription(models.Model):
    """ 
    Report Subscribers are notified when there's an update to an existing report.
    """
    report = models.ForeignKey(Report, related_name="subscriptions")
    subscriber = models.ForeignKey(User, null=False)
    class Meta:
        unique_together = (("report", "subscriber"),)

@receiver(post_save,sender=ReportSubscription)
def notify_report_subscription(sender, instance, **kwargs):
    if not kwargs['raw'] and kwargs['created']:
        report = instance.report
        notifiation = ReportNotification(
            content_template='send_subscription_to_subscriber',
            recipient=instance.subscriber,
            related=report,
        )
        notifiation.save()

class ReportMainCategoryClass(models.Model):
    __metaclass__ = TransMeta
    help_text = """
    Manage the category container list (see the report form). Allow to group categories.
    """

    name = models.CharField(verbose_name=_('Name'), max_length=100)
    slug = models.SlugField(verbose_name=_('Slug'), max_length=100)

    hint = models.ForeignKey('ReportCategoryHint', null=True)
    creation_date = models.DateTimeField(auto_now_add=True, blank=True,default=dt.now())
    update_date = models.DateTimeField(auto_now=True, blank=True,default=dt.now())
    def __unicode__(self):      
        return self.name
    
    @staticmethod    
    def listToJSON(list_of_elements):
        list_of_elements_as_json = []
        for current_element in list_of_elements:
            d = {}
            d['id'] = getattr(current_element, 'id')
            d['name_en'] = getattr(current_element, 'name_en')
            d['name_fr'] = getattr(current_element, 'name_fr')
            d['name_nl'] = getattr(current_element, 'name_nl')
            list_of_elements_as_json.append(d)
        return simplejson.dumps(list_of_elements_as_json)

    class Meta:
        verbose_name = "category group"
        verbose_name_plural = "category groups"
        translate = ('name', )

pre_save.connect(autoslug_transmeta('name', 'slug'), weak=False, sender=ReportMainCategoryClass)


class ReportSecondaryCategoryClass(models.Model):
    __metaclass__ = TransMeta
    help_text = """
    Manage the category container list (see the report form). Allow to group categories.
    """

    name = models.CharField(verbose_name=_('Name'), max_length=100)
    slug = models.SlugField(verbose_name=_('Slug'), max_length=100)

    creation_date = models.DateTimeField(auto_now_add=True, blank=True,default=dt.now())
    update_date = models.DateTimeField(auto_now=True, blank=True,default=dt.now())
    def __unicode__(self):
        return self.name

    @staticmethod    
    def listToJSON(list_of_elements):
        list_of_elements_as_json = []
        for current_element in list_of_elements:
            d = {}
            d['id'] = getattr(current_element, 'id')
            d['name_en'] = getattr(current_element, 'name_en')
            d['name_fr'] = getattr(current_element, 'name_fr')
            d['name_nl'] = getattr(current_element, 'name_nl')
            list_of_elements_as_json.append(d)
        return simplejson.dumps(list_of_elements_as_json)

    class Meta:
        verbose_name = "category group"
        verbose_name_plural = "category groups"
        translate = ('name', )

pre_save.connect(autoslug_transmeta('name', 'slug'), weak=False, sender=ReportSecondaryCategoryClass)



class ReportCategory(models.Model):
    __metaclass__ = TransMeta
    help_text = """
    Manage the report categories list (see the report form).
    When a category is selected in the website form, the hint field is loaded in ajax and displayed  in the form.
    """

    name = models.CharField(verbose_name=_('Name'), max_length=100)
    slug = models.SlugField(verbose_name=_('Slug'), max_length=100)

    creation_date = models.DateTimeField(auto_now_add=True, blank=True,default=dt.now())
    update_date = models.DateTimeField(auto_now=True, blank=True,default=dt.now())
    category_class = models.ForeignKey(ReportMainCategoryClass, verbose_name=_('Category group'), help_text="The category group container")
    secondary_category_class = models.ForeignKey(ReportSecondaryCategoryClass, verbose_name=_('Category group'), help_text="The category group container")
    public = models.BooleanField(default=True)
    def __unicode__(self):      
        return self.category_class.name + ":" + self.name
    
    @staticmethod    
    def listToJSON(list_of_elements):
        list_of_elements_as_json = []
        d = {}
        prev_d = {
           'id':None,
           'n_en':None,
           'n_fr':None,
           'n_nl':None,
           'm_c_id':None,
           'm_c_n_en':None,
           'm_c_n_fr':None,
           'm_c_n_nl':None,
           's_c_id':None,
           's_c_n_en':None,
           's_c_n_fr':None,
           's_c_n_nl':None,
           'p':None
        }
        
        for current_element in list_of_elements:
            d = {}
            d['id'] = getattr(current_element, 'id')
            d['n_en'] = getattr(current_element, 'name_en')
            d['n_fr'] = getattr(current_element, 'name_fr')
            d['n_nl'] = getattr(current_element, 'name_nl')
            d['m_c_id'] = getattr(getattr(current_element, 'category_class'),'id')
            
            is_it_public = getattr(current_element, 'public')
            if is_it_public:
                d['p'] = 1
            else:
                d['p'] = 0
            
            #Optimize data transfered removing duplicates on main class names
            m_c_n_en_value = getattr(getattr(current_element, 'category_class'), 'name_en') 
            if is_it_public or not prev_d['m_c_n_en'] == m_c_n_en_value:
                prev_d['m_c_n_en'] = d['m_c_n_en'] = m_c_n_en_value
            m_c_n_fr_value = getattr(getattr(current_element, 'category_class'), 'name_fr') 
            if is_it_public or not prev_d['m_c_n_fr'] == m_c_n_fr_value:
                prev_d['m_c_n_fr'] = d['m_c_n_fr'] = m_c_n_fr_value
            
            m_c_n_nl_value = getattr(getattr(current_element, 'category_class'), 'name_nl') 
            if is_it_public or not prev_d['m_c_n_nl'] == m_c_n_nl_value:
                prev_d['m_c_n_nl'] = d['m_c_n_nl'] = m_c_n_nl_value
            d['s_c_id'] = getattr(getattr(current_element, 'secondary_category_class'),'id')
            
            #Optimize data transfered removing duplicates on main class names
            s_c_n_en_value = getattr(getattr(current_element, 'secondary_category_class'), 'name_en') 
            if is_it_public or not prev_d['s_c_n_en'] == s_c_n_en_value:
                prev_d['s_c_n_en'] = d['s_c_n_en'] = s_c_n_en_value
            s_c_n_fr_value = getattr(getattr(current_element, 'secondary_category_class'), 'name_fr') 
            if is_it_public or not prev_d['s_c_n_fr'] == s_c_n_fr_value:
                prev_d['s_c_n_fr'] = d['s_c_n_fr'] = s_c_n_fr_value
            s_c_n_nl_value = getattr(getattr(current_element, 'secondary_category_class'), 'name_nl') 
            if is_it_public or not prev_d['s_c_n_nl'] == s_c_n_nl_value:
                prev_d['s_c_n_nl'] = d['s_c_n_nl'] = s_c_n_nl_value
            

            list_of_elements_as_json.append(d)
        return simplejson.dumps(list_of_elements_as_json)
 
    class Meta:
        verbose_name = "category"
        verbose_name_plural = "categories"
        translate = ('name', )

pre_save.connect(autoslug_transmeta('name', 'slug'), weak=False, sender=ReportCategory)



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


class ReportNotification(models.Model):
    recipient = models.ForeignKey(User)
    sent_at = models.DateTimeField(auto_now_add=True)
    success = models.BooleanField()
    error_msg = models.TextField()
    content_template = models.CharField(max_length=40)

    related = generic.GenericForeignKey('related_content_type', 'related_object_id')
    related_content_type = models.ForeignKey(ContentType)
    related_object_id = models.PositiveIntegerField()

    def save(self, data={}, *args, **kwargs):
        if not self.recipient.email:
            self.error_msg = "No email recipient"
            self.success = False
            super(ReportNotification, self).save(*args, **kwargs)
            return 

        recipients = (self.recipient.email,)

        data = data or {}
        data.update({
            "related": self.related,
            "SITE_URL": Site.objects.get_current().domain
        })

        subject, html, text = '', '', ''
        try:
            subject = render_to_string('emails/' + self.content_template + "/subject.txt", data)
        except TemplateDoesNotExist:
            self.error_msg = "No subject"
        try:
            text    = render_to_string('emails/' + self.content_template + "/message.txt", data)
        except TemplateDoesNotExist:
            self.error_msg = "No content"

        try:
            html    = render_to_string('emails/' + self.content_template + "/message.html", data)
        except TemplateDoesNotExist:
            pass

        subject = subject.rstrip(' \n\t').lstrip(' \n\t')

        msg = EmailMultiAlternatives(subject, text, settings.EMAIL_FROM_USER, recipients)

        if html:
            msg.attach_alternative(html, "text/html")

        # if self.report.photo:
            # msg.attach_file(self.report.photo.file.name)

        try:
            msg.send()
            self.success = True
        except SMTPException as e:
            self.success = False
            self.error_msg = str(e)

        super(ReportNotification, self).save(*args, **kwargs)


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

    def get_usable_zipcodes(self):       
        allManagers = FMSUser.objects.filter(manager=True)
        allCommunesHavingManagers = ZipCode.objects.filter(commune_id__in=OrganisationEntity.objects.filter(id__in=allManagers.values_list("organisation", flat=True)).values_list("id",flat=True)).distinct('code')
        return allCommunesHavingManagers.filter(hide=False)

    def get_usable_zipcodes_to_mobile_json(self):
        list_of_elements_as_json = []
        for current_element in self.get_usable_zipcodes():
            d = {}
            d['c'] = getattr(current_element, 'code')
            list_of_elements_as_json.append(d)
        return simplejson.dumps(list_of_elements_as_json)

    
 
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
        d1= xml_serializer.serialize(Report.objects.filter(id=report.id),fields=('id','category', 'description', 'created_at', 'updated', 'status'))
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
