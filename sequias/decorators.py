from django.http import HttpResponseRedirect
def session_required(f):
    def check_session(request):
        if 'activo' not in request.session.keys():
            return HttpResponseRedirect('/')
        return f(request)
    return check_session

