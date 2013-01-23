from django.utils import simplejson
from datetime import datetime as dt
from smtplib import SMTPException
import logging

from django.db.models.signals import pre_save, post_save, post_init
from django.dispatch import receiver
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _, activate, ugettext
from django.contrib.auth.models import User
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
from email.MIMEImage import MIMEImage
from django.contrib.auth.signals import user_logged_in

from transmeta import TransMeta
from simple_history.models import HistoricalRecords
from django_fixmystreet.fixmystreet.utils import FixStdImageField, get_current_user, save_file_to_server, autoslug_transmeta, resize_image
from django_extensions.db.models import TimeStampedModel



class UserTrackedModel(TimeStampedModel):
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

    telephone = models.CharField(max_length=20,null=True)
    last_used_language = models.CharField(max_length=10,null=True)
    #hash_code = models.IntegerField(null=True)# used by external app for secure sync, must be random generated
    quality = models.IntegerField(choices=REPORT_QUALITY_CHOICES, null=True, blank=True)


    agent = models.BooleanField(default=False)
    manager = models.BooleanField(default=False)
    leader = models.BooleanField(default=False)

    applicant = models.BooleanField(default=False)
    contractor = models.BooleanField(default=False)

    logical_deleted = models.BooleanField(default=False)

    categories = models.ManyToManyField('ReportCategory', related_name='type')
    organisation = models.ForeignKey('OrganisationEntity', related_name='team', null=True)

    # history = HistoricalRecords()

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
             return _('ANONYMOUS')
        else:
             return self.first_name+' '+self.last_name

    def get_organisation(self):
        '''Return the user organisation and its dependency in case of contractor'''
        if self.contractor == True:
             return self.organisation.dependency
        else:
             return self.organisation

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
        d['organisation'] = getattr(self.get_organisation(), 'id')
        return simplejson.dumps(d)
    def get_number_of_created_reports(self):
        userConnectedOrganisation = self.organisation
        reports = Report.objects.filter(responsible_entity=userConnectedOrganisation).filter(status=Report.CREATED)
        return reports.count()
    def get_number_of_in_progress_reports(self):
        connectedOrganisation = self.organisation
        userConnectedOrganisation = connectedOrganisation
        #if the user is an executeur de travaux then user the dependent organisation id
        if (self.contractor == True):
            reports = Report.objects.filter(contractor=self.organisation).filter(status__in=Report.REPORT_STATUS_IN_PROGRESS)
        else:
            reports = Report.objects.filter(responsible_entity=userConnectedOrganisation).filter(status__in=Report.REPORT_STATUS_IN_PROGRESS)
        return reports.count()
    def get_number_of_closed_reports(self):
        connectedOrganisation = self.organisation
        userConnectedOrganisation = connectedOrganisation
        #if the user is an executeur de travaux then user the dependent organisation id
        if (self.contractor == True):
            reports = Report.objects.filter(contractor=self.organisation).filter(status__in=Report.REPORT_STATUS_CLOSED)
        else:
            reports = Report.objects.filter(responsible_entity=userConnectedOrganisation).filter(status__in=Report.REPORT_STATUS_CLOSED)

        return reports.count()
    def get_number_of_subscriptions(self):
        subscriptions = ReportSubscription.objects.filter(subscriber_id=self.id)
        return subscriptions.count()

User._meta.get_field_by_name('email')[0]._unique = True
User._meta.get_field_by_name('email')[0].null = True

@receiver(post_save, sender=FMSUser)
def create_matrix_when_creating_first_manager(sender, instance, **kwargs):
    """This method is used to create the security matrix when creating the first manager of the entity"""
    #If this is the first user created and of type gestionnaire then assign all reportcategories to him
    if (instance.manager == True):
       #if we have just created the first one, then apply all type to him
       if instance.organisation.team.filter(manager=True).count() == 1:
          for type in ReportCategory.objects.all():
             instance.categories.add(type)


class OrganisationEntity(UserTrackedModel):
    __metaclass__= TransMeta
    name = models.CharField(verbose_name=_('Name'), max_length=100, null=False)
    slug = models.SlugField(verbose_name=_('Slug'), max_length=100)

    phone = models.CharField(max_length=32)
    commune = models.BooleanField(default=False)
    region = models.BooleanField(default=False)
    subcontractor = models.BooleanField(default=False)
    applicant = models.BooleanField(default=False)
    dependency = models.ForeignKey('OrganisationEntity', related_name='parent', null=True, blank=True)
    feature_id = models.CharField(max_length=25, null=True, blank=True)

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

# @receiver(user_logged_in)
# def lang(sender, **kwargs):
#     lang_code = kwargs['user'].fmsuser.get_langage()
#     kwargs['request'].session['django_language'] = lang_code.lower()
#     kwargs['request'].LANGUAGE_CODE = lang_code.lower()
#     activate(lang_code.lower())

class ReportManager(models.GeoManager):
    def get_query_set(self):
        return super(ReportManager, self).get_query_set().select_related('category', 'secondary_category', 'secondary_category__secondary_category_class', 'responsible_entity', 'contractor', 'responsible_manager', 'citizen')


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

    REPORT_STATUS_SETTABLE_TO_SOLVED = (IN_PROGRESS, MANAGER_ASSIGNED, APPLICANT_RESPONSIBLE, CONTRACTOR_ASSIGNED)
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
    address_regional = models.BooleanField(default=False)
    postalcode = models.CharField(max_length=4, verbose_name=_("Postal Code"))
    description = models.TextField(null=True, blank=True)
    category = models.ForeignKey('ReportMainCategoryClass', null=True, verbose_name=_("Category"), blank=True)
    secondary_category = models.ForeignKey('ReportCategory', null=True, verbose_name=_("Category"), blank=True)

    fixed_at = models.DateTimeField(null=True, blank=True)

    hash_code = models.IntegerField(null=True, blank=True) # used by external app for secure sync, must be random generated

    citizen = models.ForeignKey(FMSUser, null=True, related_name='citizen_reports', blank=True)
    refusal_motivation = models.TextField(null=True, blank=True)
    mark_as_done_motivation = models.TextField(null=True, blank=True)
    #responsible = models.ForeignKey(OrganisationEntity, related_name='in_charge_reports', null=False)
    responsible_entity = models.ForeignKey('OrganisationEntity', related_name='reports_in_charge', null=True, blank=True)
    contractor = models.ForeignKey(OrganisationEntity, related_name='assigned_reports', null=True, blank=True)
    responsible_manager = models.ForeignKey(FMSUser, related_name='reports_in_charge', null=True, blank=True)
    responsible_manager_validated = models.BooleanField(default=False)

    valid = models.BooleanField(default=False)
    private = models.BooleanField(default=True)
    #photo = FixStdImageField(upload_to="photos", blank=True, size=(380, 380), thumbnail_size=(66, 50))
    photo = models.FileField(upload_to="photos", blank=True)
    close_date = models.DateTimeField(null=True, blank=True)

    objects = ReportManager()

    history = HistoricalRecords()
    
    def get_marker(self):
        user = get_current_user()

        marker_color = "green" #default color
        if (self.is_in_progress()):
            marker_color = "orange"
            if user and user.is_authenticated():    
                if self.status in Report.REPORT_STATUS_ASSIGNED:
                    marker_color = "orange-executed" 
        elif (self.is_created()):
            marker_color = "red"

        if user and user.is_authenticated():
    	    if self.is_regional():
                return "images/reg-pin-"+marker_color+"-XS.png"
            elif self.is_pro():
                return "images/pro-pin-"+marker_color+"-XS.png"
            else:
                return "images/pin-"+marker_color+"-XL.png"
        else:
            if self.is_pro():
                return "images/pro-pin-"+marker_color+"-XS.png"
            else:
                return "images/pin-"+marker_color+"-XL.png"

    def is_regional(self):
        return self.address_regional == True

    def is_pro(self):
        return self.citizen == None
    
    def __unicode__(self):
        return self.display_category()

    def get_address_city_name(self):
        return ZipCode.objects.get(code=self.postalcode).name

    def display_category(self):
        return self.category.name + " / " + self.secondary_category.secondary_category_class.name + " : " + self.secondary_category.name

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
        slug = self.secondary_category.slug + '-' + self.secondary_category.secondary_category_class.slug + '-' + self.category.slug + '-' + self.responsible_entity.slug
        return reverse("report_show",kwargs={'report_id':self.id,'slug': slug })

    def get_absolute_url_pro(self):
        #TODO determine when pro and no-pro url must be returned
        slug = self.secondary_category.slug + '-' + self.secondary_category.secondary_category_class.slug + '-' + self.category.slug + '-' + self.responsible_entity.slug
        return reverse("report_show_pro", kwargs={'report_id':self.id,'slug': slug })

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

    def is_in_progress(self):
        return self.status in Report.REPORT_STATUS_IN_PROGRESS

    def is_closed(self):
        return self.status in Report.REPORT_STATUS_CLOSED

    def thumbnail(self):
        reportImages = ReportFile.objects.filter(report_id=self.id, file_type=ReportFile.IMAGE).filter(logical_deleted=False)
        if (not self.is_created()):
            if (reportImages.__len__() > 0):
                return reportImages[0].file.url

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
            "address_regional": self.address_regional,
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


@receiver(pre_save, sender=Report)
def track_former_value(sender, instance, **kwargs):
    """Save former data to compare with new data and track changed values"""
    if instance.id:
        former_report = Report.objects.get(id=instance.id)
        instance.__former = dict((field.name, getattr(former_report, field.name)) for field in Report._meta.fields)
    else:
        instance.__former = dict((field.name, getattr(Report(), field.name)) for field in Report._meta.fields)
    


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

        #Search the right responsible for the current organization.
        users = instance.responsible_entity.team.filter(manager=True, categories=instance.secondary_category)
        if len(users) > 0:
            instance.responsible_manager = users[0]
        else:
            logging.error("no responsible")
        # for currentUser in userCandidates:
        #     userCategories = currentUser.categories.all()
        #     for currentCategory in userCategories:
        #         if (currentCategory == instance.secondary_category):
        #            instance.responsible_manager = currentUser

@receiver(post_save, sender=Report)
def report_notify(sender, instance, **kwargs):
    """
    signal on a report to notify author and manager that the status of the report has changed
    """
    report = instance
    if not kwargs['raw']:
        if report.__former['status'] != report.status:
            if report.status == Report.REFUSED:
                ReportNotification(
                    content_template='send_report_refused_to_creator',
                    recipient=report.citizen or report.created_by,
                    related=report,
                    reply_to = report.responsible_manager.email,
                ).save()

                ReportEventLog(
                    report=report,
                    event_type=ReportEventLog.REFUSE,
                    user=report.responsible_manager,
                ).save()

            elif report.status == Report.PROCESSED:
                for subscription in report.subscriptions.all():
                    ReportNotification(
                        content_template='send_report_closed_to_subscribers',
                        recipient=subscription.subscriber,
                        related=report,
                        reply_to=report.responsible_manager.email,
                    ).save()

                ReportEventLog(
                    report=report,
                    event_type=ReportEventLog.CLOSE,
                    user=report.responsible_manager
                ).save()

            elif report.__former['status'] == Report.CREATED:
                # created => in progress: published by manager
                for subscription in report.subscriptions.all():
                    ReportNotification(
                        content_template='send_report_changed_to_subscribers',
                        recipient=subscription.subscriber,
                        related=report,
                        reply_to=report.responsible_manager.email,
                    ).save()

                ReportEventLog(
                    report=report,
                    event_type=ReportEventLog.PUBLISH,
                    user=report.responsible_manager
                ).save()

            elif report.status == Report.SOLVED:
                ReportNotification(
                    content_template='send_report_fixed_to_gest_resp',
                    recipient=report.responsible_manager,
                    related=report,
                ).save()
                ReportEventLog(
                    report=report,
                    event_type=ReportEventLog.SOLVE_REQUEST
                ).save()
                

            elif report.status == Report.APPLICANT_RESPONSIBLE:
                #Applicant responsible
                ReportNotification(
                    content_template='send_report_assigned_to_app_contr',
                    recipient=FMSUser.objects.filter(organisation_id=report.contractor.id)[0],
                    related=report,
                    reply_to=report.responsible_manager.email
                ).save()
                for subscription in report.subscriptions.all():
                    ReportNotification(
                        content_template='send_report_changed_to_subscribers',
                        recipient=subscription.subscriber,
                        related=report,
                        reply_to=report.responsible_manager.email,
                    ).save()
                ReportEventLog(
                    report=report,
                    event_type=ReportEventLog.APPLICANT_ASSIGNED,
                    related_new=report.contractor
                ).save()


            elif report.status == Report.CONTRACTOR_ASSIGNED:
                #Contractor assigned
                ReportNotification(
                    content_template='send_report_assigned_to_app_contr',
                    recipient=FMSUser.objects.filter(organisation_id=report.contractor.id)[0],
                    related=report,
                    reply_to=report.responsible_manager.email
                ).save()
                for subscription in report.subscriptions.all():
                    ReportNotification(
                        content_template='send_report_changed_to_subscribers',
                        recipient=subscription.subscriber,
                        related=report,
                        reply_to=report.responsible_manager.email,
                    ).save()
                ReportEventLog(
                    report=report,
                    event_type=ReportEventLog.CONTRACTOR_ASSIGNED,
                    related_new=report.contractor
                ).save()

        if report.__former['contractor']!= report.contractor:
            ReportNotification(
                content_template='send_report_assigned_to_app_contr',
                recipient=FMSUser.objects.filter(organisation_id=report.contractor.id)[0],
                related=report,
                reply_to=report.responsible_manager.email
            ).save()
            if report.__former['contractor']:
                ReportNotification(
                    content_template='send_report_deassigned_to_app_contr',
                    recipient=FMSUser.objects.filter(organisation_id=report.__former['contractor'].id)[0],
                    related=report,
                    reply_to=report.responsible_manager.email
                ).save()
            for subscription in report.subscriptions.all():
                    ReportNotification(
                        content_template='send_report_changed_to_subscribers',
                        recipient=subscription.subscriber,
                        related=report,
                        reply_to=report.responsible_manager.email,
                    ).save()
            if report.__former['contractor']:
                if report.__former['status']==Report.CONTRACTOR_ASSIGNED and report.status == Report.CONTRACTOR_ASSIGNED:
                    ReportEventLog(
                        report=report,
                        event_type=ReportEventLog.CONTRACTOR_CHANGED,
                        related_old = report.__former['contractor'],
                        related_new = report.contractor
                    ).save()
                elif report.__former['status']==Report.APPLICANT_RESPONSIBLE and report.status == Report.APPLICANT_RESPONSIBLE:
                    ReportEventLog(
                        report=report,
                        event_type=ReportEventLog.APPLICANT_CHANGED,
                        related_old = report.__former['contractor'],
                        related_new = report.contractor
                    ).save()
                else:
                    ReportEventLog(
                        report=report,
                        event_type=ReportEventLog.APPLICANT_CONTRACTOR_CHANGE,
                        related_old = report.__former['contractor'],
                        related_new = report.contractor
                    ).save()

        #Report Creation
        if report.__former['responsible_manager'] != report.responsible_manager:
            ReportNotification(
                content_template='send_report_creation_to_gest_resp',
                recipient=report.responsible_manager,
                related=report,
            ).save()
            for subscription in report.subscriptions.all():
                    ReportNotification(
                        content_template='send_report_changed_to_subscribers',
                        recipient=subscription.subscriber,
                        related=report,
                        reply_to=report.responsible_manager.email,
                    ).save()
            l = ReportEventLog()
            l.report = report
            l.event_type = ReportEventLog.MANAGER_CHANGED if report.__former['responsible_manager'] else ReportEventLog.MANAGER_ASSIGNED
            l.related_old = report.__former['responsible_manager']
            l.related_new = report.responsible_manager
            l.save()

        if report.__former['responsible_entity'] != report.responsible_entity:
            for subscription in report.subscriptions.all():
                    ReportNotification(
                        content_template='send_report_changed_to_subscribers',
                        recipient=subscription.subscriber,
                        related=report,
                        reply_to=report.responsible_manager.email,
                    ).save()
            l = ReportEventLog()
            l.report = report
            l.event_type = ReportEventLog.ENTITY_CHANGED if report.__former['responsible_entity'] else ReportEventLog.ENTITY_ASSIGNED
            l.related_old = report.__former['responsible_entity']
            l.related_new = report.responsible_entity
            l.save()


# @receiver(post_save,sender=Report)
# def report_subscribe_author(sender, instance, **kwargs):
#     """signal on a report to register author as subscriber to his own report"""
#     if kwargs['created'] and not kwargs['raw']:
#         if instance.created_by:
#             ReportSubscription(report=instance, subscriber=instance.created_by.fmsuser).save()



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
    def get_security_level(self, security_level_as_int):
        '''Return the security level key for the given int value'''
        if (self.PUBLIC == security_level_as_int):
            return self.PUBLIC
        if (self.PRIVATE == security_level_as_int):
            return self.PRIVATE
        if (self.CONFIDENTIAL == security_level_as_int):
            return self.CONFIDENTIAL


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
             return 'ANONYMOUS'
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
    file = models.FileField(upload_to="files")
    #image = FixStdImageField(upload_to="files", blank=True, size=(800, 600), thumbnail_size=(66, 50))
    #file = models.FileField(upload_to=generate_filename)
    file_type = models.IntegerField(choices=attachment_type)
    title = models.TextField(max_length=250, null=True, blank=True)
    file_creation_date= models.DateTimeField(null=True)

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
    elif content_type == 'application/msword' or content_type == 'application/vnd.oasis.opendocument.text' or content_type == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
        instance.file_type = ReportFile.WORD
    elif content_type == 'image/png' or content_type == 'image/jpeg':
        instance.file_type = ReportFile.IMAGE
    elif content_type == 'application/vnd.ms-excel' or content_type == 'application/vnd.oasis.opendocument.spreadsheet':
        instance.file_type = ReportFile.EXCEL


@receiver(post_save, sender=ReportFile)
def move_file(sender,instance,**kwargs):
    if kwargs['created']:
        file_type_string =ReportFile.attachment_type[instance.file_type-1][1]
        extension = {1:'pdf',2:'doc',3:'xls',4:'jpg'}[instance.file_type]
        new_destination = save_file_to_server(instance.file,file_type_string,extension,len(ReportFile.objects.filter(report_id=instance.report_id)), instance.report.id)
        instance.file = new_destination
        instance.save()
        if instance.file_type == ReportFile.IMAGE:
            #Resize the image
            resize_image(instance.file.path)


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
    if not kwargs['raw'] and kwargs['created']:
        report = instance.report
        notifiation = ReportNotification(
            content_template='send_subscription_to_subscriber',
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
            d['name_en'] = getattr(current_element, 'name_en')
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
            d['name_en'] = getattr(current_element, 'name_en')
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
            #d['n_en'] = getattr(current_element, 'name_en')
            #d['n_fr'] = getattr(current_element, 'name_fr')
            #d['n_nl'] = getattr(current_element, 'name_nl')
            d['n_en'] = getattr(current_element, 'name')
            d['n_fr'] = getattr(current_element, 'name')
            d['n_nl'] = getattr(current_element, 'name')
            d['m_c_id'] = getattr(getattr(current_element, 'category_class'),'id')

            is_it_public = getattr(current_element, 'public')
            if is_it_public:
                d['p'] = 1
            else:
                d['p'] = 0

            #Optimize data transfered removing duplicates on main class names
            #m_c_n_en_value = getattr(getattr(current_element, 'category_class'), 'name_en')
            m_c_n_en_value = getattr(getattr(current_element, 'category_class'), 'name')
            if is_it_public or not prev_d['m_c_n_en'] == m_c_n_en_value:
                prev_d['m_c_n_en'] = d['m_c_n_en'] = m_c_n_en_value
            #m_c_n_fr_value = getattr(getattr(current_element, 'category_class'), 'name_fr')
            m_c_n_fr_value = getattr(getattr(current_element, 'category_class'), 'name')
            if is_it_public or not prev_d['m_c_n_fr'] == m_c_n_fr_value:
                prev_d['m_c_n_fr'] = d['m_c_n_fr'] = m_c_n_fr_value

            #m_c_n_nl_value = getattr(getattr(current_element, 'category_class'), 'name_nl')
            m_c_n_nl_value = getattr(getattr(current_element, 'category_class'), 'name')
            if is_it_public or not prev_d['m_c_n_nl'] == m_c_n_nl_value:
                prev_d['m_c_n_nl'] = d['m_c_n_nl'] = m_c_n_nl_value
            d['s_c_id'] = getattr(getattr(current_element, 'secondary_category_class'),'id')

            #Optimize data transfered removing duplicates on main class names
            #s_c_n_en_value = getattr(getattr(current_element, 'secondary_category_class'), 'name_en')
            s_c_n_en_value = getattr(getattr(current_element, 'secondary_category_class'), 'name')
            if is_it_public or not prev_d['s_c_n_en'] == s_c_n_en_value:
                prev_d['s_c_n_en'] = d['s_c_n_en'] = s_c_n_en_value
            #s_c_n_fr_value = getattr(getattr(current_element, 'secondary_category_class'), 'name_fr')
            s_c_n_fr_value = getattr(getattr(current_element, 'secondary_category_class'), 'name')
            if is_it_public or not prev_d['s_c_n_fr'] == s_c_n_fr_value:
                prev_d['s_c_n_fr'] = d['s_c_n_fr'] = s_c_n_fr_value
            #s_c_n_nl_value = getattr(getattr(current_element, 'secondary_category_class'), 'name_nl')
            s_c_n_nl_value = getattr(getattr(current_element, 'secondary_category_class'), 'name')
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


@receiver(pre_save, sender=ReportNotification)
def send_notification(sender, instance, **kwargs):
    if not instance.recipient.email:
        instance.error_msg = "No email recipient"
        instance.success = False
        return

    reply_to = settings.DEFAULT_FROM_EMAIL
    if instance.reply_to:
        reply_to = instance.reply_to
    recipients = (instance.recipient.email,)

    data = {
        "related": instance.related,
        "SITE_URL": Site.objects.get_current().domain
    }

    subject, html, text = '', '', ''
    try:
        subject = render_to_string('emails/' + instance.content_template + "/subject.txt", data)
    except TemplateDoesNotExist:
        instance.error_msg = "No subject"
    try:
        text    = render_to_string('emails/' + instance.content_template + "/message.txt", data)
    except TemplateDoesNotExist:
        instance.error_msg = "No content"

    try:
        html    = render_to_string('emails/' + instance.content_template + "/message.html", data)
    except TemplateDoesNotExist:
        pass

    subject = subject.rstrip(' \n\t').lstrip(' \n\t')

    msg = EmailMultiAlternatives(subject, text, settings.EMAIL_FROM_USER, recipients, headers={"Reply-To":reply_to})

    if html:
        msg.attach_alternative(html, "text/html")

    # if self.report.photo:
        # msg.attach_file(self.report.photo.file.name)
    if isinstance(instance.related, Report):
        if instance.related.files():
            for f in instance.related.files():
                if f:
                    if f.file_type == ReportFile.IMAGE and f.is_public:
                        # Open the file
                        fp = open(settings.PROJECT_PATH+f.file.url, 'rb')
                        msgImage = MIMEImage(fp.read())
                        fp.close()
                        # Define the image's ID to reference to it
                        msgImage.add_header('Content-ID', '<image'+str(f.id)+'>')
                        msg.attach(msgImage)
    try:
        msg.send()
        instance.success = True
    except SMTPException as e:
        instance.success = False
        instance.error_msg = str(e)

class ReportEventLog(models.Model):

    # List of event types
    REFUSE = 1
    CLOSE = 2
    SOLVE_REQUEST = 3
    MANAGER_ASSIGNED = 4
    MANAGER_CHANGED = 5
    PUBLISH = 6
    ENTITY_ASSIGNED = 7
    ENTITY_CHANGED = 8
    CONTRACTOR_ASSIGNED = 9
    CONTRACTOR_CHANGED = 10
    APPLICANT_ASSIGNED =11
    APPLICANT_CHANGED = 12
    APPLICANT_CONTRACTOR_CHANGE = 13
    EVENT_TYPE_CHOICES = (
        (REFUSE,_("Refuse")),
        (CLOSE,_("Close")),
        (SOLVE_REQUEST,_("Mark as Done")),
        (MANAGER_ASSIGNED,_("Manager assinged")),
        (MANAGER_CHANGED,_("Manager changed")),
        (PUBLISH,_("Publish")),
        (ENTITY_ASSIGNED, _('Organisation assinged')),
        (ENTITY_CHANGED, _('Organisation changed')),
        (CONTRACTOR_ASSIGNED,_('Contractor assinged')),
        (CONTRACTOR_CHANGED,_('Contractor changed')),
        (APPLICANT_ASSIGNED,_('Applicant assinged')),
        (APPLICANT_CHANGED,_('Applicant changed')),
        (APPLICANT_CONTRACTOR_CHANGE,_('Applicant contractor changed')),
    )
    EVENT_TYPE_TEXT = {
        REFUSE: _("Report refused by {user}"),
        CLOSE: _("Report closed by {user}"),
        SOLVE_REQUEST: _("Report pointed as done"),
        MANAGER_ASSIGNED: _("Report as been assigned to {related_new}"),
        MANAGER_CHANGED: _("Report as change manager from {related_old} to {related_new}"),
        PUBLISH: _("Report has been published by {user}"),
        ENTITY_ASSIGNED: _('{related_new} is responsible for the report'),
        ENTITY_CHANGED: _('{related_old} give responsibility to {related_new}'),
        APPLICANT_ASSIGNED:_('Applicant {related_new} is responsible for the report'),
        APPLICANT_CHANGED:_('Applicant changed from {related_old} to {related_new}'),
        CONTRACTOR_ASSIGNED:_('Contractor {related_new} is responsible for the report'),
        CONTRACTOR_CHANGED:_('Contractor changed from {related_old} to {related_new}'),
        APPLICANT_CONTRACTOR_CHANGE:_('Applicant contractor change from {related_old} to {related_new}'),
    }

    PUBLIC_VISIBLE_TYPES = (REFUSE, CLOSE, SOLVE_REQUEST, MANAGER_ASSIGNED, MANAGER_CHANGED, PUBLISH, ENTITY_ASSIGNED, ENTITY_CHANGED)
    PRO_VISIBLE_TYPES = PUBLIC_VISIBLE_TYPES + (APPLICANT_ASSIGNED, APPLICANT_CHANGED, CONTRACTOR_ASSIGNED, CONTRACTOR_CHANGED, APPLICANT_CONTRACTOR_CHANGE)

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

    def __unicode__(self):
        return self.EVENT_TYPE_TEXT[self.event_type].format(
            user=self.user,
            organisation=self.organisation,
            related_old=self.related_old,
            related_new=self.related_new
        )
    def is_public_visible(self):
        return self.event_type in ReportEventLog.PUBLIC_VISIBLE_TYPES

    def is_pro_visible(self):
        return self.event_type in ReportEventLog.PRO_VISIBLE_TYPES


@receiver(pre_save, sender=ReportEventLog)
def eventlog_init_values(sender, instance, **kwargs):
    if instance.report:

        if instance.status_new == None:
            instance.status_new = instance.report.status

        if instance.status_old == None:
            instance.status_old = instance.report.__former["status"]

        if not hasattr(instance, "organisation"):
            instance.organisation = instance.report.responsible_entity

        if not hasattr(instance, "user"):
            instance.user = instance.report.modified_by


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
