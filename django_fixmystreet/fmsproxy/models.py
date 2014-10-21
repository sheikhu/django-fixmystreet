from django.contrib.sites.models import Site
from django.db import models
from django.utils.text import slugify

import logging
logger = logging.getLogger(__name__)

class FMSProxy(models.Model):

    name = models.CharField(max_length=20)
    slug = models.SlugField(max_length=20)

    def __unicode__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(FMSProxy, self).save(*args, **kwargs)


def get_assign_payload(report):
    creator = report.get_creator()
    site = Site.objects.get_current()
    base_url = "http://{}".format(site.domain)
    payload = {
        "application": report.contractor.fmsproxy.slug,
        "report":{
            "id": report.id,
            "created_at": report.created.isoformat(),
            "modified_at": report.modified.isoformat(),
            "category": report.display_category(),
            "pdf_url": "{}/{}".format(base_url.rstrip("/"), report.get_pdf_url_pro().lstrip("/")),  # @TODO: Add auto-auth token.
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
            "comments": [],
        },
    }

    comments = report.active_attachments_pro()
    for comment in comments:
        payload["report"]["comments"].append({
            "created_at": comment.created.isoformat(),
            "name": comment.created_by.get_display_name(),
            "text": comment.reportcomment.text,
        })

    return payload
