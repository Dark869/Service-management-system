#  Service management system

<div align="center">

![Django](https://img.shields.io/badge/django-5.1.7-green?style=for-the-badge&logo=django&color=green)
![Python](https://img.shields.io/badge/python-3.12-yellow?style=for-the-badge&logo=python)
![MySQL](https://img.shields.io/badge/mysql-8.1-blue?style=for-the-badge&logo=mysql)
![JQuery](https://img.shields.io/badge/jquery-3.7.1-blue?style=for-the-badge&logo=jquery)
![BootStrap](https://img.shields.io/badge/bootstrap-5.3.3-purple?style=for-the-badge&logo=bootstrap)
![Docker](https://img.shields.io/badge/Docker-Compose-blue?style=for-the-badge&logo=docker)

</div>

## Description

System to manage services of basic shape as register a service, list, up and down a service, and delete a service. The system is built using Django framework, MySQL database, and Docker for containerization.

This project was created to pass the final project of the course "Secure Programming" at the University Veracruzana. The system allows users to register a service, list all services, update the status of a service (up or down), and delete a service. The system is designed to be secure and follows best practices for web development as:

- Input validation to prevent SQL injection and other attacks (CSRF, XSS and code injection).
- Use of Django's built-in authentication system to manage user accounts and permissions.
- Use of HTTPS to encrypt data transmitted between the client and server.
- Use of password hashing to protect user passwords.
- Use captchas to prevent automated attacks.
- Implementation of rate limiting to prevent brute-force attacks.
- Authentication two-factor (2FA) using Telegram bot to send a code to the user's Telegram account for added security.

This project can be deployed on every platform that supports Docker.

## Installation

Before running the application, you need set the environment variables in the `.env` file in the case of linux or macOS, or set the environment variables in the system in the case of Windows. The required environment variables are:

```bash
# App
SECRET_KEY=your_secret_key_here
RECAPTCHA_PRIVATE_KEY=your_recaptcha_private_key_here
TOKEN_BOT=your_telegram_bot_token_here
CHAT_ID=your_telegram_chat_id_here

# SSH
SSH_PUBLIC=your_ssh_public_key_here
SSH_PRIVATE=your_ssh_private_key_here
FINGERPRINT=your_ssh_fingerprint_here
CLAVE_OF_KEY=your_ssh_key_passphrase_here

# Database
BD_NAME=your_database_name
BD_USER=your_database_user
BD_PASSWORD=your_database_password
BD_ROOT=your_root_password_here
BD_HOST=bd
BD_PORT=3306
```

After setting the environment variables, to run the application execute the `start.sh` script in the terminal in the case of linux of macOS:

```bash
cd Service-management-system
chmod +x start.sh
./start.sh
```

In the case of Windows, execute only the `docker compose up -d` command in the terminal:

```bash
cd Service-management-system
docker compose up -d
```

After running the application, you can access it in your web browser at `http://localhost:8000`.

## Usage

To use the application, you need to register an account. After registering, you can log in and start managing your services. You can register a new service by clicking on the "Register Service" button and filling out the form, you need to provide the public key ssh of the server. You can view all your services by clicking on the "List Services" button. You can update the status of a service by clicking on the "Update Status" button next to the service. You can delete a service by clicking on the "Delete" button next to the service.

## Authors

- [Victor Emmanuel López Espejo (Dark869)](https://github.com/Dark869)
- [Carlos Alberto Tamariz Morales (Monkey D. Cat)](https://github.com/CarlosAlbertoTamarizMorales)
- [Rodrigo Domínguez Jiménez](https://github.com/RodrigoDominguezJimenez)
