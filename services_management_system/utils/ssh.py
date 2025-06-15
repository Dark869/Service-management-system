import logging
import datetime
import paramiko
import os
from services_management_system.settings import SSH_PUBLIC

ssh_log = logging.getLogger('SSH')

def copy_key_serverRemote(user: str, ip: str, password: str) -> bool:
    Public_SSH = SSH_PUBLIC
    if not os.path.exists(Public_SSH):
        ssh_log.error("LLave inexistente")
        return False
    try:
        with open(Public_SSH, 'r') as f:
            public_key_content = f.read().strip()
    except Exception as e:
        ssh_log.error("Fallo al recuperar la llave")
        return False
    
    