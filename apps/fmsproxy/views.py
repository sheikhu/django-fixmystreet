import json
from django.template.loader import render_to_string
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseBadRequest
from django.shortcuts import get_object_or_404
from django.utils.translation import string_concat, ugettext_lazy as _
from apps.fixmystreet.models import Report, ReportAttachment, ReportComment, ReportEventLog
from apps.fmsproxy.utils import fms_proxy_signature_is_valid

ACTION_ACCEPT = "Accept"
ACTION_REJECT = "Reject"
ACTION_CLOSE = "Close"
ACTION_UPDATE = "Update"


def handle_request(request, report_id, action):
    try:
        if not request.method == 'POST':
            payload = {"message": "{0} error. Bad request method".format(action)}
            return HttpResponseBadRequest(json.dumps(payload), content_type="application/json")

        # if not fms_proxy_signature_is_valid(request):
        #     payload = {"message": "{0} error. Invalid signature"}
        #     return HttpResponseForbidden(json.dumps(payload), content_type="application/json")

        report = get_object_or_404(Report, id=report_id)

        data = json.loads(request.body)

        application = data.get('application')
        comment_text = data.get('comment')
        reference_id = data.get('reference_id')

        org_entity = report.get_organisation_entity_with_fms_proxy()

        if not (report.waiting_for_organisation_entity() and org_entity.fmsproxy.slug.lower() == application.lower()):
            payload = {"message": "{0} error. Cannot {0} report with id : ".format(action) + report_id}
            return HttpResponseForbidden(json.dumps(payload), content_type="application/json")

        params = {
            'action_msg': get_action_msg(action),
            'contractor_name': org_entity.name,
            'fms_proxy_id': org_entity.fmsproxy.id,
            'reference_id': reference_id,
            'comment': comment_text,
        }
        formatted_comment = render_to_string('formatted_comment.txt', params)

        comment = ReportComment(report_id=report.id, text=formatted_comment, type=ReportAttachment.DOCUMENTATION)
        comment.save()

        if action == ACTION_REJECT and not report.contractor:
            report.responsible_department = ReportEventLog.objects.filter(report=report_id,
                   organisation=report.responsible_entity,
                   event_type=ReportEventLog.MANAGER_ASSIGNED).latest("event_at").related_old

            report.responsible_entity = report.responsible_department.dependency
            report.status = Report.MANAGER_ASSIGNED
            report.save()

        elif action == ACTION_CLOSE and not report.contractor:
            report.close()

        payload = {"message": "{0} ok".format(action)}
        return HttpResponse(json.dumps(payload), content_type="application/json")
    except:
        payload = {"message": "{0} error. Internal server error".format(action)}
        return HttpResponse(json.dumps(payload), content_type="application/json", status=500)


def get_action_msg(action):
    if action == ACTION_ACCEPT:
        return _("Incident was accepted by")
    if action == ACTION_REJECT:
        return _("Incident was rejected by")
    if action == ACTION_CLOSE:
        return _("Incident was closed by")
    if action == ACTION_UPDATE:
        return _("Incident was updated by")
    return ""


def accept(request, report_id):
    return handle_request(request, report_id, ACTION_ACCEPT)


def reject(request, report_id):
    return handle_request(request, report_id, ACTION_REJECT)


def close(request, report_id):
    return handle_request(request, report_id, ACTION_CLOSE)

def update(request, report_id):
    return handle_request(request, report_id, ACTION_UPDATE)

# def accept(request, report_id):
#     # treat_request(request, report_id, action="Accept")
#     try:
#         if not request.method == 'POST':
#             payload = {"message": "Accept error. Bad request method"}
#             return HttpResponseBadRequest(json.dumps(payload), content_type="application/json")
#
#         if not fms_proxy_signature_is_valid(request):
#             payload = {"message": "Accept error. Invalid signature"}
#             return HttpResponseForbidden(json.dumps(payload), content_type="application/json")
#
#         report = get_object_or_404(Report, id=report_id)
#
#         data = json.loads(request.body)
#
#         application = data['application']
#         comment_text = data['comment']
#         reference_id = data['reference_id']
#
#         if not report.contractor or not application == report.contractor.fmsproxy.slug:
#             payload = {"message": "Accept error. Cannot accept report with id " + report_id}
#             return HttpResponseForbidden(json.dumps(payload), content_type="application/json")
#
#         params = {
#             'intro': _("Incident was accepted by"),
#             'contractor_name': report.contractor.name,
#             'fms_proxy_id': report.contractor.fmsproxy.id,
#             'reference_id': reference_id,
#             'comment': comment_text,
#         }
#         formatted_comment = render_to_string('formatted_comment.txt', params)
#
#         comment = ReportComment(report_id=report.id, text=formatted_comment, type=ReportAttachment.DOCUMENTATION)
#         comment.save()
#
#         payload = {"message": "accept ok"}
#         return HttpResponse(json.dumps(payload), content_type="application/json")
#     except:
#         payload = {"message": "Reject error. Internal server error"}
#         return HttpResponse(json.dumps(payload), content_type="application/json", status=500)
#
#
# def reject(request, report_id):
#     try:
#         if not request.method == 'POST':
#             payload = {"message": "Reject error. Bad request method"}
#             return HttpResponseBadRequest(json.dumps(payload), content_type="application/json")
#
#         if not fms_proxy_signature_is_valid(request):
#             payload = {"message": "Reject error. Invalid signature"}
#             return HttpResponseForbidden(json.dumps(payload), content_type="application/json")
#
#         report = get_object_or_404(Report, id=report_id)
#
#         data = json.loads(request.body)
#
#         application = data['application']
#         comment_text = data['comment']
#
#         if not report.contractor or not application == report.contractor.fmsproxy.slug:
#             payload = {"message": "Reject error. Cannot reject report with id " + report_id}
#             return HttpResponseForbidden(json.dumps(payload), content_type="application/json")
#
#         params = {
#             'intro': _("Incident was rejected by"),
#             'contractor_name': report.contractor.name,
#             'comment': comment_text,
#         }
#         formatted_comment = render_to_string('formatted_comment.txt', params)
#
#         comment = ReportComment(report_id=report.id, text=formatted_comment, type=ReportAttachment.DOCUMENTATION)
#         comment.save()
#
#         report.contractor = None
#         report.status = Report.MANAGER_ASSIGNED
#         report.save()
#
#         payload = {"message": "Reject ok"}
#         return HttpResponse(json.dumps(payload), content_type="application/json")
#     except:
#         payload = {"message": "Reject error. Internal server error"}
#         return HttpResponse(json.dumps(payload), content_type="application/json", status=500)
#
#
# def close(request, report_id):
#     try:
#         if not request.method == 'POST':
#             payload = {"message": "Close error. Bad request method"}
#             return HttpResponseBadRequest(json.dumps(payload), content_type="application/json")
#
#         if not fms_proxy_signature_is_valid(request):
#             payload = {"message": "Close error. Invalid signature"}
#             return HttpResponseForbidden(json.dumps(payload), content_type="application/json")
#
#         report = get_object_or_404(Report, id=report_id)
#
#         data = json.loads(request.body)
#
#         application = data['application']
#         comment_text = data['comment']
#         reference_id = data['reference_id']
#
#         if not report.contractor or not application == report.contractor.fmsproxy.slug:
#             payload = {"message": "Close error. Cannot close report with id " + report_id}
#             return HttpResponseForbidden(json.dumps(payload), content_type="application/json")
#
#         params = {
#             'intro': _("Incident was closed by"),
#             'contractor_name': report.contractor.name,
#             'fms_proxy_id': report.contractor.fmsproxy.id,
#             'reference_id': reference_id,
#             'comment': comment_text,
#         }
#         formatted_comment = render_to_string('formatted_comment.txt', params)
#
#         comment = ReportComment(report_id=report.id, text=formatted_comment, type=ReportAttachment.DOCUMENTATION)
#         comment.save()
#
#         report.contractor = None
#         report.status = Report.MANAGER_ASSIGNED
#         report.save()
#
#         payload = {"message": "close ok"}
#         return HttpResponse(json.dumps(payload), content_type="application/json")
#     except:
#         payload = {"message": "Close error. Internal server error"}
#         return HttpResponse(json.dumps(payload), content_type="application/json", status=500)

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

