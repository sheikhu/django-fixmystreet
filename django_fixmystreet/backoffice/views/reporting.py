import os
from datetime import date
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.conf import settings


def list(request):
    organisation = request.fmsuser.organisation
    reporting_root = os.path.join(settings.REPORTING_ROOT, str(organisation.id))

    ls = os.listdir(reporting_root)

    files = []
    for path in ls:
        f = {
            'path': path,
            'stat': os.stat(os.path.join(reporting_root, path))
        }
        f['modified_date'] = date.fromtimestamp(int(f['stat'].st_mtime))
        print f['modified_date']
        files.append(f)

    return render_to_response('pro/list_reporting.html', {
        'files': files
    }, context_instance=RequestContext(request))


def download(request, path):
    return
