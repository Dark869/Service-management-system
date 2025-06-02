from django.conf import settings
import requests

def send_code_telegram(code: str) -> bool:
    data = {
        "chat_id": settings.CHAT_ID,
        "text": f"El código de verificación es: {code}"
    }
    url = f"https://api.telegram.org/bot{settings.TOKEN_BOT}/sendMessage"

    response = requests.post(url, data=data)

    if response.status_code == 200:
        return True
    else:
        return False
    