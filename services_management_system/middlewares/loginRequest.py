from typing import Callable, Any
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect
from functools import wraps

SESSION_LOGGED_KEY = 'logged'
TWOFA_VERIFIED_KEY = '2fa_verified'

ViewFunc = Callable[[HttpRequest, Any, Any], HttpResponse]

def login_request(view: ViewFunc) -> ViewFunc:
    @wraps(view)
    def interna(request, *args, **kargs):
        if not request.session.get(SESSION_LOGGED_KEY, False):
            return redirect('/login')
        return view(request, *args, **kargs)
    return interna

def twofa_verified(view: ViewFunc) -> ViewFunc:
    @wraps(view)
    def interna(request, *args, **kargs):
        if not request.session.get(TWOFA_VERIFIED_KEY, False):
            return redirect('/verify2fa')
        return view(request, *args, **kargs)
    return interna

