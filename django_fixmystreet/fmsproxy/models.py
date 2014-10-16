import requests
import json

from django.conf import settings
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from django_fixmystreet.fixmystreet.models import Report

import logging
logger = logging.getLogger(__name__)

class FMSProxy(models.Model):

    name = models.CharField(max_length=20, unique=True)

    def __unicode__(self):
        return self.name

@receiver(post_save, sender=Report)
def report_notify_fmsproxy(sender, instance, **kwargs):

    if kwargs['raw']:
        return

    # If contractor changes and is linked to a remote partner (fmsproxy)
    if instance.contractor and instance.__former['contractor'] != instance.contractor and instance.contractor.fmsproxy:
        logger.info('Contact FMSProxy %s' % instance.contractor.fmsproxy)

        # Prepare json data
        payload = get_assign_payload(instance)
        logger.info('payload %s ' % payload)

        # Send data
        logger.info('FMSPROXY_URL %s' % settings.FMSPROXY_URL)
        url     = settings.FMSPROXY_URL
        headers = {'Content-Type': 'application/json'}

        response = requests.post(url, data=json.dumps(payload), headers=headers)

        if response.status_code != 200:
            message = 'FMSProxy assignation failed (status code %s): %s on report %s' % (response.status_code, instance.contractor.fmsproxy, instance.id)

            logger.error(message)
            raise Exception(message)

        logger.info('FMSProxy assignation success')


def get_assign_payload(report):
    creator = report.get_creator()
    payload = {
        "application": report.contractor.fmsproxy.name.lower(),
        "report":{
            "id": report.id,
            "created_at": report.created.isoformat(),
            "modified_at": report.modified.isoformat(),
            "category": report.display_category(),
            "pdf_url": report.get_pdf_url_pro(),
            "address": report.address,
            "address_number": report.address_number,
            "postal_code": report.postalcode,
            "municipality": report.get_address_commune_name(),
            "creator": {
                "type": "pro" if report.is_pro() else "citizen",
                "first_name": creator.first_name,
                "last_name": creator.last_name,
                "phone": creator.telephone,
                "email": creator.email,
            },
            "comments": None,
        },
    }

    comments = report.active_comments()
    if comments:
        payload["report"]["comments"] = []
        for comment in comments:
            payload["report"]["comments"].append({
                "created_at": comment.created.isoformat(),
                "name": comment.get_display_name(),
                "text": comment.text,
            })

    return payload
