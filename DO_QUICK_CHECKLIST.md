# Digital Ocean Deployment - Quick Checklist

Use this as a quick reference while following the full guide in DIGITALOCEAN_DEPLOYMENT.md

## Pre-Deployment

- [ ] Digital Ocean account created
- [ ] Droplet created (Ubuntu 22.04, $12/month recommended)
- [ ] Droplet IP address copied: `________________`
- [ ] SSH access working: `ssh root@YOUR_IP`

## Installation Steps

- [ ] System updated: `apt update && apt upgrade -y`
- [ ] Python installed: `apt install -y python3 python3-pip python3-venv python3-dev`
- [ ] PostgreSQL installed: `apt install -y postgresql postgresql-contrib`
- [ ] Redis installed: `apt install -y redis-server`
- [ ] Git installed: `apt install -y git`
- [ ] Nginx installed: `apt install -y nginx`
- [ ] Chrome + ChromeDriver installed

## Database Setup

- [ ] PostgreSQL database created: `devapplydb`
- [ ] PostgreSQL user created: `devapplyuser`
- [ ] Database password saved: `________________`

## Application Setup

- [ ] Repository cloned: `git clone https://github.com/EmekaIwuagwu/devapply-backend-hub.git`
- [ ] Branch checked out: `git checkout claude/fix-process-startup-logging-011TUF6MHxksZjkQBHeZoM8J`
- [ ] Virtual environment created: `python3 -m venv venv`
- [ ] Dependencies installed: `pip install -r requirements.txt`
- [ ] Encryption key generated: `________________`
- [ ] `.env` file created with all variables
- [ ] Database migrations run: `flask db upgrade`
- [ ] Platforms seeded: `flask seed_platforms`

## Services Setup

- [ ] Web service file created: `/etc/systemd/system/devapply-web.service`
- [ ] Worker service file created: `/etc/systemd/system/devapply-worker.service`
- [ ] Beat service file created: `/etc/systemd/system/devapply-beat.service`
- [ ] Log directory created: `~/devapply-backend-hub/logs`
- [ ] Services enabled and started

## Nginx Setup

- [ ] Nginx config created: `/etc/nginx/sites-available/devapply`
- [ ] Site enabled: `ln -s /etc/nginx/sites-available/devapply /etc/nginx/sites-enabled/`
- [ ] Nginx configuration tested: `nginx -t`
- [ ] Nginx restarted

## Verification

- [ ] Health endpoint works: `http://YOUR_IP/health`
- [ ] System status shows all healthy: `http://YOUR_IP/api/system/status`
- [ ] Web service running: `systemctl status devapply-web`
- [ ] Worker running: `systemctl status devapply-worker`
- [ ] Beat running: `systemctl status devapply-beat`
- [ ] Worker logs show "celery@hostname ready"
- [ ] Beat logs show "beat: Starting..."

## Security (Optional but Recommended)

- [ ] Firewall enabled: `ufw enable`
- [ ] SSH allowed: `ufw allow 22`
- [ ] HTTP/HTTPS allowed: `ufw allow 80,443/tcp`
- [ ] Non-root user created: `adduser devapply`
- [ ] Services running as non-root user

## Domain & SSL (Optional)

- [ ] Domain pointed to droplet IP
- [ ] Nginx updated with domain name
- [ ] SSL certificate installed: `certbot --nginx`
- [ ] HTTPS working

## Troubleshooting Commands

If something goes wrong:

```bash
# Check service status
systemctl status devapply-web devapply-worker devapply-beat

# View logs
journalctl -u devapply-worker -n 50
tail -f ~/devapply-backend-hub/logs/celery-worker.log

# Restart services
systemctl restart devapply-web devapply-worker devapply-beat

# Test database connection
sudo -u postgres psql devapplydb -U devapplyuser

# Test Redis
redis-cli ping

# Check environment variables
cat ~/devapply-backend-hub/.env
```

## Key File Locations

- Application: `/home/devapply/devapply-backend-hub/`
- Environment: `/home/devapply/devapply-backend-hub/.env`
- Logs: `/home/devapply/devapply-backend-hub/logs/`
- Nginx config: `/etc/nginx/sites-available/devapply`
- Service files: `/etc/systemd/system/devapply-*.service`

## Important Info to Save

- Droplet IP: `________________`
- Database Password: `________________`
- Encryption Key: `________________`
- JWT Secret: `________________`
- Gmail App Password: `________________`

## After Deployment

Your API will be available at:
- Health: `http://YOUR_IP/health`
- Status: `http://YOUR_IP/api/system/status`
- API endpoints: `http://YOUR_IP/api/...`

All background processing will work automatically!
