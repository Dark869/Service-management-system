from django.shortcuts import render, redirect
from services_management_system.utils.hashing import check_password, hash_password
from db import models


def login(request):
    if request.session.get('logged'):
        return redirect('/')

    t = 'login.html'
    if request.method == 'GET':
        return render(request, t)
    elif request.method == 'POST':
        email = request.POST.get('email', '').strip()
        passwd = request.POST.get('passwd', '').strip()
        errores = []
        if not email or not passwd:
            errores.append('El usuario o contraseña no pueden estar vacíos')
            return render(request, t, {'errores': errores})

        user_auth_data = models.AuthData.objects.filter(email=email).values("password").first()

        if not user_auth_data:
            errores.append('El usuario o contraseña no son correctos')
            return render(request, t, {'errores': errores})

        if check_password(passwd, user_auth_data['password']):
            user = models.User.objects.filter(auth_data__email=email).values("username").first()
            if not user:
                errores.append('El usuario o contraseña no son correctos')
                return render(request, t, {'errores': errores})
            request.session['logged'] = True
            request.session['user'] = user['username']
            return redirect('/')
        else:
            errores.append('El usuario o contraseña no son correctos')
            return render(request, t, {'errores': errores})
