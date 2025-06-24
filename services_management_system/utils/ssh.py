import logging
import paramiko
import os
from paramiko import HostKeys
from services_management_system.settings import FINGERPRINT, SSH_PUBLIC, SSH_PRIVATE, CLAVE_OF_KEY

ssh_log = logging.getLogger('SSH')

def register_server(ip: str, password: str) -> bool:
    """
    Funcion para configurar comunicacion SSH con el servidor registrado, usando la libreria paramiko
    se configura el envio de llaves  asi como la copia de la clave de host para la verificación.
    Args:
        ip (str): IP del servidor a registrar.
        password (str): Contraseña del usuario creado mediante el script de instalacion.

    Returns:
        bool: 
            -False: Si la comunicacion o algun paso de la configuracion falla
            -True: Si la comunicacion o configuracion fue exitosa
    """
    fingerprint = FINGERPRINT
    key_public = SSH_PUBLIC

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    registration_success = True

    try:
        ssh_log.info(f"Intentando la PRIMERA conexión a {ip}")
        client.connect(hostname=ip, username="monitoreo", password=password, timeout=10)
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
                with open(key_public, 'r') as f:
                    public_key_content = f.read().strip()
            except FileNotFoundError:
                ssh_log.error("Archivo de clave pública no encontrado.")
                registration_success = False

            if public_key_content:
                command = (
                    f"REMOTE_HOME_DIR=$(getent passwd monitoreo | cut -d: -f6); "
                    f"mkdir -p \"$REMOTE_HOME_DIR/.ssh\" && "
                    f"chmod 700 \"$REMOTE_HOME_DIR/.ssh\" && "
                    f"echo '{public_key_content}' | tee -a \"$REMOTE_HOME_DIR/.ssh/authorized_keys\" > /dev/null && "
                    f"chmod 600 \"$REMOTE_HOME_DIR/.ssh/authorized_keys\""
                )
                ssh_log.info(f"Copiando la clave pública a authorized_keys en {ip}...")
                _, stdout, stderr = client.exec_command(command)
                error_key_copy = stderr.read().decode('utf-8').strip()

                if error_key_copy:
                    ssh_log.error(f"Fallo al copiar la clave pública en {ip}: {error_key_copy}")
                    registration_success = False
                else:
                    ssh_log.info(f"Clave pública copiada exitosamente en {ip}.")
            else:
                ssh_log.error("Contenido de la clave pública no disponible.")
                registration_success = False

            if registration_success:
                try:
                    known_hosts = HostKeys()
                    if os.path.exists(fingerprint):
                        known_hosts.load(fingerprint)
                    key = client.get_transport().get_remote_server_key()
                    known_hosts.add(ip, key.get_name(), key)
                    known_hosts.save(fingerprint)
                    ssh_log.info(f"Clave de host para {ip} añadida a {fingerprint}.")
                except Exception as e:
                    ssh_log.error(f"Fallo al añadir clave de host para {ip}: {e}")
                    registration_success = False

        except paramiko.SSHException as e:
            ssh_log.error(f"Fallo de SSH durante la configuración post-conexión en {ip}: {e}")
            registration_success = False
        except Exception as e:
            ssh_log.error(f"Ocurrió un error durante la configuración post-conexión en {ip}: {e}", exc_info=True)
            registration_success = False
        finally:
            client.close()
            ssh_log.info(f"Conexión SSH a {ip} cerrada.")
    else:
        ssh_log.info(f"No se realizaron pasos de configuración adicionales para {ip} ya que la conexión inicial falló.")

    return registration_success

def connect_client(ip: str) -> paramiko.SSHClient:
    """
    Funcion que se encarga de conectar cliente SSH atravez de libreria paramiko.
    Args:
        ip (str): IP del servidor

    Returns:
        paramiko.SSHClient: Cliente de SSH conectado
        None: Error en la conexion SSH
    """
    fingerprint = FINGERPRINT
    key_private = SSH_PRIVATE
    clave_key = CLAVE_OF_KEY
    client = paramiko.SSHClient()
    
    try:
        client.load_host_keys(fingerprint)
        ssh_log.info("Claves de host cargadas.")
    except FileNotFoundError:
        ssh_log.error("Archivo known_hosts no encontrado.")
        return None
    except Exception as e:
        ssh_log.error(f"Fallo al cargar claves de host para {ip}: {e}", exc_info=True)
        return None

    client.set_missing_host_key_policy(paramiko.RejectPolicy())

    try:
        private_key = paramiko.RSAKey.from_private_key_file(key_private, password=clave_key)
        ssh_log.info(f"Intentando verificación de conexión a {ip} usando clave privada y known_hosts")
        client.connect(hostname=ip, username=str("monitoreo"), pkey=private_key, timeout=10)
        ssh_log.info(f"Conexión verificada con éxito para {ip}.")
        return client
    except paramiko.BadHostKeyException as e:
        ssh_log.error(f"Clave de host incorrecta para {ip}. La clave actual del servidor no coincide con la guardada. Detalle: {e}")
        return None
    except (paramiko.AuthenticationException, paramiko.PasswordRequiredException) as e:
        ssh_log.error(f"Fallo durante la verificación con clave privada para {ip}. Detalle: {e}")
        return None
    except paramiko.SSHException as e:
        ssh_log.error(f"Fallo de conexión SSH durante la verificación a {ip}. Detalle: {e}")
        return None
    except FileNotFoundError as e:
        ssh_log.error(f"Archivo de clave SSH privada no encontrado: {e}")
        return None
    except Exception as e:
        ssh_log.error(f"ERROR INESPERADO: Ocurrió un error durante la verificación de conexión a {ip}: {e}", exc_info=True)
        return None

def verify_service(service: str, ip: str) -> bool:
    """
    Funcion que verifica si el servicio dado existe en el servido con la IP dada
    Args:
        service (str): Servicio para verificar existencia
        ip (str): IP del servidor que guarda el servicio

    Returns:
        bool:
            -False: Si el servicio no existe en el servidor
            -True: Si el servicio si existe en el servidor
            -None: Si hubo un error al establecer la conexion SSH
    """
    client = None 
    try:
        client = connect_client(ip)
        if client is None:
            ssh_log.error(f"No se pudo establecer la conexión SSH en la {ip}.")
            return False
        
        command = f"systemctl status {service} &>/dev/null; echo $?"
        ssh_log.info(f"Ejecutando comando remoto: '{command}' en {ip}")
        _stdin, stdout, stderr = client.exec_command(command)
        exit_code_str = stdout.read().decode('utf-8').strip()
        remote_error = stderr.read().decode('utf-8').strip()

        if remote_error:
            ssh_log.warning(f"Problemas al verificar servicio '{service}' en {ip}")

        try:
            exit_code = int(exit_code_str)
            if exit_code in [0,3]:
                ssh_log.info(f"Servicio '{service}' existe.")
                return True
            else:
                ssh_log.info(f"Servicio '{service}' no existe.")
                return False
        except ValueError:
            ssh_log.error(f"No se pudo parsear el código de salida '{exit_code_str}' para el servicio '{service}'.")
            return False
    except paramiko.SSHException as e:
        ssh_log.error(f"Error en la ejecución del comando para '{service}' en {ip}: {e}")
        return False
    except Exception as e:
        ssh_log.error(f"Error al verificar el servicio '{service}' en {ip}: {e}", exc_info=True)
        return False
    finally:
        if client:
            client.close()
            ssh_log.info(f"Conexión SSH a {ip} cerrada.")

def administrator_server(ip: str, service: str, option: str) -> bool:
    """_summary_

    Args:
        ip (str): IP del servidor
        service (str): Servicio existente en el servidor
        option (str): Opcion a realizar(start,stop,restart)

    Returns:
        bool: 
            -None: Si hubo un error en la conexion SSH
            -False: Si no se logro ejecutar el comando o hubo un error
            -True: Si se ejecuto el comando correctamente
    """
    client = None
    try:
        client = connect_client(ip)
        if client is None:
            ssh_log.error(f"No se pudo establecer la conexión SSH en la {ip}.")
            return False

        if not service.endswith('.service'):
            service_extend = f"{service}.service"
        else:
            service_extend = service

        command = f"sudo systemctl {option} {service_extend}"
        ssh_log.info(f"Ejecutando comando remoto: '{command}' en {ip}")

        _stdin, stdout, stderr = client.exec_command(command, get_pty=True)
        exit_status = stdout.channel.recv_exit_status()

        if exit_status == 0:
            ssh_log.info(f"Comando '{command}' ejecutado con éxito en {ip}")
            return True
        else:
            ssh_log.error(f"Fallo al ejecutar '{command}' en {ip}.")
            return False
    except:
        ssh_log.error("Fallo de conexión SSH.")
        return False
    finally:
        if client:
            client.close()
            ssh_log.info(f"Conexión SSH a {ip} cerrada.")

def status_service(ip:str, service:str) -> str:
    """
    Funcion para verificar el estado de un servicio existente en un servidor.
    Args:
        ip (str): IP del servidor
        service (str): Servicio que se monitoreara y que exita en el server

    Returns:
        str: Estado del servicio
        None: Si la conexion SSH fallo
    """
    client = None
    try:
        client = connect_client(ip)
        if client is None:
            ssh_log.error(f"No se pudo establecer la conexión SSH en la {ip}.")
            return None

        if not service.endswith('.service'):
            service_extend = f"{service}.service"
        else:
            service_extend = service
            
        command = f"systemctl status {service_extend}"
        ssh_log.info(f"Ejecutando comando remoto para estado: '{command}' en {ip}")
        
        _stdin, stdout, stderr = client.exec_command(command)
        output = stdout.read().decode('utf-8').strip()
        error_output = stderr.read().decode('utf-8').strip()
        exit_status = stdout.channel.recv_exit_status()

        if exit_status == 0:
            if "Active: active (running)" in output:
                ssh_log.info(f"Servicio {service} en {ip} está activo.")
                return 'active'
            elif "Active: inactive (dead)" in output or "Active: failed (" in output:
                ssh_log.info(f"Servicio {service} en {ip} está inactivo o fallido.")
                return 'inactive'
            else:
                ssh_log.warning(f"Salida inesperada para {service} en {ip}. Salida: '{output}'")
                return 'unknown'
        elif exit_status == 3:
            if "Active: inactive (dead)" in output or "Active: failed (" in output:
                ssh_log.info(f"Servicio {service} en {ip} está inactivo.")
                return 'inactive'
            elif "Load state: not-found" in output or "Could not find unit" in error_output:
                ssh_log.info(f"Servicio {service} en {ip} no encontrado.")
                return 'not-found'
            else:
                ssh_log.warning(f"No se pudo determinar el estado del servicio {service} en {ip}, Errores: '{error_output}'")
                return 'unknown'
        else:
            if "Load state: not-found" in output or "Could not find unit" in error_output:
                 ssh_log.info(f"Servicio {service} en {ip} no encontrado (status {exit_status}/not-found).")
                 return 'not-found'
            else:
                ssh_log.warning(f"Fallo al obtener el estado del servicio {service} en {ip}.")
                return 'error'
    except:
        ssh_log.error("Fallo de conexión SSH.")
        return "No localizado"
    finally:
        if client:
            client.close()
            ssh_log.info(f"Conexión SSH a {ip} cerrada.")