from django.conf import settings
import requests

def recaptchaVerify(recaptcha_response):
    data = {
        "secret": settings.RECAPTCHA_PRIVATE_KEY,
        "response": recaptcha_response
    }

    response = requests.post('https://www.google.com/recaptcha/api/siteverify', data=data)
    result = response.json()
    return result.get('success', False)
