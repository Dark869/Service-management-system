from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from services_management_system.middlewares.loginRequest import login_request
from services_management_system.utils.hashing import check_hash
from db import models

@login_request
def verity_otp(request: HttpResponse) -> HttpResponse | JsonResponse:
    if request.session.get('2fa_verified'):
        return redirect('/')

    if request.method == 'GET':
        return render(request, 'verify2fa.html')
    elif request.method == 'POST':
        user = request.session.get('user')
        otp = request.POST.get('codeotp', '').strip()
        errores = []

        if not otp:
            errores.append('El codigo no puede estar vacío')
            return JsonResponse({'status': 'error', 'message': 'El código no puede estar vacío', 'errores': errores})

        user_auth = models.AuthData.objects.filter(email=user).values("codeOTP").first()

        if not user_auth['codeOTP']:
            errores.append('El código no ha sido generado')
            return JsonResponse({'status': 'error', 'message': 'El código no ha sido generado', 'errores': errores})

        if check_hash(otp, user_auth['codeOTP']):
            request.session['2fa_verified'] = True
            return redirect('/registerServer')
        else:
            errores.append('El código es incorrecto')
            return JsonResponse({'status': 'error', 'message': 'El código es incorrecto', 'errores': errores})