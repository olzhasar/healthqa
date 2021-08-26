wsgi_app = "app.main:app"
bind = "0.0.0.0:8000"
workers = 3
keepalive = 5
max_requests = 100
