from services_management_system.utils.hashing import generate_hash
from services_management_system.utils.sendCodeTelegram import send_code_telegram
from db import models
import random
import threading

def generate_code_2fa(user: str) -> bool:
    code = str(random.randint(100000, 999999))
    hashed_code = generate_hash(code)
    if not send_code_telegram(code):
        return False
    models.AuthData.objects.filter(email=user).update(codeOTP=hashed_code)
    delete_code = threading.Timer(180, delete_code_2fa, args=[user])
    delete_code.start()
    return True

def delete_code_2fa(user: str) -> None:
    models.AuthData.objects.filter(email=user).update(codeOTP=None)
    return