# Complete Digital Ocean Deployment Guide - DevApply Backend

This guide will take you from creating a Digital Ocean account to having a fully working DevApply backend with background workers.

## Part 1: Create Digital Ocean Droplet

### Step 1: Sign Up / Login

1. Go to https://www.digitalocean.com/
2. Sign up or log in
3. You may get $200 credit for 60 days as a new user

### Step 2: Create a Droplet

1. Click **"Create"** → **"Droplets"**
2. Choose configuration:

**Choose an image:**
- **Distribution**: Ubuntu
- **Version**: 22.04 LTS x64 (recommended)

**Choose Size:**
- **Droplet Type**: Basic
- **CPU Options**: Regular
- **Size**:
  - For testing: **$6/month** (1 GB RAM, 1 vCPU, 25 GB SSD)
  - For production: **$12/month** (2 GB RAM, 1 vCPU, 50 GB SSD) - recommended

**Choose Region:**
- Select closest to your users (e.g., New York, San Francisco, London)

**Authentication:**
- Select **"SSH Key"** (more secure) or **"Password"**
- If SSH Key:
  - Click "New SSH Key"
  - On your local computer, run: `cat ~/.ssh/id_rsa.pub` (Mac/Linux) or use PuTTYgen (Windows)
  - Paste your public key
  - Name it (e.g., "My Laptop")

**Hostname:**
- Name: `devapply-backend` (or anything you want)

3. Click **"Create Droplet"**

4. Wait 1-2 minutes for droplet to be created

5. **Copy the IP address** (e.g., `164.90.123.45`)

## Part 2: Connect via SSH

### On Mac/Linux:

```bash
ssh root@YOUR_DROPLET_IP
```

Replace `YOUR_DROPLET_IP` with your actual IP.

If using SSH key, it will connect automatically.
If using password, enter the password sent to your email.

### On Windows:

Use **PuTTY** or **Windows Terminal**:
```bash
ssh root@YOUR_DROPLET_IP
```

### First Time Login

If asked "Are you sure you want to continue connecting?", type `yes`

You should now see:
```
Welcome to Ubuntu 22.04.3 LTS
root@devapply-backend:~#
```

## Part 3: Initial Server Setup

### Step 1: Update System

```bash
apt update
apt upgrade -y
```

This will take 2-3 minutes.

### Step 2: Set Timezone

```bash
timedatectl set-timezone UTC
```

### Step 3: Create a Non-Root User (Recommended for Security)

```bash
adduser devapply
```

Enter a password and press Enter for other prompts (can leave blank).

Add user to sudo group:
```bash
usermod -aG sudo devapply
```

Switch to new user:
```bash
su - devapply
```

Now you're logged in as `devapply` user (safer than root).

## Part 4: Install Dependencies

### Step 1: Install Python 3.10+

```bash
sudo apt install -y python3 python3-pip python3-venv python3-dev
```

Check version:
```bash
python3 --version
```

Should show Python 3.10 or higher.

### Step 2: Install PostgreSQL

```bash
sudo apt install -y postgresql postgresql-contrib
```

Start PostgreSQL:
```bash
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

### Step 3: Install Redis

```bash
sudo apt install -y redis-server
```

Start Redis:
```bash
sudo systemctl start redis-server
sudo systemctl enable redis-server
```

Test Redis:
```bash
redis-cli ping
```

Should return: `PONG`

### Step 4: Install Git

```bash
sudo apt install -y git
```

### Step 5: Install Nginx (Web Server)

```bash
sudo apt install -y nginx
```

### Step 6: Install Chrome and ChromeDriver (for Selenium automation)

```bash
# Install Chrome
wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
sudo sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list'
sudo apt update
sudo apt install -y google-chrome-stable

# Install ChromeDriver
CHROME_VERSION=$(google-chrome --version | awk '{print $3}' | cut -d. -f1)
wget https://chromedriver.storage.googleapis.com/LATEST_RELEASE_${CHROME_VERSION} -O /tmp/chrome_version
CHROMEDRIVER_VERSION=$(cat /tmp/chrome_version)
wget https://chromedriver.storage.googleapis.com/${CHROMEDRIVER_VERSION}/chromedriver_linux64.zip
unzip chromedriver_linux64.zip
sudo mv chromedriver /usr/local/bin/
sudo chmod +x /usr/local/bin/chromedriver
rm chromedriver_linux64.zip /tmp/chrome_version
```

Verify:
```bash
google-chrome --version
chromedriver --version
```

## Part 5: Setup Database

### Step 1: Create PostgreSQL Database and User

```bash
sudo -u postgres psql
```

You're now in PostgreSQL shell. Run these commands:

```sql
CREATE DATABASE devapplydb;
CREATE USER devapplyuser WITH PASSWORD 'your_strong_password_here';
ALTER ROLE devapplyuser SET client_encoding TO 'utf8';
ALTER ROLE devapplyuser SET default_transaction_isolation TO 'read committed';
ALTER ROLE devapplyuser SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE devapplydb TO devapplyuser;
\q
```

Replace `your_strong_password_here` with a strong password. **Save this password!**

## Part 6: Clone and Setup Application

### Step 1: Clone Repository

```bash
cd ~
git clone https://github.com/EmekaIwuagwu/devapply-backend-hub.git
cd devapply-backend-hub
```

### Step 2: Checkout Your Branch (with all fixes)

```bash
git checkout claude/fix-process-startup-logging-011TUF6MHxksZjkQBHeZoM8J
```

Or if you want main:
```bash
git checkout main
```

### Step 3: Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
```

Your prompt should now show `(venv)`.

### Step 4: Install Python Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn
```

This will take 3-5 minutes.

## Part 7: Configure Environment Variables

### Step 1: Generate Encryption Key

```bash
python3 generate_key.py
```

Copy the generated key (looks like: `yw1N4c0Gg0DH0bF-U5Le_khoqkKDLNqsK7EkkqhuSlw=`)

### Step 2: Create .env File

```bash
nano .env
```

Paste this content (replace values with your actual values):

```bash
# Flask
FLASK_APP=run.py
FLASK_ENV=production
SECRET_KEY=your-secret-key-generate-random-string

# Database
DATABASE_URL=postgresql://devapplyuser:your_db_password@localhost/devapplydb

# Redis
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# JWT
JWT_SECRET_KEY=your-jwt-secret-generate-random-string

# Encryption
CREDENTIALS_ENCRYPTION_KEY=your-generated-key-from-step-1

# Email (Optional - use Gmail)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASS=your-gmail-app-password
SMTP_FROM=noreply@devapply.com

# Rate Limiting
MAX_APPLICATIONS_PER_HOUR=5
MAX_APPLICATIONS_PER_DAY=20
APPLICATION_DELAY_SECONDS=180
```

**Important replacements:**
- `your_db_password` - The PostgreSQL password you created earlier
- `your-generated-key-from-step-1` - The encryption key you just generated
- `your-email@gmail.com` and `your-gmail-app-password` - Your Gmail credentials (get app password from Google account settings)

Save file: Press `Ctrl+X`, then `Y`, then `Enter`

## Part 8: Initialize Database

### Step 1: Run Migrations

```bash
source venv/bin/activate  # Make sure venv is active
export $(cat .env | xargs)  # Load environment variables
flask db upgrade
```

### Step 2: Seed Initial Data

```bash
flask seed_platforms
```

## Part 9: Create Systemd Services

These will keep your application running 24/7.

### Step 1: Create Web Service

```bash
sudo nano /etc/systemd/system/devapply-web.service
```

Paste this content (replace `/home/devapply` with your actual home path if different):

```ini
[Unit]
Description=DevApply Web Service (Gunicorn)
After=network.target postgresql.service redis.service

[Service]
User=devapply
Group=www-data
WorkingDirectory=/home/devapply/devapply-backend-hub
Environment="PATH=/home/devapply/devapply-backend-hub/venv/bin"
EnvironmentFile=/home/devapply/devapply-backend-hub/.env
ExecStart=/home/devapply/devapply-backend-hub/venv/bin/gunicorn \
    --workers 3 \
    --bind 127.0.0.1:5000 \
    --timeout 120 \
    --access-logfile /home/devapply/devapply-backend-hub/logs/access.log \
    --error-logfile /home/devapply/devapply-backend-hub/logs/error.log \
    run:app

Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Save: `Ctrl+X`, `Y`, `Enter`

### Step 2: Create Celery Worker Service

```bash
sudo nano /etc/systemd/system/devapply-worker.service
```

Paste:

```ini
[Unit]
Description=DevApply Celery Worker
After=network.target redis.service postgresql.service

[Service]
User=devapply
Group=devapply
WorkingDirectory=/home/devapply/devapply-backend-hub
Environment="PATH=/home/devapply/devapply-backend-hub/venv/bin"
EnvironmentFile=/home/devapply/devapply-backend-hub/.env
ExecStart=/home/devapply/devapply-backend-hub/venv/bin/celery -A celery_worker.celery worker \
    --loglevel=info \
    --concurrency=2 \
    --logfile=/home/devapply/devapply-backend-hub/logs/celery-worker.log

Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Save: `Ctrl+X`, `Y`, `Enter`

### Step 3: Create Celery Beat Service

```bash
sudo nano /etc/systemd/system/devapply-beat.service
```

Paste:

```ini
[Unit]
Description=DevApply Celery Beat Scheduler
After=network.target redis.service

[Service]
User=devapply
Group=devapply
WorkingDirectory=/home/devapply/devapply-backend-hub
Environment="PATH=/home/devapply/devapply-backend-hub/venv/bin"
EnvironmentFile=/home/devapply/devapply-backend-hub/.env
ExecStart=/home/devapply/devapply-backend-hub/venv/bin/celery -A celery_worker.celery beat \
    --loglevel=info \
    --logfile=/home/devapply/devapply-backend-hub/logs/celery-beat.log

Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Save: `Ctrl+X`, `Y`, `Enter`

## Part 10: Create Log Directory

```bash
mkdir -p ~/devapply-backend-hub/logs
chmod 755 ~/devapply-backend-hub/logs
```

## Part 11: Start All Services

### Step 1: Reload Systemd

```bash
sudo systemctl daemon-reload
```

### Step 2: Enable Services (auto-start on boot)

```bash
sudo systemctl enable devapply-web
sudo systemctl enable devapply-worker
sudo systemctl enable devapply-beat
```

### Step 3: Start Services

```bash
sudo systemctl start devapply-web
sudo systemctl start devapply-worker
sudo systemctl start devapply-beat
```

### Step 4: Check Status

```bash
sudo systemctl status devapply-web
sudo systemctl status devapply-worker
sudo systemctl status devapply-beat
```

Each should show `active (running)` in green.

If any service fails, check logs:
```bash
sudo journalctl -u devapply-web -n 50
sudo journalctl -u devapply-worker -n 50
sudo journalctl -u devapply-beat -n 50
```

## Part 12: Configure Nginx

### Step 1: Create Nginx Configuration

```bash
sudo nano /etc/nginx/sites-available/devapply
```

Paste (replace `YOUR_DROPLET_IP` with your actual IP):

```nginx
server {
    listen 80;
    server_name YOUR_DROPLET_IP;

    client_max_body_size 10M;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 120s;
        proxy_send_timeout 120s;
        proxy_read_timeout 120s;
    }
}
```

Save: `Ctrl+X`, `Y`, `Enter`

### Step 2: Enable Site

```bash
sudo ln -s /etc/nginx/sites-available/devapply /etc/nginx/sites-enabled/
sudo rm /etc/nginx/sites-enabled/default  # Remove default site
```

### Step 3: Test Nginx Configuration

```bash
sudo nginx -t
```

Should say "syntax is ok" and "test is successful"

### Step 4: Restart Nginx

```bash
sudo systemctl restart nginx
```

## Part 13: Test Your Deployment

### Test 1: Health Check

Open browser and go to:
```
http://YOUR_DROPLET_IP/health
```

You should see:
```json
{
  "success": true,
  "data": {
    "status": "healthy",
    "service": "DevApply Backend"
  }
}
```

### Test 2: System Status

```
http://YOUR_DROPLET_IP/api/system/status
```

You should see all services as "healthy" or "running":
```json
{
  "overall_status": "healthy",
  "services": {
    "web_api": { "status": "running" },
    "database": { "status": "connected" },
    "redis": { "status": "connected" },
    "celery_worker": { "status": "running", "message": "1 worker(s) active" },
    "celery_beat": { "status": "running" }
  }
}
```

### Test 3: Check Logs

```bash
# Web service logs
tail -f ~/devapply-backend-hub/logs/access.log
tail -f ~/devapply-backend-hub/logs/error.log

# Worker logs
tail -f ~/devapply-backend-hub/logs/celery-worker.log

# Beat logs
tail -f ~/devapply-backend-hub/logs/celery-beat.log

# Or use systemd logs
sudo journalctl -u devapply-worker -f
```

You should see:
- Worker logs: `celery@hostname ready`
- Beat logs: `beat: Starting...`

## Part 14: Optional - Setup Domain and SSL

### If You Have a Domain Name:

#### Step 1: Point Domain to Droplet

In your domain registrar (GoDaddy, Namecheap, etc.):
1. Create an A record
2. Name: `@` or `api`
3. Value: Your droplet IP
4. TTL: 300

Wait 5-10 minutes for DNS propagation.

#### Step 2: Update Nginx

```bash
sudo nano /etc/nginx/sites-available/devapply
```

Change `server_name YOUR_DROPLET_IP;` to:
```nginx
server_name yourdomain.com;
```

#### Step 3: Install SSL with Let's Encrypt

```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com
```

Follow prompts. Choose option 2 (redirect HTTP to HTTPS).

Your site will now be available at `https://yourdomain.com`

## Part 15: Firewall Setup (Security)

```bash
# Allow SSH (important - don't lock yourself out!)
sudo ufw allow 22/tcp

# Allow HTTP and HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Enable firewall
sudo ufw --force enable

# Check status
sudo ufw status
```

## Common Commands

### Restart Services

```bash
sudo systemctl restart devapply-web
sudo systemctl restart devapply-worker
sudo systemctl restart devapply-beat
sudo systemctl restart nginx
```

### View Logs

```bash
# Last 50 lines
sudo journalctl -u devapply-worker -n 50

# Follow logs (live)
sudo journalctl -u devapply-worker -f

# Application logs
tail -f ~/devapply-backend-hub/logs/celery-worker.log
```

### Update Application

```bash
cd ~/devapply-backend-hub
git pull
source venv/bin/activate
pip install -r requirements.txt
flask db upgrade
sudo systemctl restart devapply-web
sudo systemctl restart devapply-worker
sudo systemctl restart devapply-beat
```

### Check Service Status

```bash
sudo systemctl status devapply-web
sudo systemctl status devapply-worker
sudo systemctl status devapply-beat
```

## Troubleshooting

### Service Won't Start

```bash
# Check detailed logs
sudo journalctl -u devapply-worker -n 100 --no-pager

# Check if port 5000 is in use
sudo lsof -i :5000

# Check if Redis is running
redis-cli ping

# Check if PostgreSQL is running
sudo systemctl status postgresql
```

### Worker Not Processing Tasks

```bash
# Check if worker is registered
sudo journalctl -u devapply-worker | grep "celery@"

# Manually test worker
cd ~/devapply-backend-hub
source venv/bin/activate
export $(cat .env | xargs)
celery -A celery_worker.celery worker --loglevel=debug
```

### Database Connection Error

```bash
# Test database connection
sudo -u postgres psql devapplydb -U devapplyuser -W

# Check DATABASE_URL in .env file
cat ~/devapply-backend-hub/.env | grep DATABASE_URL
```

## Monitoring

### Check Resource Usage

```bash
# CPU and Memory
htop

# Or simpler
top

# Disk space
df -h

# Memory
free -h
```

### Check All Services At Once

```bash
systemctl status devapply-web devapply-worker devapply-beat nginx postgresql redis
```

## Backup

### Backup Database

```bash
# Create backup
sudo -u postgres pg_dump devapplydb > ~/backup-$(date +%Y%m%d).sql

# Restore backup
sudo -u postgres psql devapplydb < ~/backup-20251120.sql
```

## You're Done! 🎉

Your application is now running on Digital Ocean with:
- ✅ Web API on port 80 (via Nginx)
- ✅ PostgreSQL database
- ✅ Redis cache/queue
- ✅ Celery worker processing background jobs
- ✅ Celery beat scheduler running periodic tasks
- ✅ All services auto-restart on failure
- ✅ All services auto-start on server reboot

Access your API at: `http://YOUR_DROPLET_IP`

Check system status: `http://YOUR_DROPLET_IP/api/system/status`
