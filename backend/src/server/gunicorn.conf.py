wsgi_app = "app.main:app"
bind = "unix:/run/gunicorn/socket"
workers = 3
keepalive = 5
max_requests = 100
