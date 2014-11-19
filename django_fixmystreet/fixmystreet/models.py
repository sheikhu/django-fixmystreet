import json
from exceptions import Exception
import logging
import re
import datetime
import requests

from datetime import timedelta

from django.db.models.signals import pre_save, post_save, pre_delete
from django.dispatch import receiver
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext, string_concat
from django.utils.translation import ugettext_lazy as _, pgettext_lazy
from django.contrib.auth.models import User
from django.contrib.sites.models import Site

from django.contrib.gis.db import models
from django.contrib.gis.db.models import Q
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.utils.http import urlencode

from transmeta import TransMeta
from django_extensions.db.models import TimeStampedModel
from simple_history.models import HistoricalRecords
from ckeditor.fields import RichTextField

from django_fixmystreet.fixmystreet.utils import FixStdImageField, get_current_user, autoslug_transmeta, transform_notification_template, sign_message


logger = logging.getLogger(__name__)


class UserTrackedModel(TimeStampedModel):
    created_by = models.ForeignKey('FMSUser', null=True, editable=False, related_name='%(class)s_created')
    modified_by = models.ForeignKey('FMSUser', null=True, editable=False, related_name='%(class)s_modified')

    def save(self, *args, **kwargs):
        user = get_current_user()
        if user and user.is_authenticated():
            self.modified_by = user
            if not self.id:
                self.created_by = user
            self._history_user = user  # used by simple_history
        else:
            self.modified_by = None

        super(UserTrackedModel, self).save(*args, **kwargs)

    class Meta:
        abstract = True


User._meta.get_field_by_name('email')[0]._unique = True
User._meta.get_field_by_name('email')[0].null = True
User._meta.get_field_by_name('email')[0].max_length = 75
User._meta.get_field_by_name('username')[0].max_length = 75
User._meta.get_field_by_name('password')[0].default = '!'
User._meta.get_field_by_name('is_active')[0].default = False


class FMSUserManager(models.Manager):
    def get_query_set(self):
        return FMSUserQuerySet(self.model)


class FMSUserQuerySet(models.query.QuerySet):
    def is_pro(self):
        return self.filter(Q(agent=True) | Q(manager=True) | Q(leader=True) | Q(applicant=True) | Q(contractor=True))


class FMSUser(User):
    AGENT = "agent"
    MANAGER = "manager"
    LEADER = "leader"
    CONTRACTOR = "contractor"
    APPLICANT = "applicant"

    # user types ordered by weight
    USER_TYPES = (
        LEADER,
        MANAGER,
        AGENT,
        APPLICANT,
        CONTRACTOR,
    )

    # List of qualities
    RESIDENT = 1
    TRADE = 2
    SYNDICATE = 3
    ASSOCIATION = 4
    OTHER = 5
    REPORT_QUALITY_CHOICES = (
        (RESIDENT, _("Resident")),
        (TRADE, _("Trade")),
        (SYNDICATE, _("Syndicate")),
        (ASSOCIATION, _("Association")),
        (OTHER, _("Other"))
    )

    objects = FMSUserManager()

    telephone = models.CharField(max_length=20, null=True)
    last_used_language = models.CharField(max_length=10, null=True, default="FR")
    quality = models.IntegerField(choices=REPORT_QUALITY_CHOICES, null=True, blank=True)

    agent = models.BooleanField(default=False)
    manager = models.BooleanField(default=False)
    leader = models.BooleanField(default=False)

    applicant = models.BooleanField(default=False)
    contractor = models.BooleanField(default=False)

    logical_deleted = models.BooleanField(default=False)

    organisation = models.ForeignKey(
        'OrganisationEntity',
        related_name='team',
        null=True,
        blank=True,
        verbose_name=_("Entity"),
        limit_choices_to={"type__in": ('R', 'C')}
    )  # organisation that can be responsible of reports

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
            self._history_user = user  # used by simple_history
        else:
            self.modified_by = None

        super(FMSUser, self).save(*args, **kwargs)

    def display_category(self):
        return (
            self.secondary_category.secondary_category_class.name +
            " / " + self.category.name +
            " : " + self.secondary_category.name
        )

    def get_display_name(self):
        if not self.first_name and not self.last_name:
            return _('A citizen')
        else:
            return self.get_full_name()

    def get_organisation(self):
        '''Return the user organisation and its dependency in case of contractor'''
        if self.organisation:
            return self.organisation
        elif self.contractor or self.applicant:
            return u", ".join([unicode(membership.organisation) for membership in UserOrganisationMembership.objects.filter(user=self)])

    def is_pro(self):
        return self.agent or self.manager or self.leader or self.applicant or self.contractor or self.organisation

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

    def get_user_type_list(self):
        result = []
        for user_type in self.USER_TYPES:
            if getattr(self, user_type, False):
                result.append(user_type)
        return result

    def is_user_type(self, user_type):
        return getattr(self, user_type, False)

    def organisations_list(self):
        result = []
        memberships = self.memberships.all()
        for membership in memberships:
            result.append(membership.organisation)
        return result

    def get_quality(self):
        if self.quality:
            return dict(self.REPORT_QUALITY_CHOICES)[self.quality]

    def toJSON(self):
        d = {}
        d['id'] = getattr(self, 'id')
        d['first_name'] = getattr(self, 'first_name')
        d['last_name'] = getattr(self, 'last_name')
        d['email'] = getattr(self, 'email')
        d['last_used_language'] = getattr(self, 'last_used_language')
        d['organisation'] = getattr(self.get_organisation(), 'id', None)
        return json.dumps(d)

    def get_absolute_url(self):
        return reverse("edit_user", kwargs={'user_id': self.id})

    def __unicode__(self):
        return self.get_display_name()

    class Meta:
        ordering = ['last_name']

@receiver(pre_save, sender=FMSUser)
def populate_username(sender, instance, **kwargs):
    """populate username with email"""
    if instance.email and instance.username != instance.email:
        instance.username = instance.email


class OrganisationEntity(UserTrackedModel):
    REGION = 'R'
    COMMUNE = 'C'
    SUBCONTRACTOR = 'S'
    APPLICANT = 'A'
    DEPARTMENT = 'D'
    NEIGHBOUR_HOUSE = 'N'

    ENTITY_TYPE = (
        (REGION, _('Region')),
        (COMMUNE, _('Commune')),
        (SUBCONTRACTOR, _('Subcontractor')),
        (APPLICANT, _('Applicant')),
        (DEPARTMENT, _('Department')),
        (NEIGHBOUR_HOUSE, _('Neighbour house')),
    )
    ENTITY_GROUP_REQUIRED_ROLE = {
        SUBCONTRACTOR: 'contractor',
        DEPARTMENT: 'manager',
        NEIGHBOUR_HOUSE: 'agent',
    }

    ENTITY_TYPE_GROUP = (
        (SUBCONTRACTOR, _('Subcontractor')),
        (DEPARTMENT, _('Department')),
        (NEIGHBOUR_HOUSE, _('Neighbour house')),
    )

    __metaclass__ = TransMeta
    name = models.CharField(verbose_name=_('Name'), max_length=100, null=False)
    slug = models.SlugField(verbose_name=_('Slug'), max_length=100)
    phone = models.CharField(max_length=32)
    email = models.EmailField(null=True, blank=True)

    active = models.BooleanField(default=False)

    type = models.CharField(max_length=1, choices=ENTITY_TYPE, default='')

    dependency = models.ForeignKey('OrganisationEntity', related_name='associates', null=True, blank=True)
    feature_id = models.CharField(max_length=25, null=True, blank=True)

    dispatch_categories = models.ManyToManyField('ReportCategory', related_name='assigned_to_department', blank=True)

    history = HistoricalRecords()

    fmsproxy = models.ForeignKey('fmsproxy.FMSProxy', null=True, blank=True)  # @TODO: Still needed?

    class Meta:
        translate = ('name', 'slug')
        ordering = ['name_fr']

    def contact_user(self):
        memberships = self.memberships.filter(contact_user=True)
        if memberships:
            return memberships[0].user

    def is_responsible(self):
        return self.active or self.associates.filter(type='D').exists()

    # def get_absolute_url(self):
    #     return reverse("report_commune_index", kwargs={'commune_id': self.id, 'slug': self.slug})

    def get_mail_config(self):
        return GroupMailConfig.objects.get(group=self)

    def __unicode__(self):
        return self.name

pre_save.connect(autoslug_transmeta('name', 'slug'), weak=False, sender=OrganisationEntity)


@receiver(post_save, sender=OrganisationEntity)
def create_matrix_when_creating_first_department(sender, instance, **kwargs):
    """This method is used to create the security matrix when creating the first department of the entity"""
    if instance.type == 'D' and instance.dependency:
        all_departments = instance.dependency.associates.filter(type='D')
        if all_departments.count() == 1 and instance.dispatch_categories.count() == 0:
            # the first department is created and the matrix is empty
            # actiate entity for citizen
            instance.dependency.active = True
            instance.dependency.save()
            for type in ReportCategory.objects.all():
                instance.dispatch_categories.add(type)


@receiver(pre_delete, sender=OrganisationEntity)
def organisationentity_delete(sender, instance, **kwargs):
    # Delete all memberships associated
    memberships = UserOrganisationMembership.objects.filter(organisation=instance)

    for membership in memberships:
        membership.delete()

class GroupMailConfig(models.Model):

    # Notifications can be sent to group, members or both
    notify_group   = models.BooleanField(default=True)
    notify_members = models.BooleanField(default=False)

    # Digest if True (or real-time mail if False) for each status
    digest_created    = models.BooleanField(default=False)
    digest_inprogress = models.BooleanField(default=False)
    digest_closed     = models.BooleanField(default=False)
    digest_other      = models.BooleanField(default=False)

    # This config is related to this group:
    group = models.ForeignKey(OrganisationEntity, limit_choices_to={"type": OrganisationEntity.DEPARTMENT}, unique=True)

    def get_manager_recipients(self, author=None):
        recipients = []

        # If the config mail allow the group to be notified
        if self.notify_group:
            recipients = [self.group.email]

        # If the config mail allow the members of the group to be notified
        if self.notify_members:

            # Not send the email twice if the group has the same email address than a member
            exclude_mails=[self.group.email]

            # Do not notify author if he is a PRO
            if author and author.is_pro():
                exclude_mails.append(author.email)

            # Get members recipients of this organisation
            recipients += UserOrganisationMembership.objects.filter(organisation=self.group).exclude(user__email__in=exclude_mails).values_list('user__email', flat=True)

        return recipients

class UserOrganisationMembership(UserTrackedModel):
    user = models.ForeignKey(FMSUser, related_name='memberships', null=True, blank=True)
    organisation = models.ForeignKey(
        OrganisationEntity,
        related_name='memberships',
        null=True,
        blank=True,
        limit_choices_to={"type__in": (
            OrganisationEntity.SUBCONTRACTOR,
            OrganisationEntity.APPLICANT,
            OrganisationEntity.DEPARTMENT,
            OrganisationEntity.NEIGHBOUR_HOUSE
        )}
    )
    contact_user = models.BooleanField(default=False)

    class Meta:
        unique_together = (("user", "organisation"),)


class ReportQuerySet(models.query.GeoQuerySet):

    def public(self):
        return self.filter(private=False, status__in=Report.REPORT_STATUS_VIEWABLE)

    def visible(self):
        limit_date = datetime.date.today() - datetime.timedelta(30)

        return self.filter(merged_with__isnull=True) \
            .exclude(status=Report.PROCESSED, fixed_at__lt=limit_date) \
            .exclude(status__in=Report.REPORT_STATUS_OFF) \
            .exclude(status=Report.REFUSED)

    def near(self, origin, distance):
        return self.distance(origin).filter(point__distance_lte=(origin, distance)).order_by('distance')

    # Because it returns a list and not a queryset, use it at the end of your ORM request: MyClass.objects.filter().rank()
    # params: Either arg or kwds
    # arg = 1 report object
    # kwds = report_point, report_category, report_date, created (optional), closed (optional), ignore_distance (optional)
    def rank(self, *arg, **kwds):
        DISTANCE_MAX = 50
        created      = False
        closed       = False
        params       = {
            'created' : False,
            'closed'  : False,

            'ignore_distance': kwds['ignore_distance'] if 'ignore_distance' in kwds else False,

            # For /debug/rank, we have to avoid visible filters
            'debug'   : kwds['debug'] if 'debug' in kwds else False,
        }

        # Prepare data according to params
        # 1 report object as arg
        if len(arg) == 1:
            report = arg[0]

            # Get report in DB and exclude it
            nearby_reports = self.exclude(id=report.id)

            params.update({
                'report_point'    : report.point,
                'report_category' : report.secondary_category,
                'report_date'     : report.created,
                'created'         : report.is_created(),
                'closed'          : report.is_closed()
            })

        # At least 3 params as kwargs
        else:
            # Get specific attributes
            params.update(kwds)

            # And fetch all reports
            nearby_reports = self.all()

        # Get related fields and only visible
        if not params['debug']:
            nearby_reports = nearby_reports.visible().related_fields()

        # Exclude CREATED or CLOSED reports according to status of the base report
        if params['created']:
            nearby_reports = nearby_reports.exclude(status=Report.CREATED)
        elif params['closed']:
            nearby_reports = nearby_reports.exclude(status__in=Report.REPORT_STATUS_CLOSED)

        #ticketnumber params means we want to merge with a specific incident and distance_max should be ignored
        if not params['ignore_distance']:
            # Get all reports in DISTANCE_MAX around the point
            nearby_reports = nearby_reports.near(params['report_point'], DISTANCE_MAX)

        #compute and fill the ranks of nearby reports
        nearby_reports.compute_ranks(params['report_category'], params['report_date'], DISTANCE_MAX)

        # Sort the list according to rank and return it
        return sorted(nearby_reports, key=lambda report: report.rank, reverse=True)

    def compute_ranks(self, report_category, report_date, distance_max):
        # Ranking
        for report_near in self:
            # Distance : (DISTANCE_MAX - distance) / DISTANCE_MAX * 4
            # (valeur entre 0 et 1 * 4)
            rank_distance = (distance_max - report_near.distance.m) / distance_max * 4
            if rank_distance < 0:
               rank_distance = 0    #If there is a ticketnumber param, distance between reports could be > DISTANCE_MAX
                                    #and thus rand_distance could be < 0
            # Category : 1 point par bon niveau de categorie en cascade depuis le premier niveau.
            # (valeur entre 0 et 3)
            rank_catego = 0
            if report_near.category == report_category.category_class:
                rank_catego += 1

                if report_near.secondary_category.secondary_category_class == report_category.secondary_category_class:
                    rank_catego += 1

                    if report_near.secondary_category == report_category:
                        rank_catego += 1

            # Date : 1 / abs(nbre de mois de difference +1)
            # (valeur entre 0 et 1)
            abs_days = abs((report_date - report_near.created).days)
            months   = float(abs_days) / 30

            if months > 1:
                rank_date = 1 / months
            else:
                rank_date = 1

            # Mobile : Si mobile risque eleve donc +1.
            # (valeur 0 OU 1)
            rank_source = 0
            if report_near.source == Report.SOURCES['MOBILE']:
                rank_source = 1

            # Status : Si signale +1 point.
            # (valeur 0 OU 1)
            rank_status = 0
            if report_near.status == Report.CREATED:
                rank_status = 1

            #David 9/9/2014
            #this is the rank in percent (number between 0 and 1). Number is divided by 10 because the sum
            #of all the other numbers is a number between 0 and 10 at the moment. If someone changes the rank
            # calculation,they should also change the sum just below
            rank_in_percent = (rank_distance + rank_catego + rank_date + rank_source + rank_status)/10

            # Set rank to report_near
            report_near.rank          = rank_in_percent
            report_near.rank_distance = rank_distance
            report_near.rank_catego   = rank_catego
            report_near.rank_date     = rank_date
            report_near.rank_source   = rank_source
            report_near.rank_status   = rank_status

    def responsible(self, user):
        query = Q()
        if user.contractor and user.manager:
            query = Q(responsible_department__in=user.organisations_list())
            return self.filter(query)

        if user.contractor:
            query = query | Q(contractor__in=user.organisations_list())

        if user.applicant:
            query = query | Q(contractor=user.organisation)

        if user.manager or user.leader or user.agent:
            query = query | Q(responsible_department__in=user.organisations_list())

        return self.filter(query)

    def entity_responsible(self, user):
        query = Q(responsible_entity=user.organisation)
        return self.filter(query)

    def responsible_contractor(self, user):
        query = Q(contractor__memberships__user=user)
        return self.filter(query)

    def entity_territory(self, organisation):
        return self.filter(postalcode__in=[zc.code for zc in organisation.zipcode.all()])

    def created(self):
        return self.filter(status=Report.CREATED)

    def in_progress(self):
        return self.filter(status__in=Report.REPORT_STATUS_IN_PROGRESS)

    def unfinished(self):
        return self.filter(Q(status=Report.CREATED) | Q(status__in=Report.REPORT_STATUS_IN_PROGRESS))

    def assigned(self):
        return self.filter(contractor__isnull=False)

    def closed(self):
        return self.filter(status__in=Report.REPORT_STATUS_CLOSED)

    def subscribed(self, user):
        return self.filter(subscriptions__subscriber=user)

    def related_fields(self):
        return self.select_related(
            'category', 'secondary_category',
            'secondary_category__secondary_category_class',
            'responsible_entity', 'responsible_department', 'contractor',
            'citizen', 'created_by')


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
            .exclude(status=Report.DELETED)

    def with_distance(self, origin):
        """
        Return a queryset with the distance between the report and the provided origin.

        Args: origin must be a ``Point``.
        """
        return self.get_query_set().distance(origin)


class Report(UserTrackedModel):
    __metaclass__ = TransMeta

    # List of status
    CREATED = 1
    REFUSED = 9
    TEMP = 11

    IN_PROGRESS = 2
    MANAGER_ASSIGNED = 4
    APPLICANT_RESPONSIBLE = 5
    CONTRACTOR_ASSIGNED = 6
    SOLVED = 7

    PROCESSED = 3
    DELETED = 8

    REPORT_STATUS_SETTABLE_TO_SOLVED = (CREATED, IN_PROGRESS, MANAGER_ASSIGNED, APPLICANT_RESPONSIBLE, CONTRACTOR_ASSIGNED)
    REPORT_STATUS_IN_PROGRESS = (IN_PROGRESS, MANAGER_ASSIGNED, APPLICANT_RESPONSIBLE, CONTRACTOR_ASSIGNED, SOLVED)
    REPORT_STATUS_VIEWABLE = (CREATED, IN_PROGRESS, MANAGER_ASSIGNED, APPLICANT_RESPONSIBLE, CONTRACTOR_ASSIGNED, PROCESSED, SOLVED)
    REPORT_STATUS_ASSIGNED = (APPLICANT_RESPONSIBLE, CONTRACTOR_ASSIGNED)
    REPORT_STATUS_CLOSED = (PROCESSED, DELETED)
    REPORT_STATUS_OFF = (DELETED, TEMP)

    REPORT_STATUS_CHOICES = (
        (_("Created"), (
            (CREATED, _("Created")),
            (REFUSED, _("Refused")),
            (TEMP, _("Temp")),
        )),
        (_("In progress"), (
            (IN_PROGRESS, _("In progress")),
            (MANAGER_ASSIGNED, _("Manager is assigned")),
            (APPLICANT_RESPONSIBLE, _("Applicant is responsible")),
            (CONTRACTOR_ASSIGNED, _("Contractor is assigned")),
            (SOLVED, _("Solved"))
        )),
        (_("Processed"), (
            (PROCESSED, _("Processed")),
            (DELETED, _("Deleted")),
        ))
    )

    PROBABILITY_CHOICES = (
        (0, "-"),
        (1, pgettext_lazy("probability", "Unlikely")),
        (2, pgettext_lazy("probability", "Rare")),
        (3, pgettext_lazy("probability", "Possible")),
        (4, pgettext_lazy("probability", "Occasionnel"))
    )

    GRAVITY_CHOICES = (
        (0, "-"),
        (1, pgettext_lazy("gravity", "Moderate")),
        (2, pgettext_lazy("gravity", "Serious")),
        (3, pgettext_lazy("gravity", "Grave")),
        (4, pgettext_lazy("gravity", "Major"))
    )

    SOURCES = {
        'WEB' : 'web',
        'MOBILE': 'mobile'
    }

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

    date_planned = models.DateTimeField(null=True, blank=True)
    pending = models.BooleanField(default=False)

    hash_code = models.IntegerField(null=True, blank=True)  # used by external app for secure sync, must be random generated

    citizen = models.ForeignKey(FMSUser, null=True, related_name='citizen_reports', blank=True)

    responsible_entity = models.ForeignKey(
        OrganisationEntity,
        related_name='reports_in_charge',
        null=True, blank=True,
        limit_choices_to={
            'type__in': (OrganisationEntity.REGION, OrganisationEntity.COMMUNE),
            'active': True
        }
    )
    responsible_department = models.ForeignKey(
        OrganisationEntity,
        related_name='reports_in_department',
        null=True,
        limit_choices_to={
            'type': OrganisationEntity.DEPARTMENT
        }
    )

    contractor = models.ForeignKey(OrganisationEntity, related_name='assigned_reports', null=True, blank=True)
    previous_managers = models.ManyToManyField('FMSUser', related_name='previous_reports', null=True, blank=True)

    merged_with = models.ForeignKey('Report', related_name='merged_reports', null=True, blank=True)

    private = models.BooleanField(default=False)
    gravity = models.IntegerField(default=0, choices=GRAVITY_CHOICES)
    probability = models.IntegerField(default=0, choices=PROBABILITY_CHOICES)
    photo = models.FileField(upload_to="photos", blank=True)
    thumbnail = models.TextField(null=True, blank=True)
    thumbnail_pro = models.TextField(null=True, blank=True)
    close_date = models.DateTimeField(null=True, blank=True)

    terms_of_use_validated = models.BooleanField(default=False)

    objects = ReportManager()
    history = HistoricalRecords()

    false_address = models.TextField(null=True, blank=True)
    # provider of the report (mobile / web / osiris...)
    source = models.TextField(null=False, blank=False, default=SOURCES['WEB'])

    #indicates whether the responsibility of the incident should be associated to a third party or not.
    third_party_responsibility = models.BooleanField(default=False)

    def get_category_path(self):
        return " > ".join([self.secondary_category.category_class.name, self.secondary_category.secondary_category_class.name, self.secondary_category.name])

    def get_marker(self):
        marker_color = "green"

        if self.is_in_progress():
            marker_color = "orange"
        elif self.is_created():
            marker_color = "red"
        elif self.is_refused() or self.is_temporary():
            marker_color = "gray"

        return "images/marker-" + marker_color + "-xxs.png"

    def get_marker_flat(self):
        marker_color = "icon2-list_closed"

        if self.is_in_progress():
            marker_color = "icon2-list_in_progress"
        elif self.is_created():
            marker_color = "icon2-list_created"

        return marker_color

    def is_contractor_or_applicant_assigned(self):
        return self.status == Report.APPLICANT_RESPONSIBLE or self.status == Report.CONTRACTOR_ASSIGNED

    def is_regional(self):
        return self.address_regional

    def is_solved(self):
        return self.status == Report.SOLVED

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

    def display_category(self):
        return self.category.name + " / " + self.secondary_category.secondary_category_class.name + " : " + self.secondary_category.name

    def display_address(self):
        return "%s, %s (%s %s)" % (self.address, self.address_number, self.postalcode, self.get_address_commune_name())

    def get_ticket_number(self):
        '''Return the report ticket as a usable string'''
        report_ticket_id = str(self.id)
        if (report_ticket_id.__len__() <= 6):
            for i in range(6 - (report_ticket_id.__len__())):
                report_ticket_id = "0" + report_ticket_id
        return report_ticket_id

    def get_slug(self):
        slug_sec_cat = self.secondary_category.slug
        slug_sec_cat_class = self.secondary_category.secondary_category_class.slug
        slug_cat = self.category.slug
        slug_ent = self.responsible_entity.slug
        return "{0}-{1}-{2}-{3}".format(slug_sec_cat, slug_sec_cat_class, slug_cat, slug_ent)

    def get_creator(self):
        if (self.is_pro()):
            return self.created_by
        else:
            return self.citizen

    def get_absolute_url(self):
        return reverse("report_show", kwargs={'report_id': self.id, 'slug': self.get_slug()})

    def get_absolute_url_pro(self):
        return reverse("report_show_pro", kwargs={'report_id': self.id, 'slug': self.get_slug()})

    def get_pdf_url(self):
        return reverse('report_pdf', args=[self.id])

    def get_pdf_url_pro(self):
        return reverse('report_pdf_pro', args=[self.id])

    def get_pdf_url_pro_with_auth_token(self):
        site = Site.objects.get_current()
        base_url = "http://{}".format(site.domain.rstrip("/"))
        url = reverse("report_pdf_pro_token", args=[self.id]).lstrip("/")
        querystring = urlencode({"auth": self.get_pdf_pro_auth_token()})
        return "{}/{}?{}".format(base_url, url, querystring)

    def get_pdf_pro_auth_token(self):
        key = settings.PDF_PRO_TOKEN_KEY
        message = u"{} {}".format(self.id, self.created.isoformat())
        return sign_message(key, message)

    def has_pdf_pro_access(self, request):
        token = request.POST.get("auth", request.GET.get("auth"))
        return token == self.get_pdf_pro_auth_token()

    def get_priority(self):
        return self.gravity * self.probability

    def has_at_least_one_non_confidential_comment(self):
        return ReportComment.objects.filter(report__id=self.id).filter(security_level__in=[1, 2]).count() != 0

    def has_at_least_one_non_confidential_file(self):
        return ReportFile.objects.filter(report__id=self.id).filter(security_level__in=[1, 2]).count() != 0

    def last_history_event(self):
        return ReportEventLog.objects.filter(report__id=self.id).latest('event_at')

    def last_history_status_event(self):
        return ReportEventLog.objects.filter(report__id=self.id).filter(event_type__in=ReportEventLog.STATUS_EVENTS).latest('event_at')

    def active_comments(self):
        return self.comments().filter(logical_deleted=False).filter(security_level=1).order_by("created")

    def active_files(self):
        return self.files().filter(logical_deleted=False).filter(security_level=1).order_by("created")

    def active_attachments(self):
        return self.attachmentsList().filter(logical_deleted=False).filter(security_level=1).order_by("created")

    def active_attachments_pro(self):
        return self.attachmentsList().filter(logical_deleted=False).order_by("-created")

    def is_created(self):
        return self.status == Report.CREATED

    def is_refused(self):
        return self.status == Report.REFUSED

    def is_temporary(self):
        return self.status == Report.TEMP

    def is_in_progress(self):
        return self.status in Report.REPORT_STATUS_IN_PROGRESS

    def is_closed(self):
        return self.status in Report.REPORT_STATUS_CLOSED

    def is_merged(self):
        return self.merged_with is not None

    def is_planned(self):
        return self.date_planned is not None

    def get_public_status_display(self):
        if self.is_created():
            return ugettext("Created")
        elif self.is_refused():
            return ugettext("Refused")
        elif self.is_temporary():
            return ugettext("Temporary")
        elif self.is_in_progress():
            return ugettext("In progress")
        else:
            return ugettext("Processed")

    @classmethod
    def static_get_status_for_js_map(cls, status):
        if status == cls.CREATED:
            return "reported"
        elif status == cls.PROCESSED:
            return "closed"
        elif status in cls.REPORT_STATUS_IN_PROGRESS:
            return "ongoing"
        else:
            return "other"

    def get_status_for_js_map(self):
        if self.is_created():
            return "reported"
        elif self.is_in_progress():
            return "ongoing"
        elif self.is_closed():
            return "closed"
        #elif self.is_refused() or self.is_temporary():
        else:
            return "other"

    def get_icons_for_js_map(self, pro=False):
        icons = {
            "regionalRoads": self.is_regional(),
            "assigned": self.is_contractor_or_applicant_assigned(),
            "planned": self.is_planned(),
        }
        if pro:
            icons.update({
                "pro": self.is_pro(),
                "priority": self.get_priority(),
                "solved": self.is_solved(),
            })
        return icons

    def get_date_planned(self):
        if self.date_planned:
            return self.date_planned.strftime('%m/%Y')
        return ""

    def get_date_planned_available(self):
        dates = []
        start_date = datetime.date.today() + timedelta(days=1)
        end_date = datetime.date(self.accepted_at.year, self.accepted_at.month, self.accepted_at.day) + timedelta(days=365)

        while (start_date < end_date):
            dates.append(start_date)

            month = start_date.month
            while (month == start_date.month):
                start_date = start_date + timedelta(days=1)

        return dates

    def get_nearby_reports(self):
        nearby_reports = Report.objects.all().rank(self)
        return nearby_reports

    def get_nearby_reports_count(self):
        count_nearby_reports = Report.objects.all().rank(self)
        return len(count_nearby_reports)

    def is_markable_as_solved(self):
        return self.status in Report.REPORT_STATUS_SETTABLE_TO_SOLVED

    def comments(self):
        # return self.attachments.get_query_set().comments().filter(logical_deleted=False)
        # ==> is wrong
        return ReportComment.objects.filter(report_id=self.id).filter(logical_deleted=False, security_level__in=[1, 2])

    def files(self):
        # return self.attachments.get_query_set().files().filter(logical_deleted=False)
        # ==> is wrong
        return ReportFile.objects.filter(report_id=self.id).filter(logical_deleted=False, security_level__in=[1, 2])

    def attachmentsList(self):
        return ReportAttachment.objects.filter(report_id=self.id).filter(logical_deleted=False)

    def territorial_entity(self):
        return OrganisationEntity.objects.get(zipcode__code=self.postalcode)

    def subscribe_author_ws(self):
        user = self.citizen or self.created_by
        if not self.subscriptions.filter(subscriber=user).exists():
            subscription = ReportSubscription(subscriber=user)
            subscription.notify_creation = False  # don't send notification for subscription
            self.subscriptions.add(subscription)

    def subscribe_author(self):
        user = self.created_by or self.citizen
        if not self.subscriptions.filter(subscriber=user).exists():
            subscription = ReportSubscription(subscriber=user)
            subscription.notify_creation = False  # don't send notification for subscription
            self.subscriptions.add(subscription)

    # def trigger_reopen_request(self, user=None, reopen_reason=None):
    #
    #     # Send notifications to group or members according to group configuration
    #     mail_config = report.responsible_department.get_mail_config()
    #
    #     if not mail_config.digest_other:
    #         recipients = mail_config.get_manager_recipients()
    #
    #         for email in recipients:
    #             ReportNotification(
    #                 content_template='notify-reopen-request',
    #                 recipient_mail=self.responsible_department.email,
    #                 related=self,
    #             ).save(updater=user, reopen_reason=reopen_reason)
    #
    #     ReportNotification(
    #         content_template='acknowledge-reopen-request',
    #         recipient_mail=user.email,
    #         related=self,
    #     ).save(updater=user, reopen_reason=reopen_reason)
    #
    #     ReportEventLog(
    #         report=self,
    #         event_type=ReportEventLog.REOPEN_REQUEST,
    #         user=user,
    #     ).save()
    #
    #     self.save()  # set updated date and modified_by

    def to_full_JSON(self):
        """
        Method used to display the whole object content as JSON structure for website
        """

        local_thumbnail = self.thumbnail
        thumbValue = local_thumbnail or 'null'

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
            "close_date": str(self.close_date),
            "private": self.private,
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
        local_thumbnail = self.thumbnail_pro

        thumbValue = local_thumbnail or 'null'

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
            "address_regional": self.responsible_entity.id == 20,
            "contractor": True if self.contractor else False,
            "date_planned": self.get_date_planned(),
            "thumb": thumbValue,
            "is_closed": self.is_closed(),
            "citizen": not self.is_pro(),
            "priority": self.get_priority()
        }

    def full_marker_detail_JSON(self):
        local_thumbnail = self.thumbnail
        if local_thumbnail:
            thumbValue = local_thumbnail
        else:
            thumbValue = 'null'

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
            "address_regional": self.responsible_entity.id == 20,
            "thumb": thumbValue,
            "contractor": True if self.contractor else False,
            "date_planned": self.get_date_planned()
        }

    def to_JSON(self):
        """
        Method used to display the object as JSON structure for website
        """

        close_date_as_string = ""
        if self.close_date:
            close_date_as_string = self.close_date.strftime("%Y-%m-%d %H:%M:%S")

        local_thumbnail = self.thumbnail
        thumbValue = local_thumbnail or 'null'

        local_citizen = self.citizen
        if local_citizen:
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
            "c": self.secondary_category.id,
            "m_c": self.secondary_category.category_class.id,
            "s_c": self.secondary_category.secondary_category_class.id
        }

    #returns the fms proxy entity such as Belgacom, Osiris, etc if there is one (None otherwise)
    def get_organisation_entity_with_fms_proxy(self):
        if self.contractor and self.contractor.fmsproxy:
            return self.contractor
        elif self.responsible_department and self.responsible_department.fmsproxy:
            return self.responsible_department
        elif self.responsible_entity and self.responsible_entity.fmsproxy:
            return self.responsible_entity
        else:
            return None

    #returns if the report is at the moment associated to a fms proxy entity (Belgacom, osiris, etc)
    def waiting_for_organisation_entity(self):
        if self.is_in_progress() and self.get_organisation_entity_with_fms_proxy():
            return True
        return False

    def close(self):
        #Update the status and set the close date
        self.status = Report.PROCESSED
        self.close_date = datetime.datetime.now()
        if not self.fixed_at:
            self.fixed_at = self.close_date
        self.save()

    class Meta:
        translate = ('address',)
        # unique_together = (("point", "citizen"), ("point", "created_by"))


@receiver(pre_save, sender=Report)
def track_former_value(sender, instance, **kwargs):
    """Save former data to compare with new data and track changed values"""
    if instance.id and not kwargs['raw']:
        former_report = Report.objects.get(id=instance.id)
        instance.__former = dict((field.name, getattr(former_report, field.name)) for field in Report._meta.fields)
    else:
        instance.__former = dict((field.name, getattr(Report(), field.name)) for field in Report._meta.fields)


@receiver(pre_save, sender=Report)
def init_street_number_as_int(sender, instance, **kwargs):
    """
    Store the street number as int for further filtering (as somtimes the street number is 19H ...)
    """
    non_decimal = re.compile(r'[^\d]+')
    value_processed = non_decimal.sub('', instance.address_number)
    instance.address_number_as_int = int(value_processed)


@receiver(pre_save, sender=Report)
def init_regional_street(sender, instance, **kwargs):
    if not instance.id and not kwargs['raw']:
        if StreetSurface.objects.filter(geom__intersects=instance.point.buffer(5), administrator=StreetSurface.REGION).exists():
            instance.address_regional = True


@receiver(pre_save, sender=Report)
def report_auto_assign_responsible(sender, instance, **kwargs):
    # Auto-dispatching according to group and regional or communal address
    if instance.secondary_category.get_organisation(instance.address_regional):
        instance.responsible_department = instance.secondary_category.get_organisation(instance.address_regional)
        instance.responsible_entity     = instance.responsible_department.dependency


@receiver(pre_save, sender=Report)
def report_assign_responsible(sender, instance, **kwargs):
    if not instance.responsible_entity:
        # Detect who is the responsible Manager for the given type
        if (
                instance.created_by and
                hasattr(instance.created_by, 'fmsuser') and
                instance.created_by.fmsuser.organisation and
                instance.created_by.fmsuser.organisation.is_responsible()
        ):
            # assign entity of the creator
            instance.responsible_entity = instance.created_by.fmsuser.organisation
        else:
            reponsibles = OrganisationEntitySurface.objects.filter(geom__contains=instance.point)
            if len(reponsibles) == 1:
                instance.responsible_entity = reponsibles[0].owner
            else:
                raise Exception("point does not match any entity surface")

    if not instance.responsible_department:
        # Detect who is the responsible Manager for the given type
        # Search the right responsible for the current organisation.
        departements = instance.responsible_entity.associates.filter(
            type=OrganisationEntity.DEPARTMENT)

        # Get the responsible according to dispatching category
        instance.responsible_department = departements.get(dispatch_categories=instance.secondary_category)


@receiver(pre_save, sender=Report)
def check_planned(sender, instance, **kwargs):
    if instance.pk and instance.date_planned:
        old_report = Report.objects.get(pk=instance.pk)

        dates_exists = True if old_report.accepted_at else False
        date_too_small = instance.date_planned.strftime('%Y%m') < old_report.accepted_at.strftime('%Y%m') if dates_exists else False
        date_too_big = instance.date_planned > (old_report.accepted_at + timedelta(days=365)) if dates_exists else False

        if not dates_exists or date_too_small or date_too_big:
            instance.date_planned = old_report.date_planned
    # else:
        # instance.date_planned = None

@receiver(post_save, sender=Report)
def report_notify_created(sender, instance, **kwargs):
    """
    signal on a report to notify author and manager that the report is created
    """

    if not kwargs['raw'] and kwargs['created']:
        report = instance

        if report.citizen:
            event_log_user = report.citizen
        else:
            event_log_user = report.created_by

        # Create an event in history
        ReportEventLog(
            report=report,
            event_type=ReportEventLog.CREATED,
            user=event_log_user,
            related_new=report.responsible_department
        ).save()

        # Notifiy user that the creation is a success
        if report.citizen:
            ReportNotification(
                content_template='acknowledge-creation',
                recipient=report.citizen,
                related=report,
            ).save()

        # Send notifications to group or members according to group configuration
        mail_config = report.responsible_department.get_mail_config()

        if not mail_config.digest_created:
            recipients = mail_config.get_manager_recipients(event_log_user)

            for email in recipients:
                ReportNotification(
                    content_template='notify-creation',
                    recipient_mail=email,
                    related=report,
                ).save()

@receiver(post_save, sender=Report)
def report_notify_status_changed(sender, instance, **kwargs):
    """
    signal on a report to notify author and manager that the status of the report has changed
    """

    if not kwargs['raw']:
        report = instance
        event_log_user = report.modified_by

        if report.__former['status'] != report.status:

            # REFUSED
            if report.status == Report.REFUSED:
                event = ReportEventLog(
                    report=report,
                    event_type=ReportEventLog.REFUSE,
                    user=event_log_user)
                event.save()

            # PROCESSED
            elif report.status == Report.PROCESSED:
                ReportEventLog(
                    report=report,
                    event_type=ReportEventLog.CLOSE,
                    user=event_log_user
                ).save()

                # Notify author that the report is solved
                ReportNotification(
                    content_template='announcement-processed',
                    recipient=report.citizen or report.created_by,
                    related=report,
                    reply_to=report.responsible_department.email,
                ).save()

            # IN PROGRESS
            elif report.__former['status'] == Report.CREATED and report.status != Report.REFUSED:
                event = ReportEventLog(
                    report=report,
                    event_type=ReportEventLog.VALID,
                    user=event_log_user)
                event.save()

            # SOLVED
            elif report.status == Report.SOLVED:

                ReportEventLog(
                    report=report,
                    event_type=ReportEventLog.SOLVE_REQUEST,
                    user=event_log_user
                ).save()

                # Send notifications to group or members according to group configuration
                mail_config = report.responsible_department.get_mail_config()

                if not mail_config.digest_other:
                    recipients = mail_config.get_manager_recipients(event_log_user)

                    for email in recipients:
                        ReportNotification(
                            content_template='mark-as-done',
                            recipient_mail=email,
                            related=report,
                        ).save(updater=event_log_user)

            # REOPEN
            elif (report.__former['status'] in Report.REPORT_STATUS_CLOSED or report.__former['status'] == Report.REFUSED) and report.status == Report.MANAGER_ASSIGNED:
                ReportEventLog(
                    report=report,
                    event_type=ReportEventLog.REOPEN,
                    user=event_log_user
                ).save()

@receiver(post_save, sender=Report)
def report_notify_contractor_changed(sender, instance, **kwargs):
    """
    signal on a report to notify author and manager that the contractor of the report has changed
    """

    if not kwargs['raw']:
        report = instance
        event_log_user = report.modified_by


        if report.__former['contractor'] != report.contractor:
            if report.contractor:
                event = ReportEventLog(
                    report=report,
                    event_type=(ReportEventLog.APPLICANT_ASSIGNED if report.status == Report.APPLICANT_RESPONSIBLE else ReportEventLog.CONTRACTOR_ASSIGNED),
                    related_new=report.contractor,
                    user=event_log_user)
                event.save()

                # Applicant responsible
                if report.contractor.email:
                    ReportNotification(
                        content_template='notify-affectation',
                        recipient_mail=report.contractor.email,
                        related=report,
                        reply_to=report.responsible_department.email
                    ).save(old_responsible=report.__former['responsible_department'])

@receiver(post_save, sender=Report)
def report_notify_responsible_changed(sender, instance, **kwargs):
    """
    signal on a report to notify author and manager that the responsible of the report has changed
    """

    if not kwargs['raw']:
        report = instance
        event_log_user = report.modified_by

        if report.__former['responsible_department'] != report.responsible_department:

            if report.status != Report.CREATED and report.status != Report.TEMP:

                # Send notifications to group or members according to group configuration
                mail_config = report.responsible_department.get_mail_config()

                if not mail_config.digest_inprogress:
                    recipients = mail_config.get_manager_recipients(event_log_user)

                    for email in recipients:
                        ReportNotification(
                            content_template='notify-affectation',
                            recipient_mail=email,
                            related=report,
                        ).save(old_responsible=report.__former['responsible_department'])

                ReportEventLog(
                    report=report,
                    event_type=ReportEventLog.MANAGER_ASSIGNED,
                    related_new=report.responsible_department,
                    related_old=report.__former['responsible_department'],
                    user=event_log_user
                ).save()

                if report.__former['responsible_entity'] != report.responsible_entity:
                    event = ReportEventLog(
                        report=report,
                        event_type=ReportEventLog.ENTITY_ASSIGNED,
                        related_new=report.responsible_entity,
                        user=event_log_user)
                    event.save()

@receiver(post_save, sender=Report)
def report_notify_report_planned(sender, instance, **kwargs):
    """
    signal on a report to notify author and manager that the report has been planned
    """

    if not kwargs['raw']:
        report = instance
        event_log_user = report.modified_by

        if report.date_planned and report.__former['date_planned'] != report.date_planned:
            event = ReportEventLog(
                report=report,
                event_type=ReportEventLog.PLANNED,
                user=event_log_user)
            event.save()

@receiver(post_save, sender=Report)
def report_notify_report_merged(sender, instance, **kwargs):
    """
    signal on a report to notify author and manager that the report has been merged
    """

    if not kwargs['raw']:
        report = instance
        event_log_user = report.modified_by

        if report.merged_with and report.__former['merged_with'] != report.merged_with:
            creator = report.citizen or report.created_by

            # Create event merge
            ReportEventLog(
                report=report,
                event_type=ReportEventLog.MERGED,
                user=event_log_user
            ).save()

            # Create event merge with
            ReportEventLog(
                report=report.merged_with,
                event_type=ReportEventLog.MERGED,
                merged_with_id=report.id,
                user=event_log_user
            ).save()

@receiver(post_save, sender=Report)
def report_notify_report_private(sender, instance, **kwargs):
    """
    signal on a report to notify author and manager that the status of the report has became private
    """

    if not kwargs['raw']:
        report = instance
        event_log_user = report.modified_by

        if (not kwargs['created'] and report.private and (not report.__former['private'])):
            # Inform all subscribers in real-time
            for subscription in report.subscriptions.all():
                if not subscription.subscriber.is_pro():
                    ReportNotification(
                    content_template='notify-became-private',
                    recipient=subscription.subscriber,
                    related=report,
                    reply_to=report.responsible_department.email,
                ).save()

@receiver(post_save, sender=Report)
def report_notify_report_public(sender, instance, **kwargs):
    """
    signal on a report to notify author and manager that the status of the report has became public
    """

    if not kwargs['raw']:
        report = instance
        event_log_user = report.modified_by

        if (not kwargs['created'] and not report.private and (report.__former['private'])):
            # Inform all subscribers in real-time
            for subscription in report.subscriptions.all():
                if not subscription.subscriber.is_pro():
                    ReportNotification(
                    content_template='notify-became-public',
                    recipient=subscription.subscriber,
                    related=report,
                    reply_to=report.responsible_department.email,
                ).save()

@receiver(pre_save, sender=Report)
def webhook_assignment(sender, instance, **kwargs):
    """
    Checks whether the report is being assigned to someone else.

    This fires/delegates to the hook. The hook is responsible to contact third-parties as necessary.
    """
    from django_fixmystreet.webhooks import outbound
    assignment_is_changed = instance.contractor and instance.__former['contractor'] != instance.contractor
    if kwargs['raw'] or not assignment_is_changed or not instance.is_in_progress():
        return

    webhook = outbound.ReportAssignmentRequestOutWebhook(instance, third_party=instance.contractor)
    webhook.fire()

@receiver(pre_save, sender=Report)
def webhook_transfer(sender, instance, **kwargs):
    """
    Checks whether the report is being transferred to someone else.

    This fires/delegates to the hook. The hook is responsible to contact third-parties as necessary.
    """
    from django_fixmystreet.webhooks import outbound
    is_transferred = instance.responsible_department and instance.__former['responsible_department'] != instance.responsible_department
    if kwargs['raw'] or not is_transferred or not instance.is_in_progress():
        return

    webhook = outbound.ReportTransferRequestOutWebhook(instance, third_party=instance.responsible_department)
    webhook.fire()


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
        qs = super(ReportAttachmentQuerySet, self)._clone(*args, **kwargs)
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

    #type
    DOCUMENTATION = 1
    CLOSED = 2
    REFUSED = 3
    MARK_AS_DONE = 4
    REOPEN_REQUEST = 5

    REPORT_ATTACHMENT_SECURITY_LEVEL_CHOICES = (
        (PUBLIC, _("Public")),
        (PRIVATE, _("Private")),
        (CONFIDENTIAL, _("Confidential"))
    )

    REPORT_ATTACHMENT_TYPE_CHOICES = (
        (DOCUMENTATION, _("Documentation")),
        (CLOSED, _("Closing message")),
        (REFUSED, _("Refusing message")),
        (MARK_AS_DONE, _("Mark as done message")),
        (REOPEN_REQUEST, _("Reopen request message")),
    )

    type = models.IntegerField(choices=REPORT_ATTACHMENT_TYPE_CHOICES, default=DOCUMENTATION, null=False)
    logical_deleted = models.BooleanField(default=False)
    security_level = models.IntegerField(choices=REPORT_ATTACHMENT_SECURITY_LEVEL_CHOICES, default=PRIVATE, null=False)
    report = models.ForeignKey(Report, related_name="attachments")

    objects = ReportAttachmentManager()

    publish_update = True

    def is_citizen_visible(self):
        '''Visible when not confidential and public'''
        # return self.is_validated and self.is_visible
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
        if not self.created_by or not self.created_by.first_name and not self.created_by.last_name:
            return _('ANONYMOUS')
        else:
            return self.created_by.first_name + ' ' + self.created_by.last_name

    def get_display_name_as_citizen(self):
        if self.created_by:
            if self.created_by.is_citizen():
                return _("a citizen")
            elif self.created_by.get_organisation():
                return self.created_by.get_organisation()
            else:
                return self.created_by.get_display_name()

        return _('ANONYMOUS')

    # needed to make sure that no mail is sent when a complete report is published only when individual reports are updated
    def save(self, *args, **kwargs):
        if 'publish_report' in kwargs:
            del kwargs['publish_report']
            self.publish_update = False
        super(ReportAttachment, self).save(*args, **kwargs)

    def get_type_message(self):
        if self.type == self.REFUSED:
            return dict(self.REPORT_ATTACHMENT_TYPE_CHOICES).get(self.REFUSED)
        elif self.type == self.MARK_AS_DONE:
            return dict(self.REPORT_ATTACHMENT_TYPE_CHOICES).get(self.MARK_AS_DONE)
        elif self.type == self.REOPEN_REQUEST:
            reason_int = ReportReopenReason.objects.get(pk=self.id).reason
            reason = dict(ReportReopenReason.REASON_CHOICES).get(reason_int)
            message = dict(self.REPORT_ATTACHMENT_TYPE_CHOICES).get(self.REOPEN_REQUEST)
            final_msg = string_concat(message," (", reason, ") :")
            return final_msg
        else:
            return ""


# Initialise instance.report.thumbnail with the first public photo. For pro and citizen
@receiver(post_save, sender=ReportAttachment)
def init_report_overview(sender, instance, **kwargs):

    # Thumbnail for citizen
    images_public = instance.report.active_files().filter(file_type=ReportFile.IMAGE)
    if images_public.exists():
        instance.report.thumbnail = images_public[0].image.thumbnail.url()
    else:
        instance.report.thumbnail = None

    # Thumbnail for pro
    images_pro = instance.report.files().filter(logical_deleted=False, file_type=ReportFile.IMAGE)
    if images_pro.exists():
        instance.report.thumbnail_pro = images_pro[0].image.thumbnail.url()
    else:
        instance.report.thumbnail_pro = None

    instance.report.save()

@receiver(post_save, sender=ReportAttachment)
def report_attachment_created(sender, instance, **kwargs):

    if kwargs['raw'] or not kwargs['created']:
        return

    # If the comment is created during the creation of a new report or if it's not a documentation, pass this signal
    if instance.type != ReportAttachment.DOCUMENTATION or hasattr(instance, 'is_new_report') and instance.is_new_report:
        return

    report = instance.report
    user   = instance.created_by

    # If the latest comment created is longer than 1 minute, create a new event
    if not ReportEventLog.objects.filter(report=report, event_type=ReportEventLog.UPDATED, event_at__gt=datetime.datetime.now() - datetime.timedelta(minutes=0)).exists():

        ReportEventLog(
            report=report,
            event_type=ReportEventLog.UPDATED,
            user=user,
        ).save()

        # Send notifications to group or members according to group configuration
        mail_config = report.responsible_department.get_mail_config()

        if not mail_config.digest_created and not mail_config.digest_inprogress:
            # Check type of instance to pass correct arg to ReportNotification
            instance_comment = None
            instance_files   = []

            if type(instance) is ReportFile:
                instance_files = [instance]

            if type(instance) is ReportComment:
                instance_comment = instance

            # Send notifications to correct recipients
            recipients = mail_config.get_manager_recipients(user)

            for email in recipients:
                ReportNotification(
                    content_template='notify-updates',
                    recipient_mail=email,
                    related=report,
                ).save(updater=user, comment=instance_comment, files=instance_files)

@receiver(post_save, sender=ReportAttachment)
def report_attachment_published(sender, instance, **kwargs):

    if kwargs['raw'] or kwargs['created']:
        return

    # If instance is not public or not published or is related to a new report, do nothing
    if not instance.is_public() or not instance.publish_update or hasattr(instance, 'is_new_report') and instance.is_new_report:
        return

    # If the latest published attachment is longer than 1 minute, create a new event
    if not ReportEventLog.objects.filter(report=instance.report, event_type=ReportEventLog.UPDATE_PUBLISHED, event_at__gt=datetime.datetime.now() - datetime.timedelta(minutes=1)).exists():

        # Create an event
        ReportEventLog(
            report=instance.report,
            event_type=ReportEventLog.UPDATE_PUBLISHED,
            user=instance.created_by
        ).save()

class ReportComment(ReportAttachment):
    text = models.TextField()


@receiver(post_save, sender=ReportComment)
def report_comment_notify(sender, instance, **kwargs):
    report_attachment_created(sender, instance, **kwargs)
    report_attachment_published(sender, instance, **kwargs)

class ReportFile(ReportAttachment):
    PDF = 1
    WORD = 2
    EXCEL = 3
    IMAGE = 4
    attachment_type = (
        (PDF, "pdf"),
        (WORD, "word"),
        (EXCEL, "excel"),
        (IMAGE, "image")
    )

    def move_to(instance, filename):
        path = unicode("files/{0}/{1:02d}/{2:02d}/{3}").format(
            instance.report.created.year,
            instance.report.created.month,
            instance.report.id,
            unicode(filename))
        return path

    file = models.FileField(upload_to=move_to, blank=True)
    image = FixStdImageField(upload_to=move_to, blank=True, size=(1200, 800), thumbnail_size=(80, 120))
    file_type = models.IntegerField(choices=attachment_type)
    title = models.TextField(max_length=250, null=True, blank=True)
    file_creation_date = models.DateTimeField(blank=False, null=True)

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
def init_file_type(sender, instance, **kwargs):
    if instance.file_type or not instance.file:
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

@receiver(post_save, sender=ReportFile)
def report_file_notify(sender, instance, **kwargs):
    init_report_overview(sender, instance, **kwargs)
    report_attachment_created(sender, instance, **kwargs)
    report_attachment_published(sender, instance, **kwargs)

class ReportSubscription(models.Model):
    """
    Report Subscribers are notified when there's an update to an existing report.
    """
    report = models.ForeignKey(Report, related_name="subscriptions")
    subscriber = models.ForeignKey(FMSUser, related_name="subscriptions", null=False)

    def __unicode__(self):
        return self.subscriber.email

    class Meta:
        unique_together = (("report", "subscriber"),)


@receiver(post_save, sender=ReportSubscription)
def notify_report_subscription(sender, instance, **kwargs):
    if not kwargs['raw'] and kwargs['created'] and (not hasattr(instance, 'notify_creation') or instance.notify_creation):
        report = instance.report
        notifiation = ReportNotification(
            content_template='notify-subscription',
            recipient=instance.subscriber,
            related=report,
            reply_to=report.responsible_department.email,
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
        return json.dumps(list_of_elements_as_json)

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
        return json.dumps(list_of_elements_as_json)

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

    organisation_communal = models.ForeignKey(OrganisationEntity, related_name="categories_communal", help_text="Group for auto dispatching", limit_choices_to={"type": OrganisationEntity.DEPARTMENT}, null=True, blank=True)
    organisation_regional = models.ForeignKey(OrganisationEntity, related_name="categories_regional", help_text="Group for auto dispatching", limit_choices_to={"type": OrganisationEntity.DEPARTMENT, "dependency__type": OrganisationEntity.REGION}, null=True, blank=True)

    def __unicode__(self):
        return self.category_class.name + ":" + self.name

    def get_organisation(self, region):
        # If this category has a regional organisation assigned and that the target is regional
        if region:
            return self.organisation_regional

        # If this category has a communal organisation assigned and that the target is communal
        if not region:
            return self.organisation_communal

        return False

    @staticmethod
    def listToJSON(list_of_elements):
        list_of_elements_as_json = []
        d = {}
        prev_d = {
            'id': None,
            'n_en': None,
            'n_fr': None,
            'n_nl': None,
            'm_c_id': None,
            'm_c_n_en': None,
            'm_c_n_fr': None,
            'm_c_n_nl': None,
            's_c_id': None,
            's_c_n_en': None,
            's_c_n_fr': None,
            's_c_n_nl': None,
            'p': None
        }

        for current_element in list_of_elements:
            d = {}
            d['id'] = getattr(current_element, 'id')
            d['n_en'] = getattr(current_element, 'name_fr')
            d['n_fr'] = getattr(current_element, 'name_fr')
            d['n_nl'] = getattr(current_element, 'name_nl')
            d['m_c_id'] = getattr(getattr(current_element, 'category_class'), 'id')

            is_it_public = getattr(current_element, 'public')
            if is_it_public:
                d['p'] = 1
            else:
                d['p'] = 0

            # Optimize data transfered removing duplicates on main class names
            # m_c_n_en_value = getattr(getattr(current_element, 'category_class'), 'name_en')
            m_c_n_en_value = getattr(getattr(current_element, 'category_class'), 'name_fr')
            if is_it_public or not prev_d['m_c_n_en'] == m_c_n_en_value:
                prev_d['m_c_n_en'] = d['m_c_n_en'] = m_c_n_en_value
            # m_c_n_fr_value = getattr(getattr(current_element, 'category_class'), 'name_fr')
            m_c_n_fr_value = getattr(getattr(current_element, 'category_class'), 'name_fr')
            if is_it_public or not prev_d['m_c_n_fr'] == m_c_n_fr_value:
                prev_d['m_c_n_fr'] = d['m_c_n_fr'] = m_c_n_fr_value

            # m_c_n_nl_value = getattr(getattr(current_element, 'category_class'), 'name_nl')
            m_c_n_nl_value = getattr(getattr(current_element, 'category_class'), 'name_nl')
            if is_it_public or not prev_d['m_c_n_nl'] == m_c_n_nl_value:
                prev_d['m_c_n_nl'] = d['m_c_n_nl'] = m_c_n_nl_value
            d['s_c_id'] = getattr(getattr(current_element, 'secondary_category_class'), 'id')

            # Optimize data transfered removing duplicates on main class names
            # s_c_n_en_value = getattr(getattr(current_element, 'secondary_category_class'), 'name_en')
            s_c_n_en_value = getattr(getattr(current_element, 'secondary_category_class'), 'name_fr')
            if is_it_public or not prev_d['s_c_n_en'] == s_c_n_en_value:
                d['s_c_n_en'] = s_c_n_en_value
            # s_c_n_fr_value = getattr(getattr(current_element, 'secondary_category_class'), 'name_fr')
            s_c_n_fr_value = getattr(getattr(current_element, 'secondary_category_class'), 'name_fr')
            if is_it_public or not prev_d['s_c_n_fr'] == s_c_n_fr_value:
                d['s_c_n_fr'] = s_c_n_fr_value
            # s_c_n_nl_value = getattr(getattr(current_element, 'secondary_category_class'), 'name_nl')
            s_c_n_nl_value = getattr(getattr(current_element, 'secondary_category_class'), 'name_nl')
            if is_it_public or not prev_d['s_c_n_nl'] == s_c_n_nl_value:
                d['s_c_n_nl'] = s_c_n_nl_value

            list_of_elements_as_json.append(d)
        return json.dumps(list_of_elements_as_json)

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


class ReportReopenReason(ReportComment):
    NOT_REPAIRED = 1
    BADLY_REPAIRED = 2
    OTHER = 3
    REASON_CHOICES = (
        (NOT_REPAIRED, _("Not repaired")),
        (BADLY_REPAIRED, _("Badly repaired")),
        (OTHER, _("Other"))
    )
    reason = models.IntegerField(choices=REASON_CHOICES)

@receiver(post_save, sender=ReportReopenReason)
def report_reopen_reason_notify(sender, instance, **kwargs):

    if not kwargs['created']:
        return

    report = instance.report
    user   = instance.created_by

    ReportEventLog(
        report=report,
        event_type=ReportEventLog.REOPEN_REQUEST,
        user=user,
    ).save()

    # Send notifications to group or members according to group configuration
    mail_config = report.responsible_department.get_mail_config()

    if not mail_config.digest_other:
        recipients = mail_config.get_manager_recipients(user)

        for email in recipients:
            ReportNotification(
                content_template='notify-reopen-request',
                recipient_mail=email,
                related=report,
            ).save(updater=user, reopen_reason=instance)

    # Notify requester if not pro
    if not user.is_pro():
        ReportNotification(
            content_template='acknowledge-reopen-request',
            recipient_mail=user.email,
            related=report,
        ).save(updater=user, reopen_reason=instance)

class ReportNotification(models.Model):
    recipient_mail = models.CharField(max_length=200, null=True)
    recipient = models.ForeignKey(FMSUser, related_name="notifications", null=True, blank=True)
    sent_at = models.DateTimeField(auto_now_add=True)
    success = models.BooleanField()
    error_msg = models.TextField()
    content_template = models.CharField(max_length=40)
    reply_to = models.CharField(max_length=200, null=True)

    related = generic.GenericForeignKey('related_content_type', 'related_object_id')
    related_content_type = models.ForeignKey(ContentType)
    related_object_id = models.PositiveIntegerField()

    def save(self, *args, **kwargs):
        old_responsible = None
        updater = None
        comment = None
        files = None
        date_planned = None
        merged_with = None
        reopen_reason = None

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
        if 'date_planned' in kwargs:
            date_planned = kwargs['date_planned']
            del kwargs['date_planned']
        if 'reopen_reason' in kwargs:
            reopen_reason = kwargs['reopen_reason']
            del kwargs['reopen_reason']

        if self.related.merged_with:
            merged_with = self.related.merged_with

        if not self.recipient_mail:
            self.recipient_mail = self.recipient.email

        try:
            if not self.recipient_mail:
                raise Exception("No email recipient")

            recipients = (self.recipient_mail,)

            template_mail = self.content_template

            comment = comment.text if comment else ''
            subject, html, text = transform_notification_template(template_mail, self.related, self.recipient, old_responsible=old_responsible, updater=updater, comment=comment, date_planned=date_planned, merged_with=merged_with, reopen_reason=reopen_reason)

            if self.reply_to:
                msg = EmailMultiAlternatives(subject, text, settings.DEFAULT_FROM_EMAIL, recipients, headers={"Reply-To": self.reply_to})
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


def user_to_display_public(related):
    if related and hasattr(related, 'fmsuser'):
        user = related
        if user.fmsuser.is_citizen():
            return _("a citizen")

        elif user.fmsuser.is_pro():
            return user.fmsuser.get_organisation()

    elif hasattr(related, 'dependency') and related.dependency:
        return related.dependency

    else:
        return related


class ReportEventLog(models.Model):

    # List of event types
    REFUSE = 1
    CLOSE = 2
    SOLVE_REQUEST = 3
    MANAGER_ASSIGNED = 4
    #~ MANAGER_CHANGED = 5  # deprecated
    VALID = 6
    ENTITY_ASSIGNED = 7
    #~ ENTITY_CHANGED = 8  # deprecated
    CONTRACTOR_ASSIGNED = 9
    CONTRACTOR_CHANGED = 10
    APPLICANT_ASSIGNED = 11
    APPLICANT_CHANGED = 12
    #~ APPLICANT_CONTRACTOR_CHANGE = 13  # deprecated
    CREATED = 14
    UPDATED = 15
    UPDATE_PUBLISHED = 16
    PLANNED = 17
    MERGED = 18
    REOPEN = 19
    REOPEN_REQUEST = 20
    BECAME_PRIVATE = 21
    BECAME_PUBLIC = 22

    EVENT_TYPE_CHOICES = (
        (REFUSE, _("Refuse")),
        (CLOSE, _("Close")),
        (SOLVE_REQUEST, _("Mark as Done")),
        (MANAGER_ASSIGNED, _("Manager assigned")),
        # (MANAGER_CHANGED,_("Manager changed")),
        (VALID, _("Valid")),
        (ENTITY_ASSIGNED, _('Organisation assigned')),
        # (ENTITY_CHANGED, _('Organisation changed')),
        (CONTRACTOR_ASSIGNED, _('Contractor assigned')),
        (CONTRACTOR_CHANGED, _('Contractor changed')),
        (APPLICANT_ASSIGNED, _('Applicant assigned')),
        (APPLICANT_CHANGED, _('Applicant changed')),
        # (APPLICANT_CONTRACTOR_CHANGE, _('Applicant contractor changed')),
        (CREATED, _("Created")),
        (UPDATED, _("Updated")),
        (UPDATE_PUBLISHED, _("Update published")),
        (PLANNED, _("Planned")),
        (MERGED, _("Merged")),
        (REOPEN, _("Reopen")),
        (REOPEN_REQUEST, _("Reopen request")),
        (BECAME_PRIVATE, _("Became private")),
        (BECAME_PUBLIC, _("Became public")),
    )
    EVENT_TYPE_TEXT = {
        REFUSE: _("Report refused by {user}"),
        CLOSE: _("Report closed by {user}"),
        SOLVE_REQUEST: _("Report pointed as solved"),
        MANAGER_ASSIGNED: _("Report as been assigned to {related_new}"),
        # MANAGER_CHANGED: _("Report as change manager from {related_old} to {related_new}"),
        VALID: _("Report has been approved by {user}"),
        ENTITY_ASSIGNED: _('{related_new} is responsible for the report'),
        # ENTITY_CHANGED: _('{related_old} give responsibility to {related_new}'),
        APPLICANT_ASSIGNED: _('Applicant {related_new} is assigned to the report'),
        APPLICANT_CHANGED: _('Applicant changed from {related_old} to {related_new}'),
        CONTRACTOR_ASSIGNED: _('Contractor {related_new} is assigned to the report'),
        CONTRACTOR_CHANGED: _('Contractor changed from {related_old} to {related_new}'),
        # APPLICANT_CONTRACTOR_CHANGE: _('Applicant contractor change from {related_old} to {related_new}'),
        CREATED: _("Report created by {user}"),
        UPDATED: _("Report updated by {user}"),
        UPDATE_PUBLISHED: _("Informations published by {user}"),
        PLANNED: _("Report planned to {date_planned}"),
        MERGED: _("Report merged with report #{merged_with_id}"),
        REOPEN: _("Report reopen by {user}"),
        REOPEN_REQUEST: _("Request to reopen report made by {user}"),
        BECAME_PRIVATE: _("Report became private by {user}"),
        BECAME_PUBLIC: _("Report became public by {user}"),
    }
    STATUS_EVENTS = (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13)

    PUBLIC_VISIBLE_TYPES = [REFUSE, CLOSE, VALID, APPLICANT_ASSIGNED, APPLICANT_CHANGED, ENTITY_ASSIGNED, CREATED, MERGED, UPDATE_PUBLISHED, REOPEN, REOPEN_REQUEST, BECAME_PRIVATE, BECAME_PUBLIC]
    PRO_VISIBLE_TYPES = PUBLIC_VISIBLE_TYPES + [MANAGER_ASSIGNED, CONTRACTOR_ASSIGNED, CONTRACTOR_CHANGED, SOLVE_REQUEST, UPDATED, PLANNED]

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

    merged_with_id = models.PositiveIntegerField(null=True)

    class Meta:
        ordering = ['event_at', ]

    def __unicode__(self):
        user_to_display = _("a citizen")

        if self.user:
            if self.user.fmsuser.is_citizen():
                user_to_display = self.user.get_full_name() or self.user

            if self.user.fmsuser.is_pro():
                user_to_display = u'%s %s' % (self.user.fmsuser.get_organisation(), self.user.get_full_name() or self.user)

        return self.EVENT_TYPE_TEXT[self.event_type].format(
            user=user_to_display,
            organisation=self.organisation,
            related_new=self.related_new,
            related_old=self.related_old,
            date_planned=self.value_old,
            merged_with_id=self.merged_with_id,
        )

    def get_public_activity_text(self):

        return self.EVENT_TYPE_TEXT[self.event_type].format(
            user=user_to_display_public(self.user),
            organisation=user_to_display_public(self.organisation),
            related_new=user_to_display_public(self.related_new),
            related_old=user_to_display_public(self.related_old),
            date_planned=self.value_old,
            merged_with_id=self.merged_with_id,
        )

    def get_status(self):
        return self.EVENT_TYPE_CHOICES[self.event_type][1]

    def is_public_visible(self):
        return self.event_type in ReportEventLog.PUBLIC_VISIBLE_TYPES

    def is_pro_visible(self):
        return self.event_type in ReportEventLog.PRO_VISIBLE_TYPES


@receiver(pre_save, sender=ReportEventLog)
def eventlog_init_values(sender, instance, **kwargs):
    if instance.report:

        if not instance.status_new:
            instance.status_new = instance.report.status

        if not instance.status_old and hasattr(instance.report, '__former'):
            instance.status_old = instance.report.__former["status"]

        if not hasattr(instance, "organisation"):
            instance.organisation = instance.report.responsible_entity

        if not hasattr(instance, "user"):
            instance.user = instance.report.modified_by

        if hasattr(instance.report, '__former') and instance.report.date_planned != instance.report.__former["date_planned"]:
            instance.value_old = instance.report.get_date_planned()

        if hasattr(instance.report, '__former') and instance.report.merged_with != instance.report.__former["merged_with"]:
            instance.merged_with_id = instance.report.merged_with.id


class ZipCodeManager(models.Manager):
    def get_query_set(self):
        return super(ZipCodeManager, self).get_query_set().select_related('commune')


class ParticipateZipCodeManager(ZipCodeManager):
    def get_query_set(self):
        return super(ParticipateZipCodeManager, self).get_query_set().filter(commune__active=True)


class ZipCode(models.Model):
    __metaclass__ = TransMeta

    commune = models.ForeignKey(OrganisationEntity, related_name="zipcode")
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


@receiver(pre_save, sender=FaqEntry)
def save(sender, instance, **kwargs):
    if not instance.order:
        instance.order = FaqEntry.objects.all().aggregate(models.Max('order'))['order__max'] + 1


class FaqMgr(object):

    def incr_order(self, faq_entry):
        if faq_entry.order == 1:
            return
        other = FaqEntry.objects.get(order=faq_entry.order - 1)
        self.swap_order(other[0], faq_entry)

    def decr_order(self, faq_entry):
        other = FaqEntry.objects.filter(order=faq_entry.order + 1)
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
    __metaclass__ = TransMeta
    label = models.CharField(verbose_name=_('Label'), max_length=100, null=False)
    model_class = models.CharField(verbose_name=_('Related model class name'), max_length=100, null=False)
    model_field = models.CharField(verbose_name=_('Related model field'), max_length=100, null=False)
    code = models.CharField(max_length=50, null=False)

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


class OrganisationEntitySurface(models.Model):
    urbis_id = models.IntegerField(null=True, blank=True)
    version_id = models.IntegerField(null=True, blank=True)
    owner = models.ForeignKey(OrganisationEntity)
    geom = models.GeometryField(null=False, srid=31370, blank=False)

    objects = models.GeoManager()


class MailNotificationTemplate(models.Model):
    name = models.CharField(max_length=50, help_text="Technical name")
    __metaclass__ = TransMeta
    content = models.TextField(blank=True, verbose_name="Content")
    title = models.CharField(max_length=100, blank=True, verbose_name="Subject")

    class Meta:
        translate = ('content', 'title')


class Page(models.Model):
    __metaclass__ = TransMeta

    title = models.CharField(max_length=100, verbose_name="Title")
    slug = models.CharField(max_length=100, verbose_name="Slug")
    content = RichTextField(verbose_name="Content")

    history = HistoricalRecords()

    class Meta:
        translate = ('content', 'title', 'slug')

# pre_save.connect(autoslug_transmeta('title', 'slug'), weak=False, sender=Page)
