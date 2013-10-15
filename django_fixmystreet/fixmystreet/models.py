from django.utils import simplejson
from exceptions import Exception
import logging
import re
import datetime

from datetime import timedelta

from django.db.models.signals import pre_save, post_save, pre_delete
from django.dispatch import receiver
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User

from django.contrib.gis.db import models
from django.contrib.gis.db.models import Q
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.core.mail import EmailMultiAlternatives
from django.conf import settings

from transmeta import TransMeta
from django_extensions.db.models import TimeStampedModel
from simple_history.models import HistoricalRecords

from django_fixmystreet.fixmystreet.utils import FixStdImageField, get_current_user, autoslug_transmeta, transform_notification_template

logger = logging.getLogger(__name__)


class UserTrackedModel(TimeStampedModel):
    # created = models.DateTimeField(auto_now_add=True, null=True, blank=True, editable=False)
    # modified = models.DateTimeField(auto_now=True, null=True, blank=True, editable=False)
    created_by = models.ForeignKey('FMSUser', null=True, editable=False, related_name='%(class)s_created')
    modified_by = models.ForeignKey('FMSUser', null=True, editable=False, related_name='%(class)s_modified')

    def save(self, *args, **kwargs):
        user = get_current_user()
        if user and user.is_authenticated():
            self.modified_by = user
            if not self.id:
                self.created_by = user
            self._history_user = user # used by simple_history
        else:
            self.modified_by = None

        super(UserTrackedModel, self).save(*args, **kwargs)

    class Meta:
        abstract = True


User._meta.get_field_by_name('email')[0]._unique = True
User._meta.get_field_by_name('email')[0].null = True
User._meta.get_field_by_name('email')[0].max_length=75
User._meta.get_field_by_name('username')[0].max_length=75


class FMSUserManager(models.Manager):
    def get_query_set(self):
        return FMSUserQuerySet(self.model)


class FMSUserQuerySet(models.query.QuerySet):
    def is_pro(self):
        return self.filter(Q(agent=True) | Q(manager=True) | Q(leader=True) | Q(applicant=True) | Q(contractor=True))


class FMSUser(User):
    AGENT        = "agent"
    MANAGER      = "manager"
    LEADER       = "leader"
    CONTRACTOR   = "contractor"
    APPLICANT    = "applicant"

    # user types ordered by weight
    USER_TYPES = (
        LEADER,
        MANAGER,
        AGENT,
        APPLICANT,
        CONTRACTOR,
    )


    #List of qualities
    RESIDENT = 1
    TRADE = 2
    SYNDICATE = 3
    ASSOCIATION = 4
    OTHER = 5
    REPORT_QUALITY_CHOICES = (
        (RESIDENT,_("Resident")),
        (TRADE,_("Trade")),
        (SYNDICATE,_("Syndicate")),
        (ASSOCIATION,_("Association")),
        (OTHER,_("Other"))
    )


    # user = models.OneToOneField(User)
    objects = FMSUserManager()

    telephone = models.CharField(max_length=20,null=True)
    last_used_language = models.CharField(max_length=10,null=True,default="FR")
    #hash_code = models.IntegerField(null=True)# used by external app for secure sync, must be random generated
    quality = models.IntegerField(choices=REPORT_QUALITY_CHOICES, null=True, blank=True)


    agent = models.BooleanField(default=False)
    manager = models.BooleanField(default=False)
    leader = models.BooleanField(default=False)

    applicant = models.BooleanField(default=False)
    contractor = models.BooleanField(default=False)

    logical_deleted = models.BooleanField(default=False)

    ### deprecated to remove ###
    categories = models.ManyToManyField('ReportCategory', related_name='type', blank=True)
    organisation = models.ForeignKey('OrganisationEntity', related_name='team', null=True, blank=True) # organisation that can be responsible of reports
    ### deprecated to remove replaced by UserOrganisationMembership ###
    work_for = models.ManyToManyField('OrganisationEntity', related_name='workers', null=True, blank=True) # list of contractors/services that user work with

    history = HistoricalRecords()

    # http://scottbarnham.com/blog/2008/08/21/extending-the-django-user-model-with-inheritance/
    # must extends UserTrackedModel
    created = models.DateTimeField(auto_now_add=True, null=True, editable=False)
    modified = models.DateTimeField(auto_now=True, null=True, editable=False)
    created_by = models.ForeignKey('FMSUser', null=True, editable=False, related_name='%(class)s_created')
    modified_by = models.ForeignKey('FMSUser', null=True, editable=False, related_name='%(class)s_modified')

    def save(self, *args, **kwargs):
        user = get_current_user()

        if user and user.is_authenticated():
            self.modified_by = user

            if not self.id:
                self.created_by = user
            self._history_user = user # used by simple_history
        else:
            self.modified_by = None

        super(FMSUser, self).save(*args, **kwargs)

    def display_category(self):
        return self.category.name+" / "+self.secondary_category.secondary_category_class.name+" : "+self.secondary_category.name

    def get_ticket_number(self):
        '''Return the report ticket as a usable string'''
        report_ticket_id = str(self.id)
        return report_ticket_id

    def get_ticket_as_string(self):
        '''Return the report ticket as a displayable component'''
        return "#"+self.get_ticket_number()

    def get_display_name(self):
        if ((self.first_name == None or self.first_name == "") and (self.last_name == None or self.last_name == "")):
             return _('A citizen')
        else:
             return self.first_name+' '+self.last_name

    def get_organisation(self):
        '''Return the user organisation and its dependency in case of contractor'''
        if self.organisation:
             return self.organisation
        elif self.contractor == True or self.applicant == True:
            return u", ".join([unicode(o) for o in self.work_for.all()])

    def is_pro(self):
        return self.agent or self.manager or self.leader or self.applicant or self.contractor

    def is_citizen(self):
        return not self.is_pro()

    def can_see_confidential(self):
        return self.leader or self.manager

    def get_langage(self):
        return self.last_used_language

    def get_user_type(self):
        for user_type in self.USER_TYPES:
            if getattr(self, user_type, False):
                return user_type

    def is_user_type(self, user_type):
        return getattr(self, user_type, False)

    def toJSON(self):
        d = {}
        d['id'] = getattr(self, 'id')
        d['first_name'] = getattr(self, 'first_name')
        d['last_name'] = getattr(self, 'last_name')
        d['email'] = getattr(self, 'email')
        d['last_used_language'] = getattr(self, 'last_used_language')
        d['organisation'] = getattr(self.get_organisation(), 'id', None)
        return simplejson.dumps(d)

    ### DEPRECATED ??? ###
    def get_number_of_created_reports(self):
        userConnectedOrganisation = self.organisation
        reports = Report.objects.filter(responsible_entity=userConnectedOrganisation).filter(status=Report.CREATED)
        return reports.count()
    ### DEPRECATED ??? ###
    def get_number_of_in_progress_reports(self):
        connectedOrganisation = self.organisation
        userConnectedOrganisation = connectedOrganisation
        #if the user is an executeur de travaux then user the dependent organisation id
        if (self.contractor == True):
            reports = Report.objects.filter(contractor=self.organisation).filter(status__in=Report.REPORT_STATUS_IN_PROGRESS)
        else:
            reports = Report.objects.filter(responsible_entity=userConnectedOrganisation).filter(status__in=Report.REPORT_STATUS_IN_PROGRESS)
        return reports.count()
    ### DEPRECATED ??? ###
    def get_number_of_closed_reports(self):
        connectedOrganisation = self.organisation
        userConnectedOrganisation = connectedOrganisation
        #if the user is an executeur de travaux then user the dependent organisation id
        if (self.contractor == True):
            reports = Report.objects.filter(contractor=self.organisation).filter(status__in=Report.REPORT_STATUS_CLOSED)
        else:
            reports = Report.objects.filter(responsible_entity=userConnectedOrganisation).filter(status__in=Report.REPORT_STATUS_CLOSED)

        return reports.count()
    ### DEPRECATED ??? ###
    def get_number_of_subscriptions(self):
        subscriptions = ReportSubscription.objects.filter(subscriber_id=self.id)
        return subscriptions.count()

    def get_absolute_url(self):
        return reverse("edit_user",kwargs={'user_id':self.id})


@receiver(post_save, sender=FMSUser)
def create_matrix_when_creating_first_manager(sender, instance, **kwargs):
    """This method is used to create the security matrix when creating the first manager of the entity"""
    #If this is the first user created and of type gestionnaire then assign all reportcategories to him
    if (instance.manager == True):
       #if we have just created the first one, then apply all type to him
       if instance.organisation.team.filter(manager=True).count() == 1:
          #Activate the organisation
          instance.organisation.active = True
          instance.organisation.save()
          for type in ReportCategory.objects.all():
             instance.categories.add(type)


@receiver(pre_save, sender=FMSUser)
def populate_username(sender, instance, **kwargs):
    """populate username with email"""
    if instance.email and instance.username != instance.email and instance.is_active:
       instance.username = instance.email


class OrganisationEntity(UserTrackedModel):
    ENTITY_TYPE = (
        ('R', _('Region')),
        ('C', _('Commune')),
        ('S', _('Subcontractor')),
        ('A', _('Applicant')),
        ('D', _('Department')),
        ('N', _('Neighbour house')),
    )

    ENTITY_TYPE_GROUP = (
        ('S', _('Subcontractor')),
        ('D', _('Department')),
    )

    __metaclass__= TransMeta
    name = models.CharField(verbose_name=_('Name'), max_length=100, null=False)
    slug = models.SlugField(verbose_name=_('Slug'), max_length=100)
    phone = models.CharField(max_length=32)
    email = models.EmailField(null=True, blank=True)

    active = models.BooleanField(default=False)

    ### DEPRECATED use type instead ###
    commune = models.BooleanField(default=False)
    region = models.BooleanField(default=False)
    subcontractor = models.BooleanField(default=False)
    department = models.BooleanField(default=False)
    applicant = models.BooleanField(default=False)

    type = models.CharField(max_length=1, choices=ENTITY_TYPE, default='')

    dependency = models.ForeignKey('OrganisationEntity', related_name='associates', null=True, blank=True)
    feature_id = models.CharField(max_length=25, null=True, blank=True)

    dispatch_categories = models.ManyToManyField('ReportCategory', related_name='assinged_to_department', blank=True)

    history = HistoricalRecords()

    class Meta:
        translate = ('name', 'slug')

    def get_absolute_url(self):
        return reverse("report_commune_index", kwargs={'commune_id':self.id, 'slug':self.slug})

    def __unicode__(self):
        return self.name

    def get_total_number_of_reports(self):
        reports = Report.objects.filter(responsible_entity=self).all()
        #Activate something similar to this to filter per entity !!!
        #reports = Report.objects.filter(status_id=1).filter(responsible_manager__organisation=userConnectedOrganisation)
        return reports.count()

    def get_total_number_of_users(self):
        users = FMSUser.objects.filter(organisation_id = self.id).filter(logical_deleted = False)
        return users.count()

    def get_number_of_agents(self):
        agents = FMSUser.objects.filter(organisation_id = self.id).filter(logical_deleted = False)
        agents = agents.filter(agent = True)
        return agents.count()

    def get_number_of_contractors(self):
        #Get organisations dependants from the current organisation id
        dependantOrganisations = OrganisationEntity.objects.filter(dependency_id = self.id)
        allOrganisation = list(dependantOrganisations)
        allOrganisation.append(self.id)
        contractors = FMSUser.objects.filter(organisation_id__in=allOrganisation).filter(logical_deleted = False)
        contractors = contractors.filter(contractor = True)
        return contractors.count()

    def get_number_of_impetrants(self):
        impetrants = FMSUser.objects.filter(organisation_id = self.id).filter(logical_deleted = False)
        impetrants = impetrants.filter(applicant = True)
        return impetrants.count()

    def get_number_of_managers(self):
        managers = FMSUser.objects.filter(organisation_id = self.id).filter(logical_deleted = False)
        managers = managers.filter(manager = True)
        return managers.count()

pre_save.connect(autoslug_transmeta('name', 'slug'), weak=False, sender=OrganisationEntity)

@receiver(pre_delete, sender=OrganisationEntity)
def organisationentity_delete(sender, instance, **kwargs):
    # Delete all memberships associated
    memberships = UserOrganisationMembership.objects.filter(organisation=instance)

    for membership in memberships:
        membership.delete()

# @receiver(user_logged_in)
# def lang(sender, **kwargs):
#     lang_code = kwargs['user'].fmsuser.get_langage()
#     kwargs['request'].session['django_language'] = lang_code.lower()
#     kwargs['request'].LANGUAGE_CODE = lang_code.lower()
#     activate(lang_code.lower())

class UserOrganisationMembership(UserTrackedModel):
    user = models.ForeignKey(FMSUser, related_name='memberships', null=True, blank=True)
    organisation = models.ForeignKey(OrganisationEntity, related_name='memberships', null=True, blank=True)
    contact_user = models.BooleanField(default=False)

    class Meta:
        unique_together = (("user", "organisation"),)

class ReportQuerySet(models.query.GeoQuerySet):

    def public(self):
        return self.filter(private=False, status__in=Report.REPORT_STATUS_VIEWABLE)

    def responsible(self, user):
        query = Q()

        if user.contractor or user.applicant:
            query = query | Q(contractor__in=user.work_for.all())

        if user.manager or user.leader or user.agent:
            query = query | Q(responsible_manager=user)

        return self.filter(query)

    def entity_responsible(self, user):
        query = Q()

        if user.contractor or user.applicant:
            query = query | Q(contractor__in=user.work_for.all())

        if user.agent or user.manager or user.leader:
            query = query | Q(responsible_entity=user.organisation)

        return self.filter(query)

    def entity_territory(self, organisation):
        return self.filter(postalcode__in=[zc.code for zc in organisation.zipcode_set.all()])

    def created(self):
        return self.filter(status=Report.CREATED)

    def in_progress(self):
        return self.filter(status__in=Report.REPORT_STATUS_IN_PROGRESS)

    def pending(self):
        return self.filter(Q(status=Report.CREATED) | Q(status__in=Report.REPORT_STATUS_IN_PROGRESS))

    def assigned(self):
        return self.filter(contractor__isnull=False)

    def closed(self):
        return self.filter(status__in=Report.REPORT_STATUS_CLOSED)

    def subscribed(self, user):
        return self.filter(subscriptions__subscriber=user)


class ReportManager(models.GeoManager):

    def one_week_ago(self):
        time_from = datetime.date.today() - datetime.timedelta(days=7)
        return self.get_query_set().filter(created__gt=time_from)

    def one_month_ago(self):
        time_from = datetime.date.today() - datetime.timedelta(days=30)
        return self.get_query_set().filter(created__gt=time_from)

    def created_between(self, start_date, end_date):
        return self.get_query_set().filter(created__gt=start_date, created__lt=end_date)

    def get_query_set(self):
        return ReportQuerySet(self.model) \
                .exclude(status=Report.PROCESSED, fixed_at__lt=datetime.date.today()-datetime.timedelta(30)) \
                .exclude(status=Report.DELETED) \
                .select_related('category', 'secondary_category',
                    'secondary_category__secondary_category_class',
                    'responsible_entity', 'responsible_manager', 'contractor',
                    'citizen', 'created_by')


class Report(UserTrackedModel):
    __metaclass__ = TransMeta

    # List of status
    CREATED = 1
    REFUSED = 9

    IN_PROGRESS           = 2
    MANAGER_ASSIGNED      = 4
    APPLICANT_RESPONSIBLE = 5
    CONTRACTOR_ASSIGNED   = 6
    SOLVED                = 7

    PROCESSED = 3
    DELETED   = 8

    REPORT_STATUS_SETTABLE_TO_SOLVED = (CREATED, IN_PROGRESS, MANAGER_ASSIGNED, APPLICANT_RESPONSIBLE, CONTRACTOR_ASSIGNED)
    REPORT_STATUS_IN_PROGRESS = (IN_PROGRESS, MANAGER_ASSIGNED, APPLICANT_RESPONSIBLE, CONTRACTOR_ASSIGNED, SOLVED)
    REPORT_STATUS_VIEWABLE    = (CREATED, IN_PROGRESS, MANAGER_ASSIGNED, APPLICANT_RESPONSIBLE, CONTRACTOR_ASSIGNED, PROCESSED, SOLVED)
    REPORT_STATUS_ASSIGNED    = (APPLICANT_RESPONSIBLE, CONTRACTOR_ASSIGNED)
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
    quality = models.IntegerField(choices=FMSUser.REPORT_QUALITY_CHOICES, null=True, blank=True)
    point = models.PointField(null=True, srid=31370, blank=True)
    address = models.CharField(max_length=255, verbose_name=_("Location"))
    address_number = models.CharField(max_length=255, verbose_name=_("Address Number"))
    address_number_as_int = models.IntegerField(max_length=255)
    address_regional = models.BooleanField(default=False)
    postalcode = models.CharField(max_length=4, verbose_name=_("Postal Code"))
    description = models.TextField(null=True, blank=True)
    category = models.ForeignKey('ReportMainCategoryClass', null=True, verbose_name=_("Category"), blank=True)
    secondary_category = models.ForeignKey('ReportCategory', null=True, verbose_name=_("Category"), blank=True)

    fixed_at = models.DateTimeField(null=True, blank=True)
    accepted_at = models.DateTimeField(null=True, blank=True)

    planned      = models.BooleanField(default=False)
    date_planned = models.DateTimeField(null=True, blank=True)

    hash_code = models.IntegerField(null=True, blank=True) # used by external app for secure sync, must be random generated

    citizen = models.ForeignKey(FMSUser, null=True, related_name='citizen_reports', blank=True)
    refusal_motivation = models.TextField(null=True, blank=True)
    mark_as_done_motivation = models.TextField(null=True, blank=True)
    mark_as_done_user = models.ForeignKey(FMSUser, related_name='reports_solved', null=True, blank=True)

    responsible_entity = models.ForeignKey(OrganisationEntity, related_name='reports_in_charge', null=True, blank=True)
    responsible_department = models.ForeignKey(OrganisationEntity, related_name='reports_in_department', null=True) # must be not null after migration
    ### deprecated to remove ###
    responsible_manager = models.ForeignKey(FMSUser, related_name='reports_in_charge', null=True, blank=True)
    ### deprecated to remove ###
    responsible_manager_validated = models.BooleanField(default=False)
    contractor = models.ForeignKey(OrganisationEntity, related_name='assigned_reports', null=True, blank=True)
    previous_managers = models.ManyToManyField('FMSUser',related_name='previous_reports',null=True, blank=True)

    valid = models.BooleanField(default=False)
    private = models.BooleanField(default=False)
    gravity = models.IntegerField(default=1)
    probability = models.IntegerField(default=1)
    #photo = FixStdImageField(upload_to="photos", blank=True, size=(380, 380), thumbnail_size=(66, 50))
    photo = models.FileField(upload_to="photos", blank=True)
    close_date = models.DateTimeField(null=True, blank=True)

    terms_of_use_validated = models.BooleanField(default=False)

    objects = ReportManager()

    history = HistoricalRecords()

    def get_marker(self):
        user = get_current_user()

        marker_color = "green" #default color
        if self.is_in_progress():
            marker_color = "orange"
            if user and user.is_authenticated():
                if not self.contractor == None:
                    marker_color = "orange-executed"
        elif self.is_created():
            marker_color = "red"

        if user and user.is_authenticated():
            if self.is_regional():
                return "images/reg-pin-"+marker_color+"-XS.png"
            elif self.is_pro():
                return "images/pro-pin-"+marker_color+"-XS.png"
            else:
                return "images/pin-"+marker_color+"-XS.png"
        else:
            if self.is_pro():
                return "images/pro-pin-"+marker_color+"-XS.png"
            else:
                return "images/pin-"+marker_color+"-XS.png"

    def is_regional(self):
        return self.address_regional

    def is_pro(self):
        """
        Return if the report is pro.
        This is defined by logged user when report was filled.
        """
        return self.created_by is not None

    def __unicode__(self):
        return self.display_category()

    def get_address_commune_name(self):
        return self.territorial_entity().name

    def get_number_of_subscription(self):
        return self.subscriptions.all().__len__()

    def display_category(self):
        return self.category.name + " / " + self.secondary_category.secondary_category_class.name + " : " + self.secondary_category.name

    def get_ticket_number(self):
        '''Return the report ticket as a usable string'''
        report_ticket_id = str(self.id)
        if (report_ticket_id.__len__() <= 6):
            for i in range(6-(report_ticket_id.__len__())):
                report_ticket_id = "0"+report_ticket_id;
        return report_ticket_id

    def get_ticket_as_string(self):
        '''Return the report ticket as a displayable component'''
        return "#"+self.get_ticket_number()

    def get_slug(self):
        slug_sec_cat = self.secondary_category.slug
        slug_sec_cat_class = self.secondary_category.secondary_category_class.slug
        slug_cat = self.category.slug
        slug_ent = self.responsible_entity.slug
        return "{0}-{1}-{2}-{3}".format(slug_sec_cat, slug_sec_cat_class, slug_cat, slug_ent)

    def get_absolute_url(self):
        return reverse("report_show",kwargs={'report_id':self.id,'slug': self.get_slug() })

    def get_absolute_url_pro(self):
        return reverse("report_show_pro", kwargs={'report_id':self.id,'slug': self.get_slug() })


    def get_pdf_url(self):
        return reverse('report_pdf', args=[self.id, 0])

    def get_pdf_url_pro(self):
        return reverse('report_pdf', args=[self.id, 1])

    def get_priority(self):
        return self.gravity * self.probability

    def has_at_least_one_non_confidential_comment(self):
        return ReportComment.objects.filter(report__id=self.id).filter(security_level__in=[1,2]).count() != 0

    def has_at_least_one_non_confidential_file(self):
        return ReportFile.objects.filter(report__id=self.id).filter(security_level__in=[1,2]).count() != 0

    def active_comments(self):
        return self.comments().filter(logical_deleted=False).filter(security_level=1)

    def active_files(self):
        return self.files().filter(logical_deleted=False).filter(security_level=1)

    def is_created(self):
        return self.status == Report.CREATED

    def is_refused(self):
        return self.status == Report.REFUSED

    def is_in_progress(self):
        return self.status in Report.REPORT_STATUS_IN_PROGRESS

    def is_closed(self):
        return self.status in Report.REPORT_STATUS_CLOSED

    def get_public_status_display(self):
        if self.is_created():
            return ugettext("Created")
        elif self.is_in_progress():
            return ugettext("In progress")
        else:
            return ugettext("Processed")

    def get_date_planned(self):
        if self.date_planned:
            return self.date_planned.strftime('%m%Y')
        return ""

    def thumbnail(self):
        if not self.is_created():
            user = get_current_user()
            reportImages = ReportFile.objects.filter(report_id=self.id, file_type=ReportFile.IMAGE).filter(logical_deleted=False)
            if reportImages.exists():
                if user and user.is_authenticated():
                    if not reportImages[0].is_confidential():
                        return reportImages[0].image.thumbnail.url()
                else:
                    if reportImages[0].is_public():
                        return reportImages[0].image.thumbnail.url()

    def is_markable_as_solved(self):
        return self.status in Report.REPORT_STATUS_SETTABLE_TO_SOLVED

    def comments(self):
        # return self.attachments.get_query_set().comments().filter(logical_deleted=False)
        # ==> is wrong
        return ReportComment.objects.filter(report_id=self.id).filter(logical_deleted=False)

    def files(self):
        # return self.attachments.get_query_set().files().filter(logical_deleted=False)
        # ==> is wrong
        return ReportFile.objects.filter(report_id=self.id).filter(logical_deleted=False)

    def territorial_entity(self):
        return OrganisationEntity.objects.get(zipcode__code=self.postalcode)

    def subscribe_author(self):
        user = self.created_by or self.citizen
        if not self.subscriptions.filter(subscriber=user).exists():
            subscription = ReportSubscription(subscriber=user)
            subscription.notify_creation = False # don't send notification for subscription
            self.subscriptions.add(subscription)

        # if self.id:
        #     self.create_subscriber(self.created_by or self.citizen)
        # else:
        #     # if not already created, waiting for post_save
        #     self.subscribe_author = True

    def create_subscriber(self, user):
        if not self.subscriptions.filter(subscriber=user).exists():
            self.subscriptions.add(ReportSubscription(subscriber=user))


    def trigger_updates_added(self, user=None, files=None, comment=None):
        if files or comment:
            if user != self.responsible_manager:
                ReportNotification(
                    content_template='notify-updates',
                    recipient=self.responsible_manager,
                    related=self,
                ).save(updater=user, files=files, comment=comment)

            ReportEventLog(
                report=self,
                event_type=ReportEventLog.UPDATED,
                user=user,
            ).save()

            self.save() # set updated date and updated_by

    def to_full_JSON(self):
        """
        Method used to display the whole object content as JSON structure for website
        """

        local_thumbnail = self.thumbnail()
        if (local_thumbnail == None):
            thumbValue = 'null'
        else:
            thumbValue = local_thumbnail

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
            "valid": self.valid,
            "thumb": thumbValue
        }

    def marker_detail_short(self):
        return {
            "id": self.id,
            "point": {
                "x": self.point.x,
                "y": self.point.y,
            },
            "status": self.status
        }

    def full_marker_detail_pro_JSON(self):
        local_thumbnail = self.thumbnail()
        if (local_thumbnail == None):
            thumbValue = 'null'
        else:
            thumbValue = local_thumbnail

        return {
            "id": self.id,
            "point": {
                "x": self.point.x,
                "y": self.point.y,
            },
            "category": self.display_category(),
            "address": self.address,
            "address_number": self.address_number,
            "postalcode": self.postalcode,
            "address_commune_name": self.get_address_commune_name(),
            "address_regional": self.address_regional,
            "contractor" : True if self.contractor else False,
            "date_planned" : self.get_date_planned(),
            "thumb": thumbValue,
            "is_closed": self.is_closed(),
            "citizen": not self.is_pro(),
            "priority": self.get_priority()
        }

    def full_marker_detail_JSON(self):
        local_thumbnail = self.thumbnail()
        if (local_thumbnail == None):
            thumbValue = 'null'
        else:
            thumbValue = local_thumbnail

        return {
            "id": self.id,
            "point": {
                "x": self.point.x,
                "y": self.point.y,
            },
            "category": self.display_category(),
            "address": self.address,
            "address_number": self.address_number,
            "postalcode": self.postalcode,
            "address_commune_name": self.get_address_commune_name(),
            "address_regional": self.address_regional,
            "thumb": thumbValue,
            "contractor" : True if self.contractor else False,
            "date_planned" : self.get_date_planned()
        }

    def to_JSON(self):
        """
        Method used to display the object as JSON structure for website
        """

        close_date_as_string = ""
        if (self.close_date):
            close_date_as_string = self.close_date.strftime("%Y-%m-%d %H:%M:%S")

        local_thumbnail = self.thumbnail()
        if (local_thumbnail == None):
            thumbValue = 'null'
        else:
            thumbValue = local_thumbnail

        local_citizen = self.citizen;
        if (local_citizen == None):
            citizenValue = 'false'
        else:
            citizenValue = 'true'

        return {
            "id": self.id,
            "point": {
                "x": self.point.x,
                "y": self.point.y,
            },
            "status": self.status,
            "status_label": self.get_status_display(),

            "close_date": close_date_as_string,
            "citizen": citizenValue,
            "private": self.private,
            "valid": self.valid,
            "thumb": thumbValue
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
        pro = pro report
        reg = regional report
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
            "pro": self.is_pro(),
            "reg": self.is_regional(),
            "a_d": self.address_regional,
            "v": self.valid,
            "c": self.secondary_category.id,
            "m_c": self.secondary_category.category_class.id,
            "s_c": self.secondary_category.secondary_category_class.id
        }
    class Meta:
        translate=('address',)
        #unique_together = (("point", "citizen"), ("point", "created_by"))


@receiver(pre_save, sender=Report)
def track_former_value(sender, instance, **kwargs):
    """Save former data to compare with new data and track changed values"""
    if instance.id and not kwargs['raw']:
        former_report = Report.objects.get(id=instance.id)
        instance.__former = dict((field.name, getattr(former_report, field.name)) for field in Report._meta.fields)
    else:
        instance.__former = dict((field.name, getattr(Report(), field.name)) for field in Report._meta.fields)



@receiver(pre_save,sender=Report)
def init_street_number_as_int(sender, instance, **kwargs):
    """
    Store the street number as int for further filtering (as somtimes the street number is 19H ...)
    """
    non_decimal = re.compile(r'[^\d]+')
    value_processed = non_decimal.sub('', instance.address_number)
    instance.address_number_as_int = int(value_processed)


@receiver(pre_save,sender=Report)
def init_regional_street(sender, instance, **kwargs):
    if not instance.id and not kwargs['raw']:
        if StreetSurface.objects.filter(geom__intersects=instance.point.buffer(5), administrator=StreetSurface.REGION).exists():
            instance.address_regional = True


@receiver(pre_save,sender=Report)
def report_assign_responsible(sender, instance, **kwargs):
    if not instance.responsible_entity:
        #Detect who is the responsible Manager for the given type
        if instance.created_by and hasattr(instance.created_by, 'fmsuser') and instance.created_by.fmsuser.organisation:
            # assign entity of the creator
            instance.responsible_entity = instance.created_by.fmsuser.organisation
        else:
            instance.responsible_entity = OrganisationEntity.objects.get(zipcode__code=instance.postalcode)

    if not instance.responsible_manager:
        #Detect who is the responsible Manager for the given type
        #Search the right responsible for the current organization.
        users = instance.responsible_entity.team.filter(manager=True, categories=instance.secondary_category)
        if len(users) > 0:
            instance.responsible_manager = users[0]
        else:
            raise Exception("no responsible manager found ({0} - {1})".format(instance.secondary_category, instance.responsible_entity))

@receiver(pre_save,sender=Report)
def check_planned(sender, instance, **kwargs):
    if instance.pk:
        old_report = Report.objects.get(pk=instance.pk)

        dates_exists   = True if old_report.accepted_at and instance.date_planned else False
        date_too_small = instance.date_planned.strftime('%m/%Y') < old_report.accepted_at.strftime('%m/%Y') if dates_exists else False
        date_too_big   = instance.date_planned > (old_report.accepted_at + timedelta(days=365)) if dates_exists else False

        if (not dates_exists or date_too_small or date_too_big):
            instance.planned = old_report.planned
            instance.date_planned = old_report.date_planned
    else:
        instance.planned = False
        instance.date_planned = None

@receiver(post_save, sender=Report)
def report_notify(sender, instance, **kwargs):
    """
    signal on a report to notify author and manager that the status of the report has changed
    """
    report = instance
    if not kwargs['raw']:

        ### CREATED
        if kwargs['created']:
            event_log_user = None

            if report.citizen: # and report.subscriptions.filter(subscriber=report.citizen).exists(): subscription as not been already created
                ReportNotification(
                    content_template='acknowledge-creation',
                    recipient=report.citizen,
                    related=report,
                ).save()
                event_log_user = report.citizen
            else:
                event_log_user = report.created_by

            ReportNotification(
                content_template='notify-creation',
                recipient=report.responsible_manager,
                related=report,
            ).save()

            ReportEventLog(
                report=report,
                event_type=ReportEventLog.CREATED,
                user=event_log_user,
            ).save()
        ###

        if report.__former['status'] != report.status:

            ### REFUSED
            if report.status == Report.REFUSED:
                ReportNotification(
                    content_template='notify-refused',
                    recipient=report.citizen or report.created_by,
                    related=report,
                    reply_to = report.responsible_manager.email,
                ).save()

                ReportEventLog(
                    report=report,
                    event_type=ReportEventLog.REFUSE,
                    user=report.responsible_manager,
                ).save()
            ###
            elif report.status == Report.PROCESSED:
                for subscription in report.subscriptions.all():
                    if subscription.subscriber != report.responsible_manager:
                        ReportNotification(
                            content_template='announcement-processed',
                            recipient=subscription.subscriber,
                            related=report,
                            reply_to=report.responsible_manager.email,
                        ).save()

                ReportEventLog(
                    report=report,
                    event_type=ReportEventLog.CLOSE,
                    user=report.responsible_manager
                ).save()

            elif report.__former['status'] == Report.CREATED and report.status != Report.REFUSED:
                # created => in progress: published by manager
                # for subscription in report.subscriptions.all():
                if report.subscriptions.filter(subscriber=report.created_by or report.citizen).exists():
                    ReportNotification(
                        content_template='notify-validation',
                        recipient=report.created_by or report.citizen,
                        # recipient=subscription.subscriber,
                        related=report,
                        reply_to=report.responsible_manager.email,
                    ).save()

                ReportEventLog(
                    report=report,
                    event_type=ReportEventLog.VALID,
                    user=report.responsible_manager
                ).save()

            ### SOLVED
            elif report.status == Report.SOLVED:
                ReportNotification(
                    content_template='mark-as-done',
                    recipient=report.responsible_manager,
                    related=report,
                ).save()

                ReportEventLog(
                    report=report,
                    event_type=ReportEventLog.SOLVE_REQUEST,
                    user=report.modified_by
                ).save()
            ###

            if report.__former['contractor'] != report.contractor:

                if report.contractor:
                    #Applicant responsible
                    for recipient in report.contractor.workers.all():
                        ReportNotification(
                            content_template='notify-affectation',
                            recipient=recipient,
                            related=report,
                            reply_to=report.responsible_manager.email
                        ).save(old_responsible=report.responsible_manager)

                    if report.contractor.applicant:
                        for subscription in report.subscriptions.all():
                            ReportNotification(
                                content_template='announcement-affectation',
                                recipient=subscription.subscriber,
                                related=report,
                                reply_to=report.responsible_manager.email,
                            ).save(old_responsible=report.responsible_manager)

                    ReportEventLog(
                        report=report,
                        event_type=(ReportEventLog.APPLICANT_ASSIGNED if report.status == Report.APPLICANT_RESPONSIBLE else ReportEventLog.CONTRACTOR_ASSIGNED),
                        related_new=report.contractor
                    ).save()

                # if report.__former['contractor']:
                #     for recipient in report.__former['contractor'].workers.all():
                #         ReportNotification(
                #             content_template='notify-deallocate',
                #             recipient=recipient,
                #             related=report,
                #             reply_to=report.responsible_manager.email
                #         ).save(old_responsible=report.responsible_manager)




        if report.__former['responsible_manager'] != report.responsible_manager:
            # automatic subscription for new responsible manager
            if not ReportSubscription.objects.filter(report=instance, subscriber=report.responsible_manager).exists():
                subscription = ReportSubscription(report=instance, subscriber=report.responsible_manager)
                subscription.notify_creation = False # don't send notification for subscription
                subscription.save()

            if report.status != Report.CREATED:
                ReportNotification(
                    content_template='notify-affectation',
                    recipient=report.responsible_manager,
                    related=report,
                ).save(old_responsible=report.__former['responsible_manager'])

                ReportEventLog(
                    report=report,
                    event_type=ReportEventLog.MANAGER_ASSIGNED,
                    user=report.responsible_manager
                ).save()


                if report.__former['responsible_entity'] != report.responsible_entity:
                    for subscription in report.subscriptions.all():
                        if subscription.subscriber != report.responsible_manager:
                            ReportNotification(
                                content_template='announcement-affectation',
                                recipient=subscription.subscriber,
                                related=report,
                                reply_to=report.responsible_manager.email,
                            ).save(old_responsible=report.__former['responsible_manager'])

                    ReportEventLog(
                        report=report,
                        event_type=ReportEventLog.ENTITY_ASSIGNED,
                        user=report.responsible_manager
                    ).save()

        # Report planned
        if report.__former['date_planned'] != report.date_planned:
            for subscription in report.subscriptions.all():
                if subscription.subscriber != report.responsible_manager:
                    ReportNotification(
                        content_template='notify-planned',
                        recipient=subscription.subscriber,
                        related=report,
                        reply_to=report.responsible_manager.email,
                    ).save(old_responsible=report.__former['responsible_manager'])

            if not report.__former['planned']:
                ReportEventLog(
                    report=report,
                    event_type=ReportEventLog.PLANNED
                ).save()
            else:
                ReportEventLog(
                    report=report,
                    event_type=ReportEventLog.PLANNED_CHANGE
                ).save()

class ReportAttachmentQuerySet(models.query.QuerySet):
    def files(self):
        qs = self.select_related('reportfile')
        qs.cast_to = 'file'
        return qs

    def comments(self):
        qs = self.select_related('reportcomment')
        qs.cast_to = 'comment'
        return qs

    def _clone(self, *args, **kwargs):
        qs =  super(ReportAttachmentQuerySet, self)._clone(*args, **kwargs)
        if hasattr(self, 'cast_to'):
            qs.cast_to = self.cast_to
        return qs

    def iterator(self):
        iter = super(ReportAttachmentQuerySet, self).iterator()
        if not hasattr(self, 'cast_to'):
            for obj in iter:
                yield obj
        for obj in iter:
            if self.cast_to == 'file' and hasattr(obj, 'reportfile'):
                yield obj.reportfile
            if self.cast_to == 'comment' and hasattr(obj, 'reportcomment'):
                yield obj.reportcomment


class ReportAttachmentManager(models.Manager):
    use_for_related_fields = True
    def get_query_set(self):
        return ReportAttachmentQuerySet(self.model)


class ReportAttachment(UserTrackedModel):

    PUBLIC = 1
    PRIVATE = 2
    CONFIDENTIAL = 3

    REPORT_ATTACHMENT_SECURITY_LEVEL_CHOICES = (
        (PUBLIC,_("Public")),
        (PRIVATE,_("Private")),
        (CONFIDENTIAL,_("Confidential"))
    )

    logical_deleted = models.BooleanField(default=False)
    security_level = models.IntegerField(choices=REPORT_ATTACHMENT_SECURITY_LEVEL_CHOICES, default=PRIVATE, null=False)
    report = models.ForeignKey(Report, related_name="attachments")

    objects = ReportAttachmentManager()

    #is_validated = models.BooleanField(default=False)
    #is_visible = models.BooleanField(default=False)

    #def is_deleted(self):
    #    '''Returns true if the attachment is deleted'''
    #    return self.logical_deleted

    def is_confidential_visible(self):
        '''visible when not confidential'''
        current_user = get_current_user().fmsuser
        #return (self.is_visible and (current_user.contractor or current_user.applicant) or (current_user.manager or current_user.leader))
        return (self.security_level != ReportAttachment.CONFIDENTIAL and (current_user.contractor or current_user.applicant) or (current_user.manager or current_user.leader))

    def is_citizen_visible(self):
        '''Visible when not confidential and public'''
        #return self.is_validated and self.is_visible
        return self.security_level == ReportAttachment.PUBLIC

    def is_public(self):
        '''Is the annex public?'''
        return self.security_level == ReportAttachment.PUBLIC
    def is_private(self):
        '''Is the annex private?'''
        return self.security_level == ReportAttachment.PRIVATE
    def is_confidential(self):
        '''Is the annex confidential?'''
        return self.security_level == ReportAttachment.CONFIDENTIAL

    def get_display_name(self):
        if (not self.created_by or self.created_by.first_name == None and self.created_by.last_name == None):
             return _('ANONYMOUS')
        else:
             return self.created_by.first_name+' '+self.created_by.last_name


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
    #def _save_FIELD_file(self, field, filename, raw_contents, save=True):
    #   import pdb
    #   pdb.set_trace()
    #   original_upload_to = field.upload_to
    #   field.upload_to = '%s/%s' % (field.upload_to, self.user.username)
    #   super(Patch, self)._save_FIELD_file(field, filename, raw_contents, save)
    #field.upload_to = original_upload_to
    #def generate_filename(instance, old_filename):
    #    import pdb
    #    pdb.set_trace()
    #    extension = os.path.splitext(old_filename)[1]
    #    filename = old_filename+'_'+str(time.time()) + extension
    #    return 'files/' + filename
    def move_to(instance, filename):
        path = unicode("files/{0}/{1:02d}/{2:02d}/{3}").format(
            instance.report.created.year,
            instance.report.created.month,
            instance.report.id,
            unicode(filename))
        return path

    file = models.FileField(upload_to=move_to, blank=True)
    image = FixStdImageField(upload_to=move_to, blank=True, size=(1200, 800), thumbnail_size=(80, 120))
    #file = models.FileField(upload_to=generate_filename)
    file_type = models.IntegerField(choices=attachment_type)
    title = models.TextField(max_length=250, null=True, blank=True)
    file_creation_date= models.DateTimeField(blank=False, null=True)


    #def file(self):
    #    if (self.attach == None):
    #        return self.image
    #    else:
    #        return self.attach

    def is_pdf(self):
        return self.file_type == ReportFile.PDF
    def is_word(self):
        return self.file_type == ReportFile.WORD
    def is_excel(self):
        return self.file_type == ReportFile.EXCEL
    def is_image(self):
        return self.file_type == ReportFile.IMAGE
    def is_document(self):
        return self.is_pdf() or self.is_word() or self.is_excel()



@receiver(pre_save, sender=ReportFile)
def init_file_type(sender,instance,**kwargs):
    if instance.file_type:
        return
    content_type = instance.file.file.content_type

    if content_type == "application/pdf":
        instance.file_type = ReportFile.PDF
    elif content_type == 'application/vnd.ms-excel' or content_type == 'application/vnd.oasis.opendocument.spreadsheet':
        instance.file_type = ReportFile.EXCEL
    elif content_type == 'image/png' or content_type == 'image/jpeg':
        instance.file_type = ReportFile.IMAGE
    else:
        instance.file_type = ReportFile.WORD

    if instance.file_type == ReportFile.IMAGE:
        instance.image.save(instance.file.name.split('?')[0], instance.file, save=False)


# @receiver(post_save, sender=ReportFile)
# def init_report_overview(sender,instance,**kwargs):
#     if not instance.report.photo:
#         if not instance.logical_deleted and instance.is_public():
#             instance.report = instance.image
#     elif instance.report.photo == instance.image
#         if instance.logical_deleted or not instance.is_public():
#             public_images = instance.files.filter(file_type=ReportFile.IMAGE, logical_deleted=False, security_level=ReportAttachment.PUBLIC)
#             if public_images.exists():
#                 instance.report = public_images[0]


class ReportSubscription(models.Model):
    """
    Report Subscribers are notified when there's an update to an existing report.
    """
    report = models.ForeignKey(Report, related_name="subscriptions")
    subscriber = models.ForeignKey(FMSUser, null=False)
    class Meta:
        unique_together = (("report", "subscriber"),)

@receiver(post_save,sender=ReportSubscription)
def notify_report_subscription(sender, instance, **kwargs):
    if not kwargs['raw'] and kwargs['created'] and (not hasattr(instance, 'notify_creation') or instance.notify_creation):
        report = instance.report
        notifiation = ReportNotification(
            content_template='notify-subscription',
            recipient=instance.subscriber,
            related=report,
            reply_to=report.responsible_manager.email,
        )
        notifiation.save()


class ReportMainCategoryClass(UserTrackedModel):
    __metaclass__ = TransMeta
    help_text = """
    Manage the category container list (see the report form). Allow to group categories.
    """

    name = models.CharField(verbose_name=_('Name'), max_length=100)
    slug = models.SlugField(verbose_name=_('Slug'), max_length=100)

    hint = models.ForeignKey('ReportCategoryHint', null=True)

    def __unicode__(self):
        return self.name

    @staticmethod
    def listToJSON(list_of_elements):
        list_of_elements_as_json = []
        for current_element in list_of_elements:
            d = {}
            d['id'] = getattr(current_element, 'id')
            d['name_en'] = getattr(current_element, 'name_fr')
            d['name_fr'] = getattr(current_element, 'name_fr')
            d['name_nl'] = getattr(current_element, 'name_nl')
            list_of_elements_as_json.append(d)
        return simplejson.dumps(list_of_elements_as_json)

    class Meta:
        verbose_name = "category group"
        verbose_name_plural = "category groups"
        translate = ('name', 'slug')

pre_save.connect(autoslug_transmeta('name', 'slug'), weak=False, sender=ReportMainCategoryClass)


class ReportSecondaryCategoryClass(UserTrackedModel):
    __metaclass__ = TransMeta
    help_text = """
    Manage the category container list (see the report form). Allow to group categories.
    """

    name = models.CharField(verbose_name=_('Name'), max_length=100)
    slug = models.SlugField(verbose_name=_('Slug'), max_length=100)

    def __unicode__(self):
        return self.name

    @staticmethod
    def listToJSON(list_of_elements):
        list_of_elements_as_json = []
        for current_element in list_of_elements:
            d = {}
            d['id'] = getattr(current_element, 'id')
            d['name_en'] = getattr(current_element, 'name_fr')
            d['name_fr'] = getattr(current_element, 'name_fr')
            d['name_nl'] = getattr(current_element, 'name_nl')
            list_of_elements_as_json.append(d)
        return simplejson.dumps(list_of_elements_as_json)

    class Meta:
        verbose_name = "category group"
        verbose_name_plural = "category groups"
        translate = ('name', 'slug')

pre_save.connect(autoslug_transmeta('name', 'slug'), weak=False, sender=ReportSecondaryCategoryClass)



class ReportCategory(UserTrackedModel):
    __metaclass__ = TransMeta
    help_text = """
    Manage the report categories list (see the report form).
    When a category is selected in the website form, the hint field is loaded in ajax and displayed  in the form.
    """

    name = models.CharField(verbose_name=_('Name'), max_length=100)
    slug = models.SlugField(verbose_name=_('Slug'), max_length=100)

    category_class = models.ForeignKey(ReportMainCategoryClass, related_name="categories", verbose_name=_('Category group'), help_text="The category group container")
    secondary_category_class = models.ForeignKey(ReportSecondaryCategoryClass, related_name="categories", verbose_name=_('Category group'), help_text="The category group container")
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
            d['n_en'] = getattr(current_element, 'name_fr')
            d['n_fr'] = getattr(current_element, 'name_fr')
            d['n_nl'] = getattr(current_element, 'name_nl')
            d['m_c_id'] = getattr(getattr(current_element, 'category_class'),'id')

            is_it_public = getattr(current_element, 'public')
            if is_it_public:
                d['p'] = 1
            else:
                d['p'] = 0

            #Optimize data transfered removing duplicates on main class names
            #m_c_n_en_value = getattr(getattr(current_element, 'category_class'), 'name_en')
            m_c_n_en_value = getattr(getattr(current_element, 'category_class'), 'name_fr')
            if is_it_public or not prev_d['m_c_n_en'] == m_c_n_en_value:
                prev_d['m_c_n_en'] = d['m_c_n_en'] = m_c_n_en_value
            #m_c_n_fr_value = getattr(getattr(current_element, 'category_class'), 'name_fr')
            m_c_n_fr_value = getattr(getattr(current_element, 'category_class'), 'name_fr')
            if is_it_public or not prev_d['m_c_n_fr'] == m_c_n_fr_value:
                prev_d['m_c_n_fr'] = d['m_c_n_fr'] = m_c_n_fr_value

            #m_c_n_nl_value = getattr(getattr(current_element, 'category_class'), 'name_nl')
            m_c_n_nl_value = getattr(getattr(current_element, 'category_class'), 'name_nl')
            if is_it_public or not prev_d['m_c_n_nl'] == m_c_n_nl_value:
                prev_d['m_c_n_nl'] = d['m_c_n_nl'] = m_c_n_nl_value
            d['s_c_id'] = getattr(getattr(current_element, 'secondary_category_class'),'id')

            #Optimize data transfered removing duplicates on main class names
            #s_c_n_en_value = getattr(getattr(current_element, 'secondary_category_class'), 'name_en')
            s_c_n_en_value = getattr(getattr(current_element, 'secondary_category_class'), 'name_fr')
            if is_it_public or not prev_d['s_c_n_en'] == s_c_n_en_value:
                prev_d['s_c_n_en'] = d['s_c_n_en'] = s_c_n_en_value
            #s_c_n_fr_value = getattr(getattr(current_element, 'secondary_category_class'), 'name_fr')
            s_c_n_fr_value = getattr(getattr(current_element, 'secondary_category_class'), 'name_fr')
            if is_it_public or not prev_d['s_c_n_fr'] == s_c_n_fr_value:
                prev_d['s_c_n_fr'] = d['s_c_n_fr'] = s_c_n_fr_value
            #s_c_n_nl_value = getattr(getattr(current_element, 'secondary_category_class'), 'name_nl')
            s_c_n_nl_value = getattr(getattr(current_element, 'secondary_category_class'), 'name_nl')
            if is_it_public or not prev_d['s_c_n_nl'] == s_c_n_nl_value:
                prev_d['s_c_n_nl'] = d['s_c_n_nl'] = s_c_n_nl_value


            list_of_elements_as_json.append(d)
        return simplejson.dumps(list_of_elements_as_json)

    class Meta:
        verbose_name = "category"
        verbose_name_plural = "categories"
        translate = ('name', 'slug')

pre_save.connect(autoslug_transmeta('name', 'slug'), weak=False, sender=ReportCategory)



class ReportCategoryHint(models.Model):
    __metaclass__ = TransMeta
    label = models.TextField(verbose_name=_('Label'), blank=False, null=False)
    class Meta:
        translate = ('label', )


# class ManagerCategories(UserTrackedModel):
#     help_text="""
#     Defines the relation of a user and a category
#     """
#     category = models.ForeignKey(ReportCategory)
#     user = models.ForeignKey(FMSUser)


class ReportNotification(models.Model):
    recipient = models.ForeignKey(FMSUser, related_name="notifications")
    sent_at = models.DateTimeField(auto_now_add=True)
    success = models.BooleanField()
    error_msg = models.TextField()
    content_template = models.CharField(max_length=40)
    reply_to = models.CharField(max_length=200,null=True)

    related = generic.GenericForeignKey('related_content_type', 'related_object_id')
    related_content_type = models.ForeignKey(ContentType)
    related_object_id = models.PositiveIntegerField()


    def save(self, *args, **kwargs):
        old_responsible=None
        updater=None
        comment=None
        files=None
        if 'old_responsible' in kwargs:
            old_responsible = kwargs['old_responsible']
            del kwargs['old_responsible']
        if 'updater' in kwargs:
            updater = kwargs['updater']
            del kwargs['updater']
        if 'comment' in kwargs:
            comment = kwargs['comment']
            del kwargs['comment']
        if 'files' in kwargs:
            files = kwargs['files']
            del kwargs['files']

        if not self.recipient.email:
            self.error_msg = "No email recipient"
            self.success = False
            return

        try:
            recipients = (self.recipient.email,)


            template = MailNotificationTemplate.objects.get(name=self.content_template)

            comment = comment.text if comment else ''
            subject, html, text = transform_notification_template(template, self.related, self.recipient, old_responsible=old_responsible, updater=updater, comment=comment)

            if self.reply_to:
                msg = EmailMultiAlternatives(subject, text, settings.DEFAULT_FROM_EMAIL, recipients, headers={"Reply-To":self.reply_to})
            else:
                msg = EmailMultiAlternatives(subject, text, settings.DEFAULT_FROM_EMAIL, recipients)

            if html:
                msg.attach_alternative(html, "text/html")

            if files:
                for f in files:
                    if f.file_type == ReportFile.IMAGE:
                        msg.attach(f.file.name, f.file.read(), 'image/png')


            msg.send()
            self.success = True
            super(ReportNotification, self).save(*args, **kwargs)
        except Exception as e:
            self.success = False
            self.error_msg = str(e)
            # logger.error('Mail not send !')
            # logger.error(e)
            super(ReportNotification, self).save(*args, **kwargs)
            raise



class ReportEventLog(models.Model):

    # List of event types
    REFUSE = 1
    CLOSE = 2
    SOLVE_REQUEST = 3
    MANAGER_ASSIGNED = 4
    MANAGER_CHANGED = 5
    VALID = 6
    ENTITY_ASSIGNED = 7
    ENTITY_CHANGED = 8
    CONTRACTOR_ASSIGNED = 9
    CONTRACTOR_CHANGED = 10
    APPLICANT_ASSIGNED =11
    APPLICANT_CHANGED = 12
    APPLICANT_CONTRACTOR_CHANGE = 13
    CREATED = 14
    UPDATED = 15
    UPDATE_PUBLISHED = 16
    PLANNED = 17
    PLANNED_CHANGE = 18
    EVENT_TYPE_CHOICES = (
        (REFUSE,_("Refuse")),
        (CLOSE,_("Close")),
        (SOLVE_REQUEST,_("Mark as Done")),
        (MANAGER_ASSIGNED,_("Manager assinged")),
        #(MANAGER_CHANGED,_("Manager changed")),
        (VALID,_("Valid")),
        (ENTITY_ASSIGNED, _('Organisation assinged')),
        #(ENTITY_CHANGED, _('Organisation changed')),
        (CONTRACTOR_ASSIGNED,_('Contractor assinged')),
        (CONTRACTOR_CHANGED,_('Contractor changed')),
        (APPLICANT_ASSIGNED,_('Applicant assinged')),
        (APPLICANT_CHANGED,_('Applicant changed')),
        (APPLICANT_CONTRACTOR_CHANGE,_('Applicant contractor changed')),
        (CREATED,_("Created")),
        (UPDATED,_("Updated")),
        (UPDATE_PUBLISHED,_("Update published")),
        (PLANNED,_("Planned")),
        (PLANNED_CHANGE,_("Planned change")),
    )
    EVENT_TYPE_TEXT = {
        REFUSE: _("Report refused by {user}"),
        CLOSE: _("Report closed by {user}"),
        SOLVE_REQUEST: _("Report pointed as solved"),
        MANAGER_ASSIGNED: _("Report as been assigned to {related_new}"),
        #MANAGER_CHANGED: _("Report as change manager from {related_old} to {related_new}"),
        VALID: _("Report has been approved by {user}"),
        ENTITY_ASSIGNED: _('{related_new} is responsible for the report'),
        #ENTITY_CHANGED: _('{related_old} give responsibility to {related_new}'),
        APPLICANT_ASSIGNED:_('Applicant {related_new} is assigned to the report'),
        APPLICANT_CHANGED:_('Applicant changed from {related_old} to {related_new}'),
        CONTRACTOR_ASSIGNED:_('Contractor {related_new} is assigned to the report'),
        CONTRACTOR_CHANGED:_('Contractor changed from {related_old} to {related_new}'),
        APPLICANT_CONTRACTOR_CHANGE:_('Applicant contractor change from {related_old} to {related_new}'),
        CREATED: _("Report created by {user}"),
        UPDATED: _("Report updated by {user}"),
        UPDATE_PUBLISHED: _("Informations published by {user}"),
        PLANNED: _("Report planned to {date_planned}"),
        PLANNED_CHANGE: _("Report planned change"),
    }

    PUBLIC_VISIBLE_TYPES = [REFUSE, CLOSE, VALID, APPLICANT_ASSIGNED, APPLICANT_CHANGED, ENTITY_ASSIGNED, CREATED, APPLICANT_CONTRACTOR_CHANGE]
    PRO_VISIBLE_TYPES = PUBLIC_VISIBLE_TYPES + [MANAGER_ASSIGNED, CONTRACTOR_ASSIGNED, CONTRACTOR_CHANGED, SOLVE_REQUEST, UPDATED, PLANNED, PLANNED_CHANGE]
    PRO_VISIBLE_TYPES.remove(ENTITY_ASSIGNED)

    event_type = models.IntegerField(choices=EVENT_TYPE_CHOICES)

    report = models.ForeignKey(Report, related_name='activities')
    user = models.ForeignKey(User, related_name='activities', null=True)
    organisation = models.ForeignKey(OrganisationEntity, related_name='activities')
    event_at = models.DateTimeField(auto_now_add=True)

    status_old = models.IntegerField(choices=Report.REPORT_STATUS_CHOICES, null=True)
    status_new = models.IntegerField(choices=Report.REPORT_STATUS_CHOICES, null=True)

    related_old = generic.GenericForeignKey('related_content_type', 'related_old_id')
    related_new = generic.GenericForeignKey('related_content_type', 'related_new_id')

    related_old_id = models.PositiveIntegerField(null=True)
    related_new_id = models.PositiveIntegerField(null=True)

    related_content_type = models.ForeignKey(ContentType, null=True)

    value_old = models.CharField(max_length=255, null=True)

    class Meta:
        ordering = ['event_at',]

    def __unicode__(self):
        user_to_display = _("a citizen")

        if self.user:
            if self.user.fmsuser.is_citizen():
                user_to_display = self.user.get_full_name() or self.user

            if self.user.fmsuser.is_pro():
                user_to_display = u'%s %s' %(self.user.fmsuser.get_organisation(), self.user.get_full_name() or self.user)

        return self.EVENT_TYPE_TEXT[self.event_type].format(
            user=user_to_display,
            organisation=self.organisation,
            related_new=self.related_new,
            date_planned=self.value_old
        )

    def get_public_activity_text (self):
        user_to_display = _("a citizen")

        if self.user:
            if self.user.fmsuser.is_citizen():
                user_to_display = _("a citizen")

            if self.user.fmsuser.is_pro():
                user_to_display = self.user.fmsuser.get_organisation()

        return self.EVENT_TYPE_TEXT[self.event_type].format(
            user=user_to_display,
            organisation=self.organisation,
            related_new=self.related_new
        )

    def get_status (self):
        return self.EVENT_TYPE_CHOICES[self.event_type][1]

    def is_public_visible(self):
        return self.event_type in ReportEventLog.PUBLIC_VISIBLE_TYPES

    def is_pro_visible(self):
        return self.event_type in ReportEventLog.PRO_VISIBLE_TYPES


@receiver(pre_save, sender=ReportEventLog)
def eventlog_init_values(sender, instance, **kwargs):
    if instance.report:

        if instance.status_new == None:
            instance.status_new = instance.report.status

        if instance.status_old == None and hasattr(instance.report, '__former'):
            instance.status_old = instance.report.__former["status"]

        if not hasattr(instance, "organisation"):
            instance.organisation = instance.report.responsible_entity

        if not hasattr(instance, "user"):
            instance.user = instance.report.modified_by

        if hasattr(instance.report, '__former') and instance.report.date_planned != instance.report.__former["date_planned"]:
            instance.value_old = instance.report.get_date_planned()


# class Zone(models.Model):
    # __metaclass__ = TransMeta
    #
    # name=models.CharField(max_length=100)
    # creation_date = models.DateTimeField(auto_now_add=True)
    # update_date = models.DateTimeField(auto_now=True)
    # commune = models.ForeignKey(Commune)
    #
    # class Meta:
        # translate = ('name', )


# class FMSUserZone(models.Model):
    # user = models.ForeignKey(FMSUser)
    # zone = models.ForeignKey(Zone)
    # creation_date = models.DateTimeField(auto_now_add=True, blank=True,default=dt.now())
    # update_date = models.DateTimeField(auto_now=True, blank=True,default=dt.now())


class ZipCodeManager(models.Manager):
    def get_query_set(self):
        return super(ZipCodeManager, self).get_query_set().select_related('commune')


class ParticipateZipCodeManager(ZipCodeManager):
    def get_query_set(self):
        return super(ParticipateZipCodeManager, self).get_query_set().filter(commune__active=True)


class ZipCode(models.Model):
    __metaclass__ = TransMeta

    commune = models.ForeignKey(OrganisationEntity)
    code = models.CharField(max_length=4)
    name = models.CharField(max_length=100)
    hide = models.BooleanField()

    objects = ZipCodeManager()
    participates = ParticipateZipCodeManager()

    class Meta:
        translate = ('name', )


class FaqEntry(models.Model):
    __metaclass__ = TransMeta

    q = models.CharField(_('Question'), max_length=200)
    a = models.TextField(_('Answere'), blank=True, null=True)
    slug = models.SlugField(null=True, blank=True)
    order = models.IntegerField(null=True, blank=True)

    class Meta:
        ordering = ["order"]
        verbose_name_plural = 'faq entries'
        translate = ('q', 'a')

@receiver(pre_save,sender=FaqEntry)
def save(sender, instance, **kwargs):
    if instance.order == None:
        instance.order = FaqEntry.objects.all().aggregate(models.Max('order'))['order__max'] + 1


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



# to import fresh datas:
#
# ogr2ogr -a_srs EPSG:31370 -overwrite -f "PostgreSQL" -nln public.urbis \
# PG:"host=localhost user=xxx password=xxx dbname=fixmystreet" \
# OCI:"xxx/xxx@( \
#     DESCRIPTION = \
#         (ADDRESS_LIST = (ADDRESS = (PROTOCOL = TCP)(HOST = xxx)(PORT = 1521))) \
#         (CONNECT_DATA = (SID =ORAPRD01)) \
#     ):URBIS_DIFF.URB_A_SS"


class StreetSurface(models.Model):
    REGION = 'REG'
    ADMINISTRATORS = ((REGION, 'Region'), )
    LEVELS = (
        ("+", "up"),
        ("=", "reference"),
        ("-", "down"),
        ("0", "not defined")
    )
    TYPES = (
        ("A", "access ramp"),
        ("G", "gallery"),
        ("I", "crossroads"),
        ("L", "local road"),
        ("P", "place"),
        ("S", "section")
    )

    urbis_id = models.IntegerField(null=True, blank=True)
    pw_id = models.IntegerField(null=True, blank=True)
    ssft = models.CharField(blank=True, max_length=1, choices=TYPES)
    sslv = models.CharField(blank=True, max_length=1, choices=LEVELS)
    version_id = models.IntegerField(null=True, blank=True)
    administrator = models.CharField(blank=True, null=True, max_length=3, choices=ADMINISTRATORS)
    geom = models.GeometryField(null=False, srid=31370, blank=False)

    objects = models.GeoManager()


class MailNotificationTemplate(models.Model):
    name = models.CharField(max_length=50, help_text="Tehnical name")
    __metaclass__= TransMeta
    content = models.TextField(blank=True, verbose_name="Content")
    title = models.CharField(max_length=100, blank=True, verbose_name="Subject")

    class Meta:
        translate = ('content', 'title')


