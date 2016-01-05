# -*- coding: utf-8 -*-
from django.db import models
from django.utils.translation import ugettext_lazy as _

from django_extensions.db.fields.json import JSONField


class WebhookConfig(models.Model):
    resource = models.SlugField(_(u"resource"), max_length=30)
    hook = models.SlugField(_(u"hook"), max_length=30)
    action = models.SlugField(_(u"action"), max_length=30)
    third_party = models.ForeignKey("fixmystreet.OrganisationEntity", verbose_name=_(u"third-party"), blank=True)
    url = models.URLField(_(u"URL"))
    data = JSONField(_(u"data"), blank=True, help_text=_(u"Extra parameters related to the hook or the endpoint."))

    class Meta:
        index_together = (("resource", "hook", "action"),)
        unique_together = (("resource", "hook", "action", "third_party"),)
