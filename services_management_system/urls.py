from django.urls import path
from services_management_system.views import auth, index, verity_otp, renew_otp, registerServer, registerService, serverAdministrator

urlpatterns = [
    path('', serverAdministrator.serverAdministrator, name='serverAdministrator'),
    path('login/', auth.login, name='login'),
    path('verify2fa/', verity_otp.verity_otp, name='verify2fa'),
    path('renew2fa/', renew_otp.renew_otp, name='renew2fa'),
    path('logout/', auth.logout, name='logout'),
    path('registerServer/', registerServer.registerServer, name='registerServer'),
    path('registerService/', registerService.registerService, name='registerService'),
]
