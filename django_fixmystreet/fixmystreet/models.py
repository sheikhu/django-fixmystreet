from django.utils import simplejson
from datetime import datetime as dt
from smtplib import SMTPException

from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy, ugettext as _
from django.contrib.auth.models import User, UserManager
from django.contrib.gis.geos import fromstr
from django.contrib.gis.db import models
from django.http import Http404
from django.core import serializers
from django.core.files.base import ContentFile

from transmeta import TransMeta
from simple_history.models import HistoricalRecords
from django_fixmystreet.fixmystreet.utils import FixStdImageField, HtmlTemplateMail, get_current_user
from django_extensions.db.models import TimeStampedModel



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
    telephone = models.CharField(max_length=20,null=True)
    #active = models.BooleanField(default=True)
    last_used_language = models.CharField(max_length=10,null=True)
    #hash_code = models.IntegerField(null=True)# used by external app for secure sync, must be random generated

    agent = models.BooleanField(default=False)
    manager = models.BooleanField(default=False)
    leader = models.BooleanField(default=False)

    impetrant = models.BooleanField(default=False) # todo rename to applicant
    contractor = models.BooleanField(default=False)
    
    categories = models.ManyToManyField('ReportCategory',related_name='type')
    organisation = models.ForeignKey('OrganisationEntity', related_name='team',null=True)

    objects = UserManager()

    # history = HistoricalRecords()
    
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


class OrganisationEntity(UserTrackedModel):
    __metaclass__= TransMeta
    name = models.CharField(verbose_name=_('Name'), max_length=100, null=False)

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

    class Meta:
        translate = ('name', )


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
    postalcode = models.CharField(max_length=4, verbose_name=ugettext_lazy("Postal Code"))
    description = models.TextField(null=True)
    category = models.ForeignKey('ReportMainCategoryClass', null=True, verbose_name=ugettext_lazy("Category"))
    secondary_category = models.ForeignKey('ReportCategory', null=True, verbose_name=ugettext_lazy("Category"))

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
    #photo = FixStdImageField(upload_to="photos", blank=True, size=(380, 380), thumbnail_size=(66, 50))
    photo = models.FileField(upload_to="photos")
    close_date = models.DateTimeField(null=True, blank=True)

    objects = models.GeoManager()

    history = HistoricalRecords()

    def get_absolute_url(self):
        #TODO determine when pro and no-pro url must be returned
        slug = str(self.secondary_category.name).replace(' ', '').replace('(','').replace(')','') + '-'+str(self.category.name).replace(' ', '').replace('(','').replace(')','')+'-'+self.responsible_entity.name+''
        return reverse("report_show",kwargs={'report_id':self.id,'slug': slug })
    
    def get_absolute_url_pro(self):
        #TODO determine when pro and no-pro url must be returned
        slug = str(self.secondary_category.name).replace(' ', '').replace('(','').replace(')','') + '-'+str(self.category.name).replace(' ', '').replace('(','').replace(')','')+'-'+self.responsible_entity.name+''
        return reverse("report_show_pro", kwargs={'report_id':self.id,'slug': slug })

    def has_at_least_one_non_confidential_comment(self):
        return ReportComment.objects.filter(report__id=self.id).filter(isVisible=True).count() != 0    
    
    def has_at_least_one_non_confidential_file(self):
        return ReportFile.objects.filter(report__id=self.id).filter(isVisible=True).count() != 0    

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


class ReportAttachment(UserTrackedModel):
    is_validated = models.BooleanField(default=False)
    is_visible = models.BooleanField(default=False)
    title = models.CharField(max_length=250)

    class Meta:
        abstract=True
    
    def is_confidential_visible(self):
        '''visible when not confidential'''
        current_user = get_current_user().fmsuser
        return (self.isVisible and (current_user.contractor or current_user.applicant) or (current_user.manager or current_user.leader))
    
    def is_citizen_visible(self):
        '''Visible when not confidential and public'''
        return self.validated and self.isVisible
    
    def get_display_name(self):
        if (self.created_by.first_name == None and self.created_by.last_name == None):
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
        instance.responsible_entity = OrganisationEntity.objects.get(zipcode__code=instance.postalcode)
        organizationSearchCriteria = instance.responsible_entity

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
        #if (managerFound == False):
        #    instance.responsible_entity  = OrganisationEntity.objects.get(region=True)
        #    userCandidates = FMSUser.objects.filter(organisation__id=organizationSearchCriteria.id).filter(manager=True)
        #    for currentUser in userCandidates:
        #        userCategories = currentUser.categories.all()
        #        for currentCategory in userCategories:
        #            if (currentCategory == instance.secondary_category):
        #                instance.responsible_manager = currentUser


# 
@receiver(post_save,sender=Report)
def report_subscribe_author(sender, instance, **kwargs):
    """
    signal on a report to register author as subscriber to his own report
    """
    if kwargs['created'] and not kwargs['raw']:
        if instance.created_by:
            ReportSubscription(report=instance, subscriber=instance.created_by).save()


# #update the report, set modified and is_fixed correctly
# @receiver(post_save, sender=ReportUpdate)
# def update_report(sender, instance, **kwargs):
    # instance.report.modified = instance.created
# 
    # instance.report.is_fixed = instance.is_fixed
    # if(instance.is_fixed and not instance.report.fixed_at):
        # instance.report.fixed_at = instance.created
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

@receiver(post_save,sender=ReportSubscription)
def notify_report_subscription(sender, instance, **kwargs):
    if not kwargs['raw'] and instance.subscriber.email:
        report = instance.report
        mail = HtmlTemplateMail(template_dir='send_subscription_to_subscriber', data={
            'report':   report,
            'comments': report.comments.all(),
            'files':    report.files.all()
        },
        recipients=(instance.subscriber.email,))
        mail.send()

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
    
    @staticmethod    
    def listToJSON(list_of_elements):
        list_of_elements_as_json = []
        for current_element in list_of_elements:
            d = {}
            d['id'] = getattr(current_element, 'id')
            d['n_en'] = getattr(current_element, 'name_en')
            d['n_fr'] = getattr(current_element, 'name_fr')
            d['n_nl'] = getattr(current_element, 'name_nl')
            d['m_c_id'] = getattr(getattr(current_element, 'category_class'),'id')
            d['m_c_n_en'] = getattr(getattr(current_element, 'category_class'),'name_en')
            d['m_c_n_fr'] = getattr(getattr(current_element, 'category_class'),'name_fr')
            d['m_c_n_nl'] = getattr(getattr(current_element, 'category_class'),'name_nl')
            d['s_c_id'] = getattr(getattr(current_element, 'secondary_category_class'),'id')
            d['s_c_n_en'] = getattr(getattr(current_element, 'secondary_category_class'),'name_en')
            d['s_c_n_fr'] = getattr(getattr(current_element, 'secondary_category_class'),'name_fr')
            d['s_c_n_nl'] = getattr(getattr(current_element, 'secondary_category_class'),'name_nl')
            list_of_elements_as_json.append(d)
        return simplejson.dumps(list_of_elements_as_json)
 
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


# 
# class ReportNotification(models.Model):
    # report = models.ForeignKey(Report)
    # recipient = models.ForeignKey(FMSUser)
    # content_template = models.CharField(max_size)
    # sent_at = models.DateTimeField()
    # success = models.BooleanField()
    # message = models.TextField()
# 
# 
    # def send(self):
        # msg = HtmlTemplateMail('send_report_to_city', {'report': self.report}, (self.to_councillor.email,))
        # data['SITE_URL'] = 'http://locahost'
        # 
        # subject, html, text = '', '', ''
        # try:
            # subject = render_to_string('emails/' + template_dir + "/subject.txt", data)
        # except TemplateDoesNotExist:
            # pass
        # try:
            # text    = render_to_string('emails/' + template_dir + "/message.txt", data)
        # except TemplateDoesNotExist:
            # pass
        # try:
            # html    = render_to_string('emails/' + template_dir + "/message.html", data)
        # except TemplateDoesNotExist:
            # pass
        # subject = subject.rstrip(' \n\t').lstrip(' \n\t')
        # super(HtmlTemplateMail, self).__init__(subject, text, settings.EMAIL_FROM_USER, recipients, **kargs)
        # if html:
            # self.attach_alternative(html, "text/html")
# 
# 
        # if self.report.photo:
            # msg.attach_file(self.report.photo.file.name)
        # self.sent_at = dt.now()
        # try:
            # msg.send()
            # self.success = True
        # except SMTPException as e:
            # self.success = False
            # self.msg = str(e)
# 

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

