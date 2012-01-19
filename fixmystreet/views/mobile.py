    import json

    from social_auth.backends import get_backend
    from django.contrib.auth import authenticate
    from django.http import HttpResponse


    def oauthtoken_to_user(backend_name,token,request,*args, **kwargs):
        """Check and retrieve user with given token.
        """
        backend = get_backend(backend_name,request,"")
        response = backend.user_data(token) or {}
        response['access_token'] = token
        kwargs.update({'response': response, backend_name: True})
        user = authenticate(*args, **kwargs)
        return user

    def create_report(request):
        user = oauthtoken_to_user(request.GET.get('backend'),request.GET.get('access_token'),request)

        return HttpResponse(json.dumps({
            'status':'success',
            'user':user.get_full_name()
        }),mimetype="application/json")
