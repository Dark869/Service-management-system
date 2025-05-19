from django.conf import settings
import requests

def send_code_telegram(code: str) -> None:
    data = {
        "chat_id": settings.CHAT_ID,
        "text": f"El código de verificación es: {code}"
    }
    url = f"https://api.telegram.org/bot{settings.TOKEN_BOT}/sendMessage"

    response = requests.post(url, data=data)

    if response.status_code == 200:
        return
    else:
        raise Exception(f"Error al enviar el mensaje a Telegram: {response.status_code} - {response.text}")
    