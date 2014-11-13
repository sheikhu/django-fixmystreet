# pylint: disable=E1120
import logging

from django.db import models
from django.utils.text import slugify


logger = logging.getLogger(__name__)


class FMSProxy(models.Model):

    name = models.CharField(max_length=20)
    slug = models.SlugField(max_length=20)

    def __unicode__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(FMSProxy, self).save(*args, **kwargs)
