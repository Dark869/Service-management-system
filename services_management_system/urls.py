from django.urls import path
from services_management_system.views import auth, index, verity_otp, renew_otp, registerServer, registerService, serverAdministrator, ajaxMonitor

urlpatterns = [
    path('', serverAdministrator.server_Administrator, name='serverAdministrator'),
    path('login/', auth.login, name='login'),
    path('verify2fa/', verity_otp.verity_otp, name='verify2fa'),
    path('renew2fa/', renew_otp.renew_otp, name='renew2fa'),
    path('logout/', auth.logout, name='logout'),
    path('registerServer/', registerServer.register_Server, name='registerServer'),
    path('registerService/', registerService.register_Service, name='registerService'),
    path('monitor/', ajaxMonitor.server_Administrator, name='ajaxMonitor'),
]
