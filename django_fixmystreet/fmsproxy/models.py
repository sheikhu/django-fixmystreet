import requests
import json

from django.conf import settings
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.template.loader import render_to_string

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
        data_json = render_to_string('assign.json', {'report':instance})

        logger.info('data_json %s ' % data_json)

        # Send data
        logger.info('FMSPROXY_URL %s' % settings.FMSPROXY_URL)
        url     = settings.FMSPROXY_URL
        headers = {'Content-Type': 'application/json'}

        response = requests.post(url, data=data_json, headers=headers)

        if response.status_code != 200:
            message = 'FMSProxy assignation failed (status code %s): %s on report %s' % (response.status_code, instance.contractor.fmsproxy, instance.id)

            logger.error(message)
            raise Exception(message)

        logger.info('FMSProxy assignation success')
