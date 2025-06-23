#!/bin/bash

MONITOR_USER="monitoreo"
SUDOERS_FILE="/etc/sudoers.d/monitoreo_commands"
SSHD_PACKAGE=""
PACKAGE_MANAGER=""

echo "#####################################################################"
echo "#           Iniciando configuración del usuario '$MONITOR_USER'     #"
echo "#          Por favor, introduce tu contraseña de administrador      #"
echo "#          cuando se te solicite (para sudo).                       #"
echo "#####################################################################"
echo ""

# Verificar si el script se ejecuta como root o con sudo
if [ "$EUID" -ne 0 ]; then
    echo "ERROR: Este script debe ejecutarse como root o con sudo."
    echo "Ejemplo: sudo bash $(basename "$0")"
    exit 1
fi

# 1. Detectar el sistema operativo y configurar el administrador de paquetes
if command -v apt &>/dev/null; then
    PACKAGE_MANAGER="apt"
    SSHD_PACKAGE="openssh-server"
    echo "Sistema operativo detectado: Debian/Ubuntu (usando apt)"
elif command -v yum &>/dev/null; then
    PACKAGE_MANAGER="yum"
    SSHD_PACKAGE="openssh-server"
    echo "Sistema operativo detectado: CentOS/RHEL (usando yum)"
elif command -v dnf &>/dev/null; then
    PACKAGE_MANAGER="dnf"
    SSHD_PACKAGE="openssh-server"
    echo "Sistema operativo detectado: Fedora (usando dnf)"
else
    echo "ERROR: Administrador de paquetes no soportado. Este script soporta Debian/Ubuntu, CentOS/RHEL/Fedora."
    exit 1
fi

# 2. Verificar, instalar y activar SSHD
echo "Verificando estado de SSHD..."
if ! systemctl is-active --quiet sshd; then
    echo "SSHD no está activo. Verificando instalación..."
    if ! command -v sshd &>/dev/null; then
        echo "SSHD no está instalado. Instalando '$SSHD_PACKAGE'..."
        $PACKAGE_MANAGER update -y
        $PACKAGE_MANAGER install -y "$SSHD_PACKAGE"
        if [ $? -ne 0 ]; then
            echo "ERROR: Falló la instalación de SSHD. Por favor, revisa los mensajes anteriores."
            exit 1
        fi
    fi

    echo "Habilitando e iniciando SSHD..."
    systemctl enable sshd
    systemctl start sshd
    if ! systemctl is-active --quiet sshd; then
        echo "ERROR: SSHD no pudo iniciarse. Por favor, verifica el servicio manualmente."
        exit 1
    fi
    echo "SSHD está ahora activo."
else
    echo "SSHD ya está activo y funcionando."
fi

# 3. Crear el usuario de monitoreo
echo "Verificando usuario '$MONITOR_USER'..."
if ! id "$MONITOR_USER" &>/dev/null; then
    useradd -m -s /bin/bash "$MONITOR_USER"
    echo "Usuario '$MONITOR_USER' creado con éxito."
else
    echo "Usuario '$MONITOR_USER' ya existe."
fi

# 4. Establecer la contraseña para el usuario de monitoreo
echo ""
echo "#####################################################################"
echo "# ¡IMPORTANTE! Establece la contraseña para el usuario '$MONITOR_USER'.   #"
echo "# **Esta contraseña es la que deberás ingresar en el formulario** #"
echo "# **de registro del servidor en la aplicación Django.** #"
echo "#####################################################################"
echo ""
passwd "$MONITOR_USER"
if [ $? -ne 0 ]; then
    echo "ERROR: Falló el establecimiento de la contraseña para '$MONITOR_USER'."
    exit 1
fi
echo "Contraseña para '$MONITOR_USER' establecida."

# 5. Configurar el directorio .ssh y el archivo authorized_keys para el usuario de monitoreo
MONITOR_HOME=$(getent passwd "$MONITOR_USER" | cut -d: -f6)
echo "Configurando directorio .ssh para '$MONITOR_USER' en $MONITOR_HOME..."
mkdir -p "$MONITOR_HOME/.ssh"
chmod 700 "$MONITOR_HOME/.ssh"
touch "$MONITOR_HOME/.ssh/authorized_keys"
chmod 600 "$MONITOR_HOME/.ssh/authorized_keys"
chown -R "$MONITOR_USER":"$MONITOR_USER" "$MONITOR_HOME/.ssh"
echo "Directorio .ssh configurado para '$MONITOR_USER'."

# 6. Configurar permisos sudo para systemctl (principio de mínimo privilegio)
echo "Configurando permisos sudo para '$MONITOR_USER'..."
if ! grep -q "# User privilege specification for monitoring" "$SUDOERS_FILE" &>/dev/null; then
    echo "# User privilege specification for monitoring" | sudo tee "$SUDOERS_FILE" > /dev/null
    echo "$MONITOR_USER ALL=(ALL) NOPASSWD: /usr/bin/systemctl restart *, /usr/bin/systemctl stop *, /usr/bin/systemctl start *, /usr/bin/systemctl status *" | sudo tee -a "$SUDOERS_FILE" > /dev/null
    sudo chmod 0440 "$SUDOERS_FILE" # Permisos estrictos para sudoers
    echo "Permisos sudo para systemctl configurados para '$MONITOR_USER' en '$SUDOERS_FILE'."
else
    echo "Permisos sudo ya existentes en '$SUDOERS_FILE'."
fi

echo ""
echo "#####################################################################"
echo "# Configuración de '$MONITOR_USER' completada exitosamente.      #"
echo "#                                                                   #"
echo "# ¡RECUERDA!: La contraseña que asignaste a '$MONITOR_USER' es la   #"
echo "# que debes usar en el formulario de registro de tu servidor en    #"
echo "# la aplicación Django.                                             #"
echo "#####################################################################"
echo ""

exit 0