# gunicorn.conf.py
import multiprocessing
import os
import sys

# Add the project to Python path
sys.path.append('/var/www/genome-editing-in-africa-backend')

# Virtual environment path
python_path = '/var/www/venv/bin/python'

# Socket path
bind = "unix:/var/www/genome-editing-in-africa-backend/gunicorn.sock"

# Workers
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = 'sync'
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 100

# Timeouts
timeout = 30
graceful_timeout = 30
keepalive = 2

# Logging
accesslog = '/var/log/gunicorn/access.log'
errorlog = '/var/log/gunicorn/error.log'
loglevel = 'info'

# Process naming
proc_name = 'genome_africa'

# User and group
user = 'www-data'
group = 'www-data'

# Preload app for better performance
preload_app = True

# Django settings module
os.environ['DJANGO_SETTINGS_MODULE'] = 'ged.settings'
