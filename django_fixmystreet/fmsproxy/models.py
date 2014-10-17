from django.db import models

import logging
logger = logging.getLogger(__name__)

class FMSProxy(models.Model):

    name = models.CharField(max_length=20, unique=True)

    def __unicode__(self):
        return self.name

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
