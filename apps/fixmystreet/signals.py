# File imported from __init.py
import re
import datetime
from datetime import timedelta
from exceptions import Exception
from transmeta import TransMeta

from django.db.models.signals import pre_save, post_save, pre_delete, post_delete
from django.dispatch import receiver
from django.contrib.auth.models import User

from apps.fixmystreet.models import *
from .utils import autoslug_transmeta

import logging
logger = logging.getLogger("fixmystreet")

#############################################################
#############################################################
# Signals for FMSUser
#############################################################
#############################################################
#pre_save
@receiver(pre_save, sender=FMSUser)
def populate_username(sender, instance, **kwargs):
    """populate username with email"""
    if instance.email and instance.username != instance.email:
        instance.username = instance.email
#############################################################
#post_save
#############################################################
#pre_delete
#############################################################
#post_delete


#############################################################
#############################################################
# Signals for OrganisationEntity
#############################################################
#############################################################
#pre_save
pre_save.connect(autoslug_transmeta('name', 'slug'), weak=False, sender=OrganisationEntity)
#############################################################
#post_save
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
#############################################################
#pre_delete
@receiver(pre_delete, sender=OrganisationEntity)
def organisationentity_delete(sender, instance, **kwargs):
    # Delete all memberships associated
    memberships = UserOrganisationMembership.objects.filter(organisation=instance)

    for membership in memberships:
        membership.delete()
#############################################################
#post_delete


#############################################################
#############################################################
# Signals for Report
#############################################################
#############################################################
#pre_save
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
    # Do not auto assign if it's NOT a new report
    if Report.objects.filter(pk=instance.pk).exists():
        return

    # Auto-dispatching according to group and regional or communal address
    entity = instance.secondary_category.get_organisation(instance.address_regional)

    if entity:
        instance.responsible_entity = entity

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

@receiver(pre_save, sender=Report)
def webhook_assignment(sender, instance, **kwargs):
    """
    Checks whether the report is being assigned to someone else.

    This fires/delegates to the hook. The hook is responsible to contact third-parties as necessary.
    """
    from apps.webhooks import outbound
    assignment_is_changed = instance.contractor and instance.__former['contractor'] != instance.contractor
    if kwargs['raw'] or not assignment_is_changed or not instance.is_in_progress():
        return

    webhook = outbound.ReportAssignmentRequestOutWebhook(instance, third_party=instance.contractor)
    webhook.fire()

#############################################################
#post_save
@receiver(post_save, sender=Report)
def webhook_transfer(sender, instance, **kwargs):
    """
    Checks whether the report is being transferred to someone else.

    This fires/delegates to the hook. The hook is responsible to contact third-parties as necessary.

    Must be post_save to allow auto-dispatching to third party when a new report is created. Without this post save, report id needed to generate the PDF is missing.
    """
    from apps.webhooks import outbound

    is_transferred = instance.responsible_department and instance.__former['responsible_department'] != instance.responsible_department

    if not kwargs['raw'] and is_transferred and (instance.is_created() or instance.is_in_progress()):
        webhook = outbound.ReportTransferRequestOutWebhook(instance, third_party=instance.responsible_department)
        webhook.fire()

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
#############################################################
#pre_delete
#############################################################
#post_delete


#############################################################
#############################################################
# Signals for ReportFile
#############################################################
#############################################################
#pre_save
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
#############################################################
#post_save
@receiver(post_save, sender=ReportFile)
def report_file_notify(sender, instance, **kwargs):
    init_report_overview(sender, instance, **kwargs)
    report_attachment_created(sender, instance, **kwargs)
    report_attachment_published(sender, instance, **kwargs)
#############################################################
#pre_delete
#############################################################
#post_delete
@receiver(post_delete, sender=ReportFile)
def report_file_delete(sender, instance, **kwargs):
    # Pass false so FileField doesn't save the model.
    if instance.file:
        logger.info('delete file: %s' % instance.file.path)
        instance.file.delete(False)

    if instance.image:
        logger.info('delete image: %s' % instance.image.path)
        instance.image.delete(False)


#############################################################
#############################################################
# Signals for ReportSubscription
#############################################################
#############################################################
#pre_save
#############################################################
#post_save
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
#############################################################
#pre_delete
#############################################################
#post_delete


#############################################################
#############################################################
# Signals for ReportMainCategoryClass
#############################################################
#############################################################
#pre_save
pre_save.connect(autoslug_transmeta('name', 'slug'), weak=False, sender=ReportMainCategoryClass)
#############################################################
#post_save
#############################################################
#pre_delete
#############################################################
#post_delete


#############################################################
#############################################################
# Signals for ReportSecondaryCategoryClass
#############################################################
#############################################################
#pre_save
pre_save.connect(autoslug_transmeta('name', 'slug'), weak=False, sender=ReportSecondaryCategoryClass)
#############################################################
#post_save
#############################################################
#pre_delete
#############################################################
#post_delete


#############################################################
#############################################################
# Signals for ReportCategory
#############################################################
#############################################################
#pre_save
pre_save.connect(autoslug_transmeta('name', 'slug'), weak=False, sender=ReportCategory)
#############################################################
#post_save
#############################################################
#pre_delete
#############################################################
#post_delete


#############################################################
#############################################################
# Signals for ReportEventLog
#############################################################
#############################################################
#pre_save
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
#############################################################
#post_save
#############################################################
#pre_delete
#############################################################
#post_delete


#############################################################
#############################################################
# Signals for Page
#############################################################
#############################################################
#pre_save
# pre_save.connect(autoslug_transmeta('title', 'slug'), weak=False, sender=Page)
#############################################################
#post_save
#############################################################
#pre_delete
#############################################################
#post_delete


#############################################################
#############################################################
# Signals for ReportAttachment
#############################################################
#############################################################
#pre_save
#############################################################
#post_save
# Initialise instance.report.thumbnail with the first public photo. For pro and citizen
@receiver(post_save, sender=ReportAttachment)
def init_report_overview(sender, instance, **kwargs):

    # Thumbnail for citizen
    images_public = instance.report.active_files().filter(file_type=ReportFile.IMAGE)
    if images_public.exists():
        instance.report.thumbnail = images_public[0].image.thumbnail.url
    else:
        instance.report.thumbnail = None

    # Thumbnail for pro
    images_pro = instance.report.files().filter(logical_deleted=False, file_type=ReportFile.IMAGE).order_by('-modified')
    if images_pro.exists():
        instance.report.thumbnail_pro = images_pro[0].image.thumbnail.url
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

        recipients = []

        # Send notifications to contractor
        if report.contractor and report.contractor.email:
            recipients += [report.contractor.email]

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
            recipients += mail_config.get_manager_recipients(user)

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
#############################################################
#pre_delete
#############################################################
#post_delete


#############################################################
#############################################################
# Signals for ReportComment
#############################################################
#############################################################
#pre_save
#############################################################
#post_save
@receiver(post_save, sender=ReportComment)
def report_comment_notify(sender, instance, **kwargs):
    report_attachment_created(sender, instance, **kwargs)
    report_attachment_published(sender, instance, **kwargs)
#############################################################
#pre_delete
#############################################################
#post_delete


#############################################################
#############################################################
# Signals for ReportReopenReason
#############################################################
#############################################################
#pre_save
#############################################################
#post_save
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
#############################################################
#pre_delete
#############################################################
#post_delete


#############################################################
#############################################################
# Signals for XXXXXXXX
#############################################################
#############################################################
#pre_save
#############################################################
#post_save
#############################################################
#pre_delete
#############################################################
#post_delete
