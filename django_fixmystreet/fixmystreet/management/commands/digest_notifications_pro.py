from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.core.management.base import BaseCommand, CommandError
from django.template.loader import render_to_string

from optparse import make_option

from django.db.models import Q

from django_fixmystreet.fixmystreet.models import GroupMailConfig, OrganisationEntity, ReportEventLog, UserOrganisationMembership

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
        # Date of yesterday (or specific date)
        if options['date']:
            YESTERDAY = datetime.datetime.strptime(options['date'], "%d/%m/%Y").date()
        else:
            YESTERDAY = datetime.date.today() - datetime.timedelta(days=1)

        logger.info('DIGEST OF NOTIFICATIONS FOR ACTVITIES OF %s' % YESTERDAY)

        # All group mail configurations with at least 1 digest config
        group_mail_configs = GroupMailConfig.objects.filter(group__type=OrganisationEntity.DEPARTMENT).filter(Q(digest_closed=True) | Q(digest_created=True) | Q(digest_inprogress=True) | Q(digest_other=True))
        print 'group_mail_configs', group_mail_configs

        # All group having digest config
        groups = group_mail_configs.values_list('group', flat=True)
        print 'groups', groups

        # All events of yesterday related to groups
        events_yesterday = ReportEventLog.objects.filter(event_at__contains=YESTERDAY, report__responsible_department__in=groups)
        print 'events_yesterday', events_yesterday

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

            # Render digest mail
            digests_notifications = render_to_string("emails/digest.txt", {'activities_list': activities_list})

            logger.info('Sending digest to %s' % recipients)
            msg = EmailMultiAlternatives("Digest of your notifications", digests_notifications, settings.DEFAULT_FROM_EMAIL, recipients)

            msg.send()
