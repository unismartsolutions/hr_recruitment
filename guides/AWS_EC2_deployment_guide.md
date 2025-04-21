# HR Recruitment System - AWS EC2 Deployment Guide

This guide provides step-by-step instructions for deploying the HR Recruitment System to an AWS EC2 instance with PostgreSQL database.

## Prerequisites

- AWS account with necessary permissions
- Access to AWS Management Console
- Basic knowledge of Linux command line
- Git installed on your local machine

## Step 1: Launch an EC2 Instance

1. Log in to the AWS Management Console
2. Navigate to EC2 Dashboard
3. Click on "Launch Instance"
4. Select an Amazon Machine Image (AMI)
   - Recommended: Amazon Linux 2023 or Ubuntu Server 22.04 LTS
5. Choose an instance type
   - Recommended: t2.micro (free tier) or t3.small for production
6. Configure instance details
   - Default VPC and subnet is usually sufficient
   - Enable auto-assign public IP
7. Add storage
   - Default 8GB is usually sufficient to start
8. Add tags (optional)
   - Key: Name, Value: HR-Recruitment-System
9. Configure security group
   - Create a new security group with the following rules:
     - SSH (port 22) from your IP address
     - HTTP (port 80) from anywhere
     - HTTPS (port 443) from anywhere
     - Custom TCP (port 5432) from the instance's security group (for PostgreSQL)
10. Review and launch
11. Create or select an existing key pair
    - Download the key pair (.pem file) and keep it secure
12. Launch instance

## Step 2: Connect to the EC2 Instance

### For Linux/macOS:

```bash
chmod 400 your-key-pair.pem
ssh -i your-key-pair.pem ec2-user@your-instance-public-dns
```

### For Windows:

Use PuTTY or Windows Subsystem for Linux (WSL) to connect using the .pem file.

## Step 3: Update the System and Install Dependencies

### For Amazon Linux 2023:

```bash
# Update system packages
sudo yum update -y

# Install Python, PostgreSQL, Git, and other dependencies
sudo yum install -y python3 python3-pip python3-devel postgresql postgresql-server postgresql-devel git nginx

# Initialize PostgreSQL
sudo postgresql-setup --initdb

# Start and enable PostgreSQL service
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Start and enable Nginx
sudo systemctl start nginx
sudo systemctl enable nginx

# Install AWS CLI for backup script
sudo yum install -y awscli
```

### For Ubuntu Server:

```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Install Python, PostgreSQL, Git, and other dependencies
sudo apt install -y python3 python3-pip python3-dev postgresql postgresql-contrib libpq-dev git nginx

# PostgreSQL is started automatically on Ubuntu
# Check status
sudo systemctl status postgresql

# Start and enable Nginx
sudo systemctl start nginx
sudo systemctl enable nginx

# Install AWS CLI for backup script
sudo apt install -y awscli
```

## Step 4: Clone the Repository

```bash
# Create directory for application
sudo mkdir -p /var/www/hr_recruitment
sudo chown $USER:$USER /var/www/hr_recruitment

# Clone the repository
cd /var/www/hr_recruitment
git clone https://your-repository-url.git .
```

## Step 5: Set Up PostgreSQL Database

```bash
# Switch to postgres user
sudo -i -u postgres

# Create database and user
psql

CREATE DATABASE hr_recruitment;
CREATE USER hr_user WITH ENCRYPTED PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE hr_recruitment TO hr_user;
\q

# Exit postgres user
exit

# Initialize database with schema
psql -U hr_user -d hr_recruitment -f /var/www/hr_recruitment/scripts/db_init.sql
```

## Step 6: Set Up Python Environment

```bash
# Create and activate virtual environment
cd /var/www/hr_recruitment
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt
pip install gunicorn  # Production WSGI server
```

## Step 7: Configure Environment Variables

Create a .env file in the application directory:

```bash
nano /var/www/hr_recruitment/.env
```

Add the following content:

```
SECRET_KEY=your_secure_secret_key
DATABASE_URL=postgresql://hr_user:your_secure_password@localhost/hr_recruitment
OPENAI_API_KEY=your_openai_api_key
UPLOAD_FOLDER=/var/www/hr_recruitment/app/static/uploads

# Backup configuration
DB_NAME=hr_recruitment
DB_USER=hr_user
DB_PASSWORD=your_secure_password
DB_HOST=localhost
DB_PORT=5432
BACKUP_DIR=/var/backups/hr_recruitment

# Optional S3 backup configuration
S3_BUCKET=your-backup-bucket-name
```

Set proper permissions:

```bash
chmod 600 /var/www/hr_recruitment/.env
```

## Step 8: Initialize the Application

```bash
# Make sure virtual environment is activated
cd /var/www/hr_recruitment
source venv/bin/activate

# Initialize the database
export FLASK_APP=run.py
flask init-db

# Create upload directory with proper permissions
mkdir -p app/static/uploads
chmod 755 app/static/uploads
```

## Step 9: Configure Gunicorn Systemd Service

Create a systemd service file:

```bash
sudo nano /etc/systemd/system/hr_recruitment.service
```

Add the following content:

```
[Unit]
Description=HR Recruitment System
After=network.target postgresql.service

[Service]
User=ec2-user  # or ubuntu for Ubuntu server
Group=ec2-user  # or ubuntu for Ubuntu server
WorkingDirectory=/var/www/hr_recruitment
Environment="PATH=/var/www/hr_recruitment/venv/bin"
EnvironmentFile=/var/www/hr_recruitment/.env
ExecStart=/var/www/hr_recruitment/venv/bin/gunicorn -w 4 -b 127.0.0.1:8000 'run:app'
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start the service:

```bash
sudo systemctl enable hr_recruitment
sudo systemctl start hr_recruitment
sudo systemctl status hr_recruitment
```

## Step 10: Configure Nginx as Reverse Proxy

Create an Nginx configuration file:

```bash
sudo nano /etc/nginx/conf.d/hr_recruitment.conf
```

Add the following content:

```
server {
    listen 80;
    server_name your_domain_or_ip;

    location /static {
        alias /var/www/hr_recruitment/app/static;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Increase maximum file upload size (to handle large CVs)
    client_max_body_size 16M;
}
```

Test and reload Nginx:

```bash
sudo nginx -t
sudo systemctl reload nginx
```

## Step 11: Set Up Database Backup

Make the backup script executable:

```bash
chmod +x /var/www/hr_recruitment/scripts/backup.sh
```

Set up a cron job to run daily backups:

```bash
sudo crontab -e
```

Add the following line:

```
0 2 * * * /var/www/hr_recruitment/scripts/backup.sh >> /var/log/hr_backup.log 2>&1
```

This will run the backup script every day at 2:00 AM.

## Step 12: Set Up HTTPS with Let's Encrypt (Optional but Recommended)

For a production environment, secure your application with HTTPS:

```bash
# Install Certbot
# For Amazon Linux 2023
sudo dnf install -y python3-certbot-nginx

# For Ubuntu
sudo apt install -y certbot python3-certbot-nginx

# Obtain and install certificate
sudo certbot --nginx -d your_domain.com

# Certbot will update your Nginx configuration automatically
# Verify renewal works
sudo certbot renew --dry-run
```

## Step 13: Final Tests

Access your application via web browser:

```
http://your_domain_or_ip
```

The default admin credentials are:
- Username: admin
- Password: admin123

**Important:** Change the default admin password immediately after first login!

### To create a new user from command line:

```bash
cd /var/www/hr_recruitment
source venv/bin/activate
export FLASK_APP=run.py
flask create-user
```

## Troubleshooting

### Check application logs:

```bash
sudo journalctl -u hr_recruitment.service
```

### Check Nginx logs:

```bash
sudo tail -f /var/log/nginx/error.log
sudo tail -f /var/log/nginx/access.log
```

### Check PostgreSQL logs:

```bash
# Amazon Linux 2023
sudo tail -f /var/lib/pgsql/data/log/postgresql-*.log

# Ubuntu
sudo tail -f /var/log/postgresql/postgresql-*.log
```

## Security Best Practices

1. Use strong passwords for PostgreSQL and application users
2. Keep your EC2 instance and all packages updated
3. Use a restrictive security group that only allows necessary traffic
4. Configure AWS Identity and Access Management (IAM) correctly
5. Use HTTPS with valid SSL/TLS certificates
6. Regularly backup your database
7. Monitor your instance for unusual activity

## Recovery Plan

If your EC2 instance fails, you can recover your system by:

1. Launch a new EC2 instance
2. Install all the required software as described above
3. Clone the repository from Git
4. Restore the database from the latest backup:

```bash
# Restore from a backup file
gunzip -c /path/to/backup/hr_recruitment_YYYYMMDD_HHMMSS.sql.gz > restored.sql
psql -U hr_user -d hr_recruitment -f restored.sql

# Or restore from S3 (if S3 backup is configured)
aws s3 cp s3://your-backup-bucket-name/hr_recruitment_backups/latest-backup.sql.gz .
gunzip -c latest-backup.sql.gz > restored.sql
psql -U hr_user -d hr_recruitment -f restored.sql
```

5. Update the configuration as needed
6. Start the services

## Scaling Considerations

For higher traffic or larger databases:

1. Upgrade your EC2 instance type for more CPU and memory
2. Consider using RDS for PostgreSQL for better database management
3. Implement an Application Load Balancer with multiple EC2 instances
4. Use Amazon S3 for storing uploaded CVs instead of local storage
5. Implement caching with Redis or Memcached for faster responses

## Conclusion

Your HR Recruitment System should now be running on AWS EC2. Remember to:

- Regularly update your system packages
- Monitor system performance
- Verify that backups are working correctly
- Change default credentials
- Follow security best practices

For additional help, refer to the AWS EC2 documentation or contact your system administrator.
