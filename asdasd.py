import paramiko
import time
from colorama import Fore, Back, Style, init
import pyfiglet
########################################################

########################################################
vps_ip = "109.x.218"
vps_user = ""
vps_pass = ""

emailmain = ""
domain = ".ru"

install_apache = True
install_php = True
install_certbot = True
configure_certbot = False
upload_zip = False
zip_file = "C:/a.zip"
########################################################

########################################################

init()  

fonts = ['slant']
colors = [Fore.RED]

for font in fonts:
    f = pyfiglet.Figlet(font=font)
    for color in colors:
        output = f.renderText('UNDER BYTES')
        print(color + output + Style.RESET_ALL)

def connect_to_vps(ip, user, password):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(ip, username=user, password=password)
    except Exception as e:
        print(f"Error al conectar: {e}")
        client = None
    return client

def execute_commands(client, commands):
    for command in commands:
        try:
            stdin, stdout, stderr = client.exec_command(command)
            print(stdout.read().decode())
            error = stderr.read().decode()
            if error:
                print(f"Error  {command}: {error}")
            time.sleep(1)
        except Exception as e:
            print(f"Error {command}: {e}")

def upload_file(client, local_path, remote_path):
    try:
        sftp = client.open_sftp()
        sftp.put(local_path, remote_path)
        sftp.close()
    except Exception as e:
        print(f"Error {e}")

def append_to_file(client, file_path, content):
    try:
        sftp = client.open_sftp()
        with sftp.file(file_path, 'a') as file:
            file.write(content)
        sftp.close()
    except Exception as e:
        print(f"Error{e}")

def detect_os(client):
    stdin, stdout, stderr = client.exec_command("cat /etc/os-release")
    output = stdout.read().decode().lower()
    if 'debian' in output or 'ubuntu' in output:
        return 'debian'
    elif 'centos' in output or 'fedora' in output or 'rhel' in output:
        return 'redhat'
    else:
        return None

remote_dir = "/var/www/html/main"
client = connect_to_vps(vps_ip, vps_user, vps_pass)
if not client:
    exit(1)

os_type = detect_os(client)
if not os_type:
    client.close()
    exit(1)

commands = []

if os_type == 'debian':
    if install_apache:
        commands.extend([
            "sudo apt update -y",
            "sudo apt install unzip -y",
            "sudo apt install apache2 -y",
            "sudo systemctl start apache2",
            "sudo systemctl enable apache2"
        ])
    if install_php:
        commands.extend([
            "sudo apt install software-properties-common -y",
            "sudo add-apt-repository ppa:ondrej/php -y",
            "sudo apt update -y",
            "sudo apt install php libapache2-mod-php php-mysql -y",
            "sudo systemctl restart apache2"
        ])
    if install_certbot:
        commands.extend([
            "sudo apt install certbot python3-certbot-apache -y"
        ])
elif os_type == 'redhat':
    if install_apache:
        commands.extend([
            "sudo yum update -y",
            "sudo yum install httpd -y",
            "sudo yum install unzip -y",
            "sudo systemctl start httpd",
            "sudo systemctl enable httpd"
        ])
    if install_php:
        commands.extend([
            "sudo yum install epel-release -y",
            "sudo yum install yum-utils -y",
            "sudo yum install http://rpms.remirepo.net/enterprise/remi-release-7.rpm -y",
            "sudo yum-config-manager --enable remi-php74",
            "sudo yum install php php-common php-opcache php-mcrypt php-cli php-gd php-curl php-mysqlnd -y",
            "sudo systemctl restart httpd"
        ])
    if install_certbot:
        commands.extend([
            "sudo yum install certbot python2-certbot-apache -y"
        ])

commands.append(f"sudo mkdir -p {remote_dir}")
commands.append(f"sudo chmod 755 {remote_dir}")
execute_commands(client, commands)

if upload_zip:
    remote_zip_path = f"/tmp/{zip_file.split('/')[-1]}"
    upload_file(client, zip_file, remote_zip_path)

    unzip_commands = [
        f"sudo unzip {remote_zip_path} -d {remote_dir}",
        f"sudo chown -R www-data:www-data {remote_dir}" if os_type == 'debian' else f"sudo chown -R apache:apache {remote_dir}"
    ]
    execute_commands(client, unzip_commands)

if install_certbot:
    apache_config = f"""
    <VirtualHost *:80>
        ServerName {domain}
        ServerAlias www.{domain}
        DocumentRoot /var/www/html
        Redirect permanent / https://{domain}/
    </VirtualHost>

    <VirtualHost *:443>
        ServerName {domain}
        ServerAlias www.{domain}
        DocumentRoot /var/www/html

        <Directory {remote_dir}>
            Options -Indexes +FollowSymLinks
            AllowOverride All
            Require all granted
        </Directory>

        ErrorLog /var/log/{'apache2' if os_type == 'debian' else 'httpd'}/{domain}-error.log
        CustomLog /var/log/{'apache2' if os_type == 'debian' else 'httpd'}/{domain}-access.log combined
    </VirtualHost>
    """

    config_file_path = "/etc/apache2/sites-available/000-default.conf" if os_type == 'debian' else "/etc/httpd/conf/httpd.conf"
    append_to_file(client, config_file_path, apache_config)
    execute_commands(client, ["sudo systemctl restart apache2" if os_type == 'debian' else "sudo systemctl restart httpd"])

if configure_certbot:
    certbot_command = f"sudo certbot --apache -d {domain} --non-interactive --agree-tos --email {emailmain}"
    execute_commands(client, [certbot_command])

client.close()
