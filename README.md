
# VPS Setup Automation Script

This Python script automates the setup and configuration of a VPS for web services. It uses `paramiko` for SSH connection, `colorama` for terminal customization, and `pyfiglet` for text banner rendering. It enables the installation of Apache, PHP, Certbot, and the option to upload a `.zip` file to configure a website.

## Features

- Connect to a VPS via SSH.
- Automatically detect the operating system of the VPS (Debian/Ubuntu or RedHat/CentOS).
- Automatically install Apache, PHP, and Certbot.
- Option to upload and extract a `.zip` file on the server.
- Configure SSL certificates with Certbot and Apache.
- Customizable terminal banners for aesthetics.

## Requirements

- Python 3.x
- Python libraries:
  - `paramiko`
  - `colorama`
  - `pyfiglet`

Install them using `pip`:

```bash
pip install paramiko colorama pyfiglet
```

## Usage

### Configuration

Before running the script, edit the following variables with the appropriate server information:

```python
vps_ip = "109.x.218"  # VPS IP address
vps_user = ""         # VPS username
vps_pass = ""         # VPS password

emailmain = ""        # Email for Certbot
domain = ".ru"        # Domain for SSL certificate

install_apache = True          # Install Apache (True or False)
install_php = True             # Install PHP (True or False)
install_certbot = True         # Install Certbot (True or False)
configure_certbot = False      # Auto configure Certbot (True or False)
upload_zip = False             # Upload a ZIP file (True or False)
zip_file = "C:/a.zip"          # Local path of the ZIP file to upload
```

### Execution

To run the script, execute the following command in the terminal:

```bash
python script_name.py
```

The script will automatically perform the following steps:
1. Connect to the VPS via SSH.
2. Detect the VPS operating system.
3. Install Apache, PHP, and Certbot based on the configuration.
4. Upload a `.zip` file and extract it into the `/var/www/html/main` directory (if enabled).
5. Configure Apache to use Certbot and enable SSL.

### Installation Options

- `install_apache`: Installs Apache on the VPS.
- `install_php`: Installs PHP and configures it with Apache.
- `install_certbot`: Installs Certbot for SSL certificate management.
- `configure_certbot`: Automatically configures Certbot with the specified domain.
- `upload_zip`: Upload and extract a `.zip` file on the server.

### Example Output

The script will print a banner in the terminal and then execute the installation and configuration commands:

```bash
UNDER BYTES
Connecting to VPS...
Installing Apache...
Installing PHP...
Configuring Certbot...
```
