import os
from os import access
import sys
import time
import logging
import urllib2

from django.views.decorators.cache import never_cache
from django.conf import settings
from django.template import RequestContext
from django.shortcuts import render_to_response
from urlparse import urljoin


logger = logging.getLogger(__name__)


class Monitoring:

    STATUS = ("OK","INFO","WARNING","KO")
    STATUS_CODE = {"OK": 200, "INFRA": 413, "APP": 414}


    def check_django_version(self):
        import django
        return (0, ".".join(map(lambda n: str(n), django.VERSION)))
    check_django_version.label = "Django version : %s"


    def check_app_version(self):
        return (0, settings.VERSION)
    check_app_version.label = "App version %s"


    def check_uptime(self):
        process = os.popen("/usr/bin/uptime","r")
        uptime = process.read()
        process.close()
        return (0, uptime)
    check_uptime.label = "Uptime: %s"


    def check_db_connection(self):
        from django.db import connection
        connection.cursor()
        return (0, )
    check_db_connection.label = "Database connection %s"
    check_db_connection.status_type = 'INFRA'


    def check_db_timing(self):
        from django.contrib.auth.models import User

        start = time.time()
        User.objects.count()

        delay = time.time() - start

        if delay > 30:
            return (3, "extremely slow ( > 30 sec )")
        elif delay > 10 :
            return (2, "slow ( > 10 sec )")
        elif delay > 2:
            return (1, "delay > 2 sec")

        return (0, "%f sec" % delay)
    check_db_timing.label = "Database access speed %s"
    check_db_timing.status_type = 'INFO'


    def check_db_count(self):
        from django.contrib.auth.models import User
        userscount = User.objects.count()

        if userscount == 0:
            return (3, "no User found | database empty ?")

        return (0, "%s users" % userscount)
    check_db_count.label = "Database records ... %s"
    check_db_count.status_type = 'INFO'


    def check_permissions(self):
        if not access(settings.MEDIA_ROOT,os.R_OK):
            return (3, "cannot be read")

        if not access(settings.MEDIA_ROOT,os.W_OK):
            return (2, "is not writable")

        return (0, "read/write ok")
    check_permissions.label = "/static directory %s"
    check_permissions.status_type = 'APP'


    def check_charge(self):
        load = os.getloadavg()
        charge = load[0]

        if charge > 10.0:
            return (3, "server overloaded ( %s )" % charge)
        if charge > 3.0:
            return (2, "server heavily loaded ( %s )" % charge)
        elif charge > 1.0:
            return (1, "server loaded ( %s )" % charge)

        return (0, charge)
    check_charge.label = "server charge %s"
    check_charge.status_type = 'INFO'

    def check_freespace(self):
        import re
        process = os.popen("/bin/df %s" % settings.MEDIA_ROOT,"r")
        df_line = process.read()
        process.close()

        freespace_line = df_line.split("\n")[-2]
        freespace = 100 - int(re.match(r".*?([0-9]+)%", freespace_line).groups()[-1])

        if freespace < 1:
            return (3, freespace)
        elif freespace < 10:
            return (2, freespace)
        elif freespace < 30:
            return (1, freespace)


        return (0, "%s" % freespace)
    check_freespace.label = "free space on /static directory %s%%"
    check_freespace.status_type = 'INFO'



    def __init__(self):
        self.status = []
        status_code_final = self.STATUS_CODE['OK']

        for method_name in dir(self):
            method = getattr(self, method_name)
            if hasattr(method, "label") and getattr(method, "label", False):
                try:
                    result = method() or (3, " - software error, monitoring function returned nothing")
                except Exception, e:
                    logger.exception(e)
                    result = (3, sys.exc_info()[1])

                severity = result[0]
                if len(result) > 1:
                    description = "%s" % str(result[1]).replace(":","|").strip()
                else:
                    description = "(%s)" % self.STATUS[severity]

                self.status.append("%s:%s:" % (self.STATUS[severity], method.label % description))

                # If severity 3, set final code to INFRA (413) or APP (414)
                if severity == 3:
                    # If final code isn't yet INFRA (prior code)
                    if status_code_final != self.STATUS_CODE['INFRA']:
                        if method.status_type in ('INFRA', 'APP'):
                            status_code_final = self.STATUS_CODE[method.status_type]

        self.status_code_final = status_code_final
        logger.info('Happy page status : %s' % self.status_code_final)

    def _long_request(self, url, timeout=None, params=None, headers={}):
        import socket

        if timeout is None:
            timeout = 7
        response = None
        try:
            logger.debug("HTTP GET %s" % url)
            oldtimeout = socket.getdefaulttimeout()
            socket.setdefaulttimeout(timeout)
            request = urllib2.Request(url, params, headers)
            opener = urllib2.build_opener()
            response = opener.open(request)
            status = response.code
        except urllib2.HTTPError, e:
            status = e.code
        except urllib2.URLError, e:
            status = None
        finally:
            socket.setdefaulttimeout(oldtimeout)
        return (status, response)

@never_cache
def happy_page(request):
    monitoring = Monitoring()
    response = render_to_response('monitoring/happy_page.txt', { 'status': monitoring.status },
              context_instance=RequestContext(request), mimetype='text/plain; charset=utf-8')
    response.status_code = monitoring.status_code_final
    return response


@never_cache
def cpu(request):
    import cpu_benchmark
    return render_to_response('monitoring/cpu.txt', { 'times': cpu_benchmark.benchmark()},
              context_instance=RequestContext(request), mimetype='text/plain; charset=utf-8')
