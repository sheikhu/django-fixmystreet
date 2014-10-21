import json
from django.template.loader import render_to_string
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseBadRequest
from django.shortcuts import get_object_or_404
from django.utils.translation import string_concat, ugettext_lazy as _
from django_fixmystreet.fixmystreet.models import Report, ReportAttachment, ReportComment
from django_fixmystreet.fmsproxy.utils import fms_proxy_signature_is_valid


def accept(request, report_id):
    try:
        if not request.method == 'POST':
            payload = {"message": "Accept error. Bad request method"}
            return HttpResponseBadRequest(json.dumps(payload), mimetype="application/json")

        if not fms_proxy_signature_is_valid(request):
            payload = {"message": "Accept error. Invalid signature"}
            return HttpResponseForbidden(json.dumps(payload), mimetype="application/json")

        report = get_object_or_404(Report, id=report_id)

        data = json.loads(request.body)

        application = data['application']
        comment_text = data['comment']
        reference_id = data['reference_id']

        if not report.contractor or not application == report.contractor.fmsproxy.slug:
            payload = {"message": "Accept error. Cannot accept report with id " + report_id}
            return HttpResponseForbidden(json.dumps(payload), mimetype="application/json")

        params = {
            'intro': _("Incident was accepted by"),
            'contractor_name': report.contractor.name,
            'fms_proxy_id': report.contractor.fmsproxy.id,
            'reference_id': reference_id,
            'comment': comment_text,
        }
        formatted_comment = render_to_string('formatted_comment.txt', params)

        comment = ReportComment(report_id=report.id, text=formatted_comment, type=ReportAttachment.DOCUMENTATION)
        comment.save()

        payload = {"message": "accept ok"}
        return HttpResponse(json.dumps(payload), mimetype="application/json")
    except:
        payload = {"message": "Reject error. Internal server error"}
        return HttpResponse(json.dumps(payload), mimetype="application/json", status=500)


def reject(request, report_id):
    try:
        if not request.method == 'POST':
            payload = {"message": "Reject error. Bad request method"}
            return HttpResponseBadRequest(json.dumps(payload), mimetype="application/json")

        if not fms_proxy_signature_is_valid(request):
            payload = {"message": "Reject error. Invalid signature"}
            return HttpResponseForbidden(json.dumps(payload), mimetype="application/json")

        report = get_object_or_404(Report, id=report_id)

        data = json.loads(request.body)

        application = data['application']
        comment_text = data['comment']

        if not report.contractor or not application == report.contractor.fmsproxy.slug:
            payload = {"message": "Reject error. Cannot reject report with id " + report_id}
            return HttpResponseForbidden(json.dumps(payload), mimetype="application/json")

        params = {
            'intro': _("Incident was rejected by"),
            'contractor_name': report.contractor.name,
            'comment': comment_text,
        }
        formatted_comment = render_to_string('formatted_comment.txt', params)

        comment = ReportComment(report_id=report.id, text=formatted_comment, type=ReportAttachment.DOCUMENTATION)
        comment.save()

        report.contractor = None
        report.status = Report.MANAGER_ASSIGNED
        report.save()

        payload = {"message": "Reject ok"}
        return HttpResponse(json.dumps(payload), mimetype="application/json")
    except:
        payload = {"message": "Reject error. Internal server error"}
        return HttpResponse(json.dumps(payload), mimetype="application/json", status=500)


def close(request, report_id):
    try:
        if not request.method == 'POST':
            payload = {"message": "Close error. Bad request method"}
            return HttpResponseBadRequest(json.dumps(payload), mimetype="application/json")

        if not fms_proxy_signature_is_valid(request):
            payload = {"message": "Close error. Invalid signature"}
            return HttpResponseForbidden(json.dumps(payload), mimetype="application/json")

        report = get_object_or_404(Report, id=report_id)

        data = json.loads(request.body)

        application = data['application']
        comment_text = data['comment']
        reference_id = data['reference_id']

        if not report.contractor or not application == report.contractor.fmsproxy.slug:
            payload = {"message": "Close error. Cannot close report with id " + report_id}
            return HttpResponseForbidden(json.dumps(payload), mimetype="application/json")

        params = {
            'intro': _("Incident was closed by"),
            'contractor_name': report.contractor.name,
            'fms_proxy_id': report.contractor.fmsproxy.id,
            'reference_id': reference_id,
            'comment': comment_text,
        }
        formatted_comment = render_to_string('formatted_comment.txt', params)

        comment = ReportComment(report_id=report.id, text=formatted_comment, type=ReportAttachment.DOCUMENTATION)
        comment.save()

        report.contractor = None
        report.status = Report.MANAGER_ASSIGNED
        report.save()

        payload = {"message": "close ok"}
        return HttpResponse(json.dumps(payload), mimetype="application/json")
    except:
        payload = {"message": "Close error. Internal server error"}
        return HttpResponse(json.dumps(payload), mimetype="application/json", status=500)

# It's an example of view decoding json data in fmsproxy. It's not used by FMS.
def test_assign(request):

    if not request.method == 'POST':
        return HttpResponseBadRequest('test_assign ERROR')

    decoded_data = json.loads(request.body)
    data = json.loads(decoded_data)

    fmsproxy = data['fmsproxy']
    report = data['report']
    creator = data['creator']

    print 'fmsproxy', fmsproxy
    print 'report', report['id'], report['category']
    print 'creator', creator['last_name'], creator['first_name'], creator['email']

    return HttpResponse('test_assign ok')


# def create_reference_comment(fms_proxy_id, reference_id):
#     if reference_id:
#         if fms_proxy_id == 1 and reference_id: #id = 1 belgacom-icare
#             return string_concat("iCare: ", reference_id)
#     elif fms_proxy_id == 2 and reference_id: #id = 2 osiris
#         return string_concat("Osiris ID: ", reference_id)
#     return ""

