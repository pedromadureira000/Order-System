from django.http.response import JsonResponse
from django.contrib.auth import logout
from django.utils.translation import gettext_lazy as _

class OneSessionPerUserMiddleware:
    # Called only once when the web server starts
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        #  print('inside onesession middleware: ', datetime.now())
        if request.user.is_authenticated:
            path = request.get_full_path()
            if not request.user.current_session_key:
                # This will occur when an user attempt to access an API with a old valid session after he has being logged out.
                logout(request)
                return JsonResponse({"detail": _("Invalid session. Try to login again.")}, status=403)
            if path == '/api/user/own_profile' and request.method == 'GET':
                if  request.user.current_session_key != request.session.session_key:
                    request.user.current_session_key = request.session.session_key
                    request.user.save(update_fields=['current_session_key'])
                response = self.get_response(request)
                return response
            if  request.user.current_session_key != request.session.session_key:
                return JsonResponse({"detail":_("A session was opened in another browser. Reload the page to access here.")}, status=403)
        response = self.get_response(request)
        return response
