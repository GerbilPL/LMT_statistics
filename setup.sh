#!/bin/bash

# Get the script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PROJECT_DIR="$SCRIPT_DIR"

# App name
# Default: lmt_statistics
APP_NAME="lmt_statistics"
APP_NAME_NICE="LMT Statistics"

python3 -m venv "$PROJECT_DIR/venv"
source "$PROJECT_DIR/venv/bin/activate"

pip install -r "$PROJECT_DIR/requirements.txt"
pip install gunicorn

deactivate

sudo -v

# Install nginx if not present
if ! command -v nginx &> /dev/null
then
    sudo apt-get update
    sudo apt-get install nginx
fi

# Create nginx config file
NGINX_CONFIG="server {
    listen 80;
    server_name 127.0.0.1;

    location / {
        proxy_pass http://localhost:8050;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}"

echo "$NGINX_CONFIG" | sudo tee /etc/nginx/sites-available/$APP_NAME > /dev/null

sudo ln -sf /etc/nginx/sites-available/$APP_NAME /etc/nginx/sites-enabled/

sudo rm /etc/nginx/sites-enabled/default 2> /dev/null

# Create service file
SERVICE_FILE="[Unit]
Description=$APP_NAME_NICE Service
After=network.target

[Service]
User=$USER
WorkingDirectory=$PROJECT_DIR
Environment="PATH=$PROJECT_DIR/venv/bin"
ExecStart=$PROJECT_DIR/venv/bin/gunicorn -w 4 -b 127.0.0.1:8050 wsgi:server

[Install]
WantedBy=multi-user.target"

echo "$SERVICE_FILE" | sudo tee /etc/systemd/system/$APP_NAME.service > /dev/null

# Reload systemctl daemon and start the service
sudo systemctl daemon-reload
sudo systemctl enable $APP_NAME.service
sudo systemctl start $APP_NAME.service
sudo systemctl restart nginx