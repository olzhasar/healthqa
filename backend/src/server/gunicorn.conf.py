wsgi_app = "app.main:app"
bind = "unix:/run/gunicorn/socket"
workers = 3
threads = 3
preload_app = True
keepalive = 5
max_requests = 100
