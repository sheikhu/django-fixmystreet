from django.http import HttpResponse, HttpResponseForbidden, HttpResponseBadRequest
from django.shortcuts import get_object_or_404

from django_fixmystreet.fixmystreet.models import Report, ReportAttachment, ReportComment

def accept(request, report_id):
    print 'accept', report_id

    report = get_object_or_404(Report, id=report_id)
    print report

    comment = ReportComment(report_id=report.id, text='belgacom comment accept', type=ReportAttachment.DOCUMENTATION)
    comment.save()

    return HttpResponse('accept ok')

def reject(request, report_id):
    print 'reject', report_id

    report = get_object_or_404(Report, id=report_id)
    print report

    comment = ReportComment(report_id=report.id, text='belgacom comment reject', type=ReportAttachment.DOCUMENTATION)
    comment.save()

    report.contractor = None
    report.status = Report.MANAGER_ASSIGNED
    report.save()

    return HttpResponse('reject ok')

def close(request, report_id):
    print 'close', report_id

    report = get_object_or_404(Report, id=report_id)
    print report

    comment = ReportComment(report_id=report.id, text='belgacom comment close', type=ReportAttachment.DOCUMENTATION)
    comment.save()

    report.contractor = None
    report.status = Report.MANAGER_ASSIGNED
    report.save()

    return HttpResponse('close ok')

# It's an example of view decoding json data in fmsproxy. It's not used by FMS.
def test_assign(request):

    if request.method == 'POST':
        import json
        decoded_data = json.loads(request.body)
        data = json.loads(decoded_data)

        fmsproxy = data['fmsproxy']
        report = data['report']
        creator = data['creator']

        print 'fmsproxy', fmsproxy
        print 'report', report['id'], report['category']
        print 'creator', creator['last_name'], creator['first_name'], creator['email']

        return HttpResponse('test_assign ok')

    return HttpResponse('test_assign ERROR', status=400)

