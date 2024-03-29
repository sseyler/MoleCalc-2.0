#!/usr/bin/env bash

# Consider running these two commands separately
# Do a reboot before continuing.
sudo apt update
sudo apt upgrade -y

sudo apt install zsh -y
echo Y | sh -c "$(curl -fsSL https://raw.github.com/robbyrussell/oh-my-zsh/master/tools/install.sh)"
sudo chsh -s $(which zsh) "$USER" && zsh
git clone https://github.com/romkatv/powerlevel10k.git "$ZSH_CUSTOM"/themes/powerlevel10k
### Enable powerlevel10k theme by setting in the ~/.zshrc file:
# ZSH_THEME="powerlevel10k/powerlevel10k"
### zsh-syntax-highlighting
# git clone https://github.com/zsh-users/zsh-syntax-highlighting.git ${ZSH_CUSTOM:-~/.oh-my-zsh/custom}/plugins/zsh-syntax-highlighting
### zsh-autosuggestions
# git clone https://github.com/zsh-users/zsh-autosuggestions ${ZSH_CUSTOM:-~/.oh-my-zsh/custom}/plugins/zsh-autosuggestions
### Activate the plugins by setting in the ~/.zshrc file:
# plugins=( git zsh-syntax-highlighting zsh-autosuggestions )
#sudo apt install ruby-full
#sudo gem install colorls
#if [ -x "$(command -v colorls)" ]; then
#    alias ls="colorls"
#    alias la="colorls -al"
#fi

# Set environment variables after starting zsh
WORKDIR="$PWD"
REPO_NAME=MoleCalc
APP_NAME=molecalc
REPO_PATH=/apps/${REPO_NAME}
MOLECALC_GITHUB=https://github.com/sseyler/MoleCalc-2.0.git
PPQM_GITHUB=https://github.com/mscloudlab/ppqm

# Create common directories
mkdir ~/Library ~/Downloads

# Install some OS dependencies:
sudo apt install -y -q build-essential git unzip zip nload tree httpie expect
#sudo apt install -y -q python3-pip python3-dev python3-venv
sudo apt install -y -q nginx
# for gzip support in uwsgi
sudo apt install --no-install-recommends -y -q libpcre3-dev libz-dev
# Stop the hackers
sudo apt install fail2ban -y

sudo ufw allow 22
sudo ufw allow 80
sudo ufw allow 443
echo -e "y\n" | sudo ufw enable

# Basic git setup
git config --global credential.helper cache
git config --global credential.helper 'cache --timeout=720000'

# Be sure to put your info here:
git config --global user.email "slseyler@asu.com"
git config --global user.name "Sean L Seyler"

# TODO Currently doing /apps (but do we want a local ~/apps install?)
# Web app file structure
sudo mkdir /apps
sudo chmod 777 /apps
sudo mkdir /apps/logs
sudo mkdir /apps/logs/${APP_NAME}
sudo mkdir /apps/logs/${APP_NAME}/app_log

# Clone the app repository:
cd /apps
git clone ${MOLECALC_GITHUB} ${REPO_NAME}

# Install mambaforge
cd Downloads
curl -L -O "https://github.com/conda-forge/miniforge/releases/latest/download/Mambaforge-$(uname)-$(uname -m).sh"
$REPO_PATH/scripts/autoinstall_mambaforge.sh "$(uname)-$(uname -m)" "${HOME}"/Library/mambaforge

# Set short conda environment name for prompt
cd /apps
conda config --set env_prompt '({name}) ' && . ~/.zshrc
conda env create -p env -f ${REPO_NAME}/environment.yml
conda activate ./env
# TODO: might require running "conda init zsh" to get "conda activate ./env" working...

# Set up the web app environment:
cd ${REPO_PATH}
pip install -e molecalc
git clone -b main ${PPQM_GITHUB} ppqm.git
ln -s ppqm.git/ppqm ppqm
make setup_assets

# Copy and enable the daemon
sudo cp ${REPO_PATH}/server/${APP_NAME}.service /etc/systemd/system/${APP_NAME}.service
sudo systemctl start ${APP_NAME}
sudo systemctl status ${APP_NAME} | tee -a /apps/logs/${APP_NAME}/${APP_NAME}.status
sudo systemctl enable ${APP_NAME}

# Set up NGINX as the public-facing server (already installed in Ubuntu 20.04 LTS)
#sudo apt install nginx

# CAREFUL HERE. If you are using default, maybe skip this
sudo rm /etc/nginx/sites-enabled/default

sudo cp ${REPO_PATH}/server/${APP_NAME}.nginx /etc/nginx/sites-enabled/${APP_NAME}.nginx
sudo update-rc.d nginx enable
sudo service nginx restart


# Optionally add SSL support via Let's Encrypt:
# https://www.digitalocean.com/community/tutorials/how-to-secure-nginx-with-let-s-encrypt-on-ubuntu-18-04

#sudo add-apt-repository ppa:certbot/certbot
#sudo apt install python-certbot-nginx
#certbot --nginx -d molecalc.cloud

# Updated certbot instructions
#sudo snap install core; sudo snap refresh core
#sudo snap install --classic certbot
#sudo ln -s /snap/bin/certbot /usr/bin/certbot
#sudo certbot --nginx
#sudo certbot renew --dry-run