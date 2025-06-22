import logging
import paramiko
import os
from services_management_system.settings import FINGERPRINT, SSH_PUBLIC, SSH_PRIVATE

ssh_log = logging.getLogger('SSH')
fingerprint = FINGERPRINT
key_public = SSH_PUBLIC
key_private = SSH_PRIVATE

def register_server(ip: str, password: str) -> bool:
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    registration_success = True

    try:
        ssh_log.info(f"Intentando la PRIMERA conexión a {ip}")
        client.connect(hostname=ip, username=str("monitoreo"), password=password, timeout=10)
        ssh_log.info(f"Conexión SSH inicial establecida con éxito a {ip}.")
    except paramiko.AuthenticationException as e:
        ssh_log.error(f"Fallo al conectar a {ip}. Verifica credenciales. Detalle: {e}")
        registration_success = False
    except paramiko.SSHException as e:
        ssh_log.error(f"Fallo de conexión SSH a {ip}. Detalle: {e}")
        registration_success = False
    except Exception as e:
        ssh_log.error(f"Ocurrió un error durante la conexión inicial a {ip}: {e}", exc_info=True)
        registration_success = False

    if registration_success:
        try:
            public_key_content = None
            try:
                with open(SSH_PUBLIC, 'r') as f:
                    public_key_content = f.read().strip()
            except FileNotFoundError:
                ssh_log.error(f"Archivo de clave pública no encontrado en: {SSH_PUBLIC}.")
                registration_success = False

            if public_key_content and registration_success:
                command = (
                    f"REMOTE_HOME_DIR=$(getent passwd monitoreo | cut -d: -f6); "
                    f"mkdir -p \"${{REMOTE_HOME_DIR}}\"/.ssh && "
                    f"chmod 700 \"${{REMOTE_HOME_DIR}}\"/.ssh && "
                    f"echo '{public_key_content}' | tee -a \"${{REMOTE_HOME_DIR}}\"/.ssh/authorized_keys > /dev/null && "
                    f"chmod 600 \"${{REMOTE_HOME_DIR}}\"/.ssh/authorized_keys"
                )
                ssh_log.info(f"Copiando la clave pública a authorized_keys en {ip}...")
                _stdin, stdout, stderr = client.exec_command(command)
                error_key_copy = stderr.read().decode('utf-8').strip()

                if error_key_copy:
                    ssh_log.error(f"Fallo al copiar la clave pública en {ip}: {error_key_copy}")
                    registration_success = False
                else:
                    ssh_log.info(f"Clave pública copiada exitosamente en {ip}.")
            elif registration_success:
                ssh_log.error("Contenido de la clave pública no disponible.")
                registration_success = False
            if registration_success:
                try:
                    host_keys = client.get_host_keys()
                    host_keys.save(fingerprint)
                    ssh_log.info(f"Clave de host para {ip} guardada en {fingerprint}.")
                except Exception as e:
                    ssh_log.error(f"Fallo al guardar la clave de host para {ip} en {fingerprint}: {e}")
                    registration_success = False
        except paramiko.SSHException as e:
            ssh_log.error(f"Fallo de SSH durante la configuración post-conexión en {ip}: {e}")
            registration_success = False
        except Exception as e:
            ssh_log.error(f"Ocurrió un error durante la configuración post-conexión en {ip}: {e}", exc_info=True)
            registration_success = False
        finally:
            if client:
                client.close()
                ssh_log.info(f"Conexión SSH a {ip} cerrada.")
    else:
        ssh_log.info(f"No se realizaron pasos de configuración adicionales para {ip} ya que la conexión inicial falló.")

    return registration_success

def verify_fingerprint(name: str, ip: str) -> bool:
    client = paramiko.SSHClient()

    try:
        client.load_host_keys(FINGERPRINT)
        ssh_log.info(f"Claves de host cargadas exitosamente desde: {FINGERPRINT}.")
    except FileNotFoundError:
        ssh_log.error(f"Archivo known_hosts no encontrado en {FINGERPRINT}.")
        return False
    except Exception as e:
        ssh_log.error(f"Fallo al cargar claves de host desde {FINGERPRINT} para {ip}: {e}", exc_info=True)
        return False

    client.set_missing_host_key_policy(paramiko.RejectPolicy())

    try:
        private_key = paramiko.RSAKey.from_private_key_file(SSH_PRIVATE)
        ssh_log.info(f"Intentando verificación de conexión a {ip} usando clave privada y known_hosts...")
        client.connect(hostname=ip, username=str("monitoreo"), pkey=private_key, timeout=10)
        ssh_log.info(f"Conexión verificada con éxito para {ip}.")
        return True
    except paramiko.BadHostKeyException as e:
        ssh_log.error(f"Clave de host incorrecta para {ip}. La clave actual del servidor no coincide con la guardada. Detalle: {e}")
        return False
    except (paramiko.AuthenticationException, paramiko.PasswordRequiredException) as e:
        ssh_log.error(f"Fallo durante la verificación con clave privada para {ip}. Detalle: {e}")
        return False
    except paramiko.SSHException as e:
        ssh_log.error(f"Fallo de conexión SSH durante la verificación a {ip}. Detalle: {e}")
        return False
    except FileNotFoundError as e:
        ssh_log.error(f"Archivo de clave SSH privada no encontrado en {SSH_PRIVATE}: {e}")
        return False
    except Exception as e:
        ssh_log.error(f"ERROR INESPERADO: Ocurrió un error durante la verificación de conexión a {ip}: {e}", exc_info=True)
        return False
    finally:
        if client:
            client.close()
            ssh_log.info(f"Conexión SSH de verificación a {ip} cerrada.")

def verify_service(name: str, service: str, ip: str) -> bool:
    client = paramiko.SSHClient()

    try:
        client.load_host_keys(FINGERPRINT)
        ssh_log.info(f"Claves de host cargadas desde: {FINGERPRINT}.")
    except FileNotFoundError:
        ssh_log.error(f"Archivo known_hosts personalizado no encontrado en {FINGERPRINT}.")
        return False
    except Exception as e:
        ssh_log.error(f"Fallo al cargar claves de host desde {FINGERPRINT} para {ip}: {e}", exc_info=True)
        return False

    client.set_missing_host_key_policy(paramiko.RejectPolicy())

    try:
        private_key = paramiko.RSAKey.from_private_key_file(SSH_PRIVATE)
        ssh_log.info(f"Intentando conectar a {ip} para verificar servicio '{service}'...")
        client.connect(hostname=ip, username=str("monitoreo"), pkey=private_key, timeout=10)
        ssh_log.info(f"Conexión SSH establecida con éxito a {ip}.")

        command = f"systemctl status {service} &>/dev/null; echo $?"
        ssh_log.info(f"Ejecutando comando remoto: '{command}' en {ip}")
        
        _stdin, stdout, stderr = client.exec_command(command)
        exit_code_str = stdout.read().decode('utf-8').strip()
        remote_error = stderr.read().decode('utf-8').strip()

        if remote_error:
            ssh_log.warning(f"Problemas al verificar servicio '{service}' en {ip}")

        try:
            exit_code = int(exit_code_str)
            if exit_code == 0:
                ssh_log.info(f"Servicio '{service}' existe.")
                return True
            else:
                ssh_log.info(f"Servicio '{service}' no existe.")
                return False
        except ValueError:
            ssh_log.error(f"No se pudo parsear el código de salida '{exit_code_str}' para el servicio '{service}'.")
            return False
    except:
        ssh_log.error(f"Fallo de conexión SSH.")
        return False
    finally:
        if client:
            client.close()
            ssh_log.info(f"Conexión SSH a {ip} cerrada.")