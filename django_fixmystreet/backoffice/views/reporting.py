import os, re
from datetime import date

from django.http import HttpResponse
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.conf import settings
from django.utils.translation import ugettext as _

def reporting_list(request):
    # Filter on organisation entity
    organisation = request.fmsuser.organisation
    reporting_root = os.path.join(settings.REPORTING_ROOT, str(organisation.id))

    pdf = []
    xls = None
    try:
        ls = os.listdir(reporting_root)

        for path in ls:
            f = {
                'path': path,
                'stat': os.stat(os.path.join(reporting_root, path))
            }
            f['modified_date'] = date.fromtimestamp(int(f['stat'].st_mtime))

            # Check if xls or pdf
            extension = re.search(r'xls$', path)
            if extension:
                xls = f
            else:
                pdf.append(f)
    except OSError:
        messages.add_message(request, messages.ERROR, _("Reporting currently unavailable"))

    return render_to_response('pro/list_reporting.html', {
        'pdf': pdf,
        'xls': xls
    }, context_instance=RequestContext(request))

import mimetypes
from django.contrib import messages

def reporting_download(request, path):
    # Filter on organisation entity
    organisation = request.fmsuser.organisation

    try:
        reporting_file_path = os.path.join(settings.REPORTING_ROOT, str(organisation.id), str(path))

        reporting_file_type, reporting_file_encoding =  mimetypes.guess_type(reporting_file_path)

        reporting_file = open(reporting_file_path, 'r')
        response = HttpResponse(reporting_file.read(), mimetype=reporting_file_type)
        response['Content-Disposition'] = 'attachment; filename=%s' % path
        reporting_file.close()

        return response
    except IOError:
        messages.add_message(request, messages.ERROR, _("An error occured by opening file"))

    return reporting_list(request)
