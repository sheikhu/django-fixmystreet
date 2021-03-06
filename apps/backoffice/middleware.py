import re

from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect




class LoginRequiredMiddleware:
    """
    Middleware that requires a user to be authenticated to view any page other
    than LOGIN_URL. Exemptions to this requirement can optionally be specified
    in settings via a list of regular expressions in LOGIN_EXEMPT_URLS (which
    you can copy from your urls.py).

    Requires authentication middleware and template context processors to be
    loaded. You'll get an error if they aren't.
    """
    def process_request(self, request):
        from django.conf import settings
        request.backoffice = False
        if re.compile(settings.LOGIN_REQUIRED_URL).search(request.path_info):
            if request.user.is_authenticated():
                request.backoffice = True
            else:
                if request.path_info != reverse("login"):
                    return HttpResponseRedirect('{0}?next={1}'.format(reverse("login"), request.path))


class LoadUserMiddleware:
    """
    """
    def process_request(self, request):
        from apps.fixmystreet.models import FMSUser
        if request.user.is_authenticated():
            try:
                request.fmsuser = request.user.fmsuser
            except FMSUser.DoesNotExist:
                pass # authenticated user is not a FMSUser
