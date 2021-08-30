wsgi_app = "app.main:app"
bind = "unix:/run/gunicorn/socket"
workers = 1
threads = 4
keepalive = 5
max_requests = 100
