#!/usr/bin/env bash
# Author: Vladyslav Adamovych + tteck-style adaptation
# License: MIT

function header_info {
clear
cat <<"EOF"
   __                _ __    __          __      __
  / /   ____  ____ _/ / /   / /   ____ _/ /_  __/ /__
 / /   / __ \/ __  / / /   / /   / __  / / / / / //_/
/ /___/ /_/ / /_/ / / /   / /___/ /_/ / / /_/ / ,<
\____/\____/\__,_/_/_/   /_____/\__,_/_/\__,_/_/|_|

          Simple LangGraph LinkedIn Jobs (LXC)
EOF
}

header_info

# Variables
CTID=${CTID:-111} # Changed default to not conflict with MCP server
HOSTNAME=${HOSTNAME:-linkedin-agent}
MEM=${MEM:-2048}
DISK=${DISK:-8}
CORES=${CORES:-2}
BRG=${BRG:-vmbr0}

YW=$(echo "\033[33m")
BL=$(echo "\033[36m")
RD=$(echo "\033[01;31m")
GN=$(echo "\033[1;92m")
CL=$(echo "\033[m")

# --- Critical User Interaction for .env file ---
echo -e "\n${RD}!!! ACTION REQUIRED !!!${CL}"
echo -e "This script requires a '.env' file to be present in the same directory."
echo -e "Please create and configure your '.env' file based on the '.env.example' from the repository."
echo -e "The script will push this file into the LXC container."

if [ ! -f ".env" ]; then
    echo -e "\n${RD}ERROR: '.env' file not found. Please create it and run the script again.${CL}"
    exit 1
fi

read -p "Press ${GN}[ENTER]${CL} to continue..."

# --- Create LXC Container ---
echo -e "\n${BL}Creating LXC Container: $CTID ($HOSTNAME)${CL}\n"
pct create $CTID local:vztmpl/debian-12-standard_12.7-1_amd64.tar.zst \
  --hostname $HOSTNAME \
  --cores $CORES \
  --memory $MEM \
  --swap 512 \
  --rootfs local-lvm:${DISK} \
  --net0 name=eth0,bridge=$BRG,ip=dhcp \
  --features nesting=1,keyctl=1 \
  --unprivileged 1

# --- Start container and wait for network ---
pct start $CTID
echo -e "${BL}Waiting for container to start and get an IP...${CL}"
sleep 5

# --- Run setup commands inside the LXC ---
echo -e "${BL}Updating OS and installing dependencies...${CL}"
pct exec $CTID -- bash -c "apt update && apt upgrade -y" >/dev/null
pct exec $CTID -- bash -c "apt install -y git python3-pip python3-venv" >/dev/null

echo -e "${BL}Cloning project repository...${CL}"
APP_DIR="/opt/linkedin-agent"
GIT_URL="https://github.com/VladislovePT/SimpleLangGraphLinkedInJobs.git"
pct exec $CTID -- bash -c "git clone $GIT_URL $APP_DIR" >/dev/null

echo -e "${BL}Pushing .env file into the container...${CL}"
pct push $CTID .env ${APP_DIR}/.env >/dev/null

echo -e "${BL}Setting up Python virtual environment and installing packages...${CL}"
pct exec $CTID -- bash -c "python3 -m venv ${APP_DIR}/venv" >/dev/null
pct exec $CTID -- bash -c "${APP_DIR}/venv/bin/pip install -r ${APP_DIR}/requirements.txt" >/dev/null

echo -e "${BL}Creating and enabling systemd service...${CL}"
SERVICE_NAME="linkedin-agent"
SERVICE_FILE="/etc/systemd/system/${SERVICE_NAME}.service"
pct exec $CTID -- bash -c "cat > ${SERVICE_FILE} << EOF
[Unit]
Description=LinkedIn Agent Service
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=${APP_DIR}
EnvironmentFile=${APP_DIR}/.env
ExecStart=${APP_DIR}/venv/bin/python rss_feed.py
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF"

pct exec $CTID -- systemctl daemon-reload
pct exec $CTID -- systemctl enable --now ${SERVICE_NAME}

# --- Final Instructions ---
echo -e "\n${GN}✅ LXC $CTID ($HOSTNAME) deployed successfully!${CL}"
echo -e "The application is running as a service inside the container."
echo -e "To find the IP address, run: ${BL}pct exec $CTID -- ip a${CL}"
echo -e "The RSS feed will be available at: ${BL}http://<LXC-IP>:5000/rss${CL}\n"