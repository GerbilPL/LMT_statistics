#!/bin/bash

# Default values
DEFAULT_SERVER_NAME="127.0.0.1"
DEFAULT_SERVER_PORT=80
DEFAULT_APP_NAME="lmt_statistics"
DEFAULT_APP_NAME_NICE="LMT Statistics"

# Default value for proxy path
PROXY_PASS="http://localhost:8050"
DASH_SERVER="127.0.0.1:8050"

# Default value for project directory, script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
DEFAULT_PROJECT_DIR="$SCRIPT_DIR"

# Parse command line arguments
while getopts ":dhs:p:P:a:" opt; do
  case ${opt} in
    d )
      SKIP_DIST_CHECK=true
      ;;
    s )
      SERVER_NAME=$OPTARG
      ;;
    p )
      SERVER_PORT=$OPTARG
      ;;
    P )
      PROJECT_DIR=$OPTARG
      ;;
    a )
      if [[ "$OPTARG" ]]; then
        APP_NAME=$OPTARG
        shift $((OPTIND -1))
        if [[ "$1" ]]; then
          APP_NAME_NICE=$1
          shift $((OPTIND -1))
        fi
      fi
      ;;
    h )
      echo "Usage: setup.sh [-h] [-d] [-s SERVER_NAME] [-s SERVER_PORT] [-P PROJECT_DIR] [-a APP_NAME APP_NAME_NICE]"
      echo "  -d: Skip distribution check"
      echo "  -s SERVER_NAME: Server name"
      echo "  -p SERVER_PORT: Server port"
      echo "  -P PROJECT_DIR: Project directory"
      echo "  -a APP_NAME: Application name APP_NAME_NICE: Nicer application name (with spaces etc)"
      echo "  -h: Show this help message"
      echo ""
      echo "Note: -s and -p do not refer to internal dash server, which is by default run on 127.0.0.1:8050"
      echo " You can also change that by modifying PROXY_PASS and DASH_SERVER variables in setup.sh"
      echo " Current values: PROXY_PASS=$PROXY_PASS, DASH_SERVER=$DASH_SERVER"
      exit 0
      ;;
    \? )
      echo "Invalid option: $OPTARG" 1>&2
      exit 1
      ;;
    : )
      echo "Invalid option: $OPTARG requires an argument" 1>&2
      exit 1
      ;;
  esac
done
shift $((OPTIND -1))

# Skip distribution check if specified
if [ "$SKIP_DIST_CHECK" = true ]; then
    echo "Skipping distribution check"
else
    UNAME=$(uname | tr "[:upper:]" "[:lower:]")
    # If Linux, try to determine specific distribution
    if [ "$UNAME" == "linux" ]; then
        # If available, use LSB to identify distribution
        if [ -f /etc/lsb-release -o -d /etc/lsb-release.d ]; then
            export DISTRO=$(lsb_release -i | cut -d: -f2 | sed s/'^\t'//)
        # Otherwise, use release info file
        else
            export DISTRO=$(ls -d /etc/[A-Za-z]*[_-][rv]e[lr]* | grep -v "lsb" | cut -d'/' -f3 | cut -d'-' -f1 | cut -d'_' -f1)
        fi
    fi
    # For everything else (or if above failed), just use generic identifier
    [ "$DISTRO" == "" ] && export DISTRO=$UNAME
    unset UNAME

    if [ "$DISTRO" != "Ubuntu" ]; then
        echo "Only Ubuntu is supported"
        exit 1
    else
        echo "Script is running on Ubuntu. Continuing..."
    fi
fi

# If not specified, use default values
SERVER_NAME=${SERVER_NAME:-$DEFAULT_SERVER_NAME}
SERVER_PORT=${SERVER_PORT:-$DEFAULT_SERVER_PORT}
APP_NAME=${APP_NAME:-$DEFAULT_APP_NAME}
APP_NAME_NICE=${APP_NAME_NICE:-$DEFAULT_APP_NAME_NICE}
PROJECT_DIR=${PROJECT_DIR:-$DEFAULT_PROJECT_DIR}

echo "Using server name: $SERVER_NAME"
echo "Using server port: $SERVER_PORT"
echo "Using app name: $APP_NAME"
echo "Using nicer app name: $APP_NAME_NICE"
echo "Using project directory: $PROJECT_DIR"

while true; do
    read -p "Do you wish to continue? y/n? " yn
    case $yn in
        [Yy]* ) break;;
        [Nn]* ) exit 0;;
        * ) echo "Please answer yes or no.";;
    esac
done

# Check if sudo access is available
sudo -v

# Install Python3 if not present
if ! command -v python3 &> /dev/null; then
    sudo apt-get update
    sudo apt-get install -y python3
fi

# Create virtual environment
python3 -m venv "$PROJECT_DIR/venv"
source "$PROJECT_DIR/venv/bin/activate"

# Install Python dependencies
pip install -r "$PROJECT_DIR/requirements.txt"
pip install gunicorn

# Deactivate virtual environment
deactivate

# Install Nginx if not present
if ! command -v nginx &> /dev/null; then
    sudo apt-get update
    sudo apt-get install -y nginx
fi

# Create Nginx config file
NGINX_CONFIG="server {
    listen $SERVER_PORT;
    server_name $SERVER_NAME;

    location / {
        proxy_pass $PROXY_PASS;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}"

echo "$NGINX_CONFIG" | sudo tee "/etc/nginx/sites-available/$APP_NAME" > /dev/null

sudo ln -sf "/etc/nginx/sites-available/$APP_NAME" "/etc/nginx/sites-enabled/"

sudo rm "/etc/nginx/sites-enabled/default" 2> /dev/null

# Create systemd service file
SERVICE_FILE="[Unit]
Description=$APP_NAME_NICE Service
After=network.target

[Service]
User=$USER
WorkingDirectory=$PROJECT_DIR
Environment=\"PATH=$PROJECT_DIR/venv/bin\"
ExecStart=$PROJECT_DIR/venv/bin/gunicorn -w 4 -b $DASH_SERVER wsgi:server

[Install]
WantedBy=multi-user.target"

echo "$SERVICE_FILE" | sudo tee "/etc/systemd/system/$APP_NAME.service" > /dev/null

# Reload systemctl daemon and start the service
sudo systemctl daemon-reload
sudo systemctl enable "$APP_NAME.service"
sudo systemctl start "$APP_NAME.service"
sudo systemctl restart nginx