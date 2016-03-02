from django.core.management.base import BaseCommand, CommandError

from optparse import make_option

from apps.fixmystreet.utils import send_digest

import datetime
import logging

logger = logging.getLogger("fixmystreet")

class Command(BaseCommand):
    help = 'Send digest of activities of the previous day to all subscribers'

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
        from apps.fixmystreet.models import ReportEventLog, ReportSubscription

        # Events related to subscriptions
        SUBSCRIPTION_EVENTS = [
            ReportEventLog.REFUSE, ReportEventLog.CLOSE,

            ReportEventLog.VALID, ReportEventLog.REOPEN,

            ReportEventLog.PLANNED, ReportEventLog.MERGED, ReportEventLog.UPDATE_PUBLISHED,

            ReportEventLog.APPLICANT_ASSIGNED, ReportEventLog.CONTRACTOR_ASSIGNED,

            ReportEventLog.MANAGER_ASSIGNED,
        ]

        # Date of yesterday (or specific date)
        if options['date']:
            YESTERDAY = datetime.datetime.strptime(options['date'], "%d/%m/%Y").date()
        else:
            YESTERDAY = datetime.date.today() - datetime.timedelta(days=1)

        logger.info('DIGEST OF SUBSCRIPTIONS FOR ACTVITIES OF %s' % YESTERDAY)

        # All events of yesterday
        events_yesterday = ReportEventLog.objects.filter(event_at__contains=YESTERDAY, event_type__in=SUBSCRIPTION_EVENTS)

        # All reports related to events of yesterday
        reports_list = events_yesterday.order_by('report').distinct('report').values_list('report', flat=True)

        # All subscriptions of reports related to events of yesterday
        subscriptions_list = ReportSubscription.objects.filter(report__id__in=reports_list)
        subscribers_list   = subscriptions_list.distinct('subscriber')

        for subscription in subscribers_list:
            user = subscription.subscriber

            # Returns all activities of yesterday grouped by reports where there are subscriptions with this user
            # If user is citizen, do not get activities of private reports
            activities_list = events_yesterday \
                .filter(report__id__in=subscriptions_list.filter(subscriber=user) \
                .values_list('report', flat=True), report__private__in=[False, user.is_pro()]) \
                .exclude(user=user) \
                .order_by('report', 'event_at')

            if not activities_list:
                continue

            logger.info('Digest of %s (%s)' % (unicode(user), user.email))
            logger.info('   Number of activities: %s' % activities_list.count())

            for activity in activities_list:
                logger.info('   %s %s %s' % (activity.event_at, activity.report.id, activity))

            # If NOT option send, do not send email
            if not options['send']:
                continue

            # Render and send the digest by mail
            send_digest(user, activity, activities_list, YESTERDAY)
