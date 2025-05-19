from services_management_system.utils.hashing import generate_hash
from services_management_system.utils.sendCodeTelegram import send_code_telegram
from db import models
import random

def generate_code_2fa(user: str) -> None:
    code = str(random.randint(100000, 999999))
    hashed_code = generate_hash(code)
    send_code_telegram(code)
    models.AuthData.objects.filter(email=user).update(codeOTP=hashed_code)
    return 