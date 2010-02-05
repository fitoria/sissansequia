from django.http import HttpResponseRedirect
def session_required(f):
    def check_session(request):
        if 'activo' not in request.session.keys():
            return HttpResponseRedirect('/sequia/index/')
        return f(request)
    return check_session

