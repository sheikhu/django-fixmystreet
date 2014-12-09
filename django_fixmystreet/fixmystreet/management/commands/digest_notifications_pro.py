from django.core.management.base import BaseCommand, CommandError

from optparse import make_option

from django.db.models import Q
from django_fixmystreet.fixmystreet.models import FMSUser

from django_fixmystreet.fixmystreet.utils import send_digest

import datetime
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Send digest of activities of the previous day to all responsibles'

    option_list = BaseCommand.option_list + (
        make_option('--send',
            action='store_true',
            dest='send',
            default=False,
            help='Send digest by mails'),

        make_option('--date',
            action='store',
            dest='date',
            default=False,
            help='Specify date of digest. Format: 30/12/2012')
        )

    def handle(self, *args, **options):
        from django_fixmystreet.fixmystreet.models import GroupMailConfig, OrganisationEntity, ReportEventLog, UserOrganisationMembership

        # Date of yesterday (or specific date)
        if options['date']:
            YESTERDAY = datetime.datetime.strptime(options['date'], "%d/%m/%Y").date()
        else:
            YESTERDAY = datetime.date.today() - datetime.timedelta(days=1)

        logger.info('DIGEST OF NOTIFICATIONS FOR ACTVITIES OF %s' % YESTERDAY)

        # All group mail configurations with at least 1 digest config
        group_mail_configs = GroupMailConfig.objects.filter(group__type=OrganisationEntity.DEPARTMENT).filter(Q(digest_closed=True) | Q(digest_created=True) | Q(digest_inprogress=True) | Q(digest_other=True))
        logger.info('group_mail_configs %s' % group_mail_configs)

        # All group having digest config
        groups = group_mail_configs.values_list('group', flat=True)
        logger.info('groups %s' % groups)

        # All events of yesterday related to groups
        events_yesterday = ReportEventLog.objects.filter(event_at__contains=YESTERDAY, report__responsible_department__in=groups)
        logger.info('events_yesterday %s' % events_yesterday)

        for mail_config in group_mail_configs:
            group = mail_config.group

            # Returns all activities of yesterday grouped by reports where and related to group
            activities_list = events_yesterday.filter(report__responsible_department=group)

            if not activities_list:
                continue

            # Send digest to responsibles according to mail config
            recipients = mail_config.get_manager_recipients()

            logger.info('Digest of %s %s' % (group, recipients))
            logger.info('   Number of activities: %s' % activities_list.count())

            for activity in activities_list:
                logger.info('   %s %s %s' % (activity.event_at, activity.report.id, activity))

            # If NOT option send, do not send email
            if not options['send']:
                continue

            for recipient in recipients:
                # Because recipients are email and can be a user or group email, have to mock a user
                user = FMSUser()
                user.email = recipient
                user.is_pro = lambda: True
                user.last_used_language = "fr"

                # Render and send the digest by mail
                send_digest(user, activity, activities_list, YESTERDAY)
