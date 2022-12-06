#!/usr/bin/env bash

#--------------------------------------------------
# Intel oneAPI Base Toolkit for Linux
#    https://www.intel.com/content/www/us/en/developer/tools/oneapi/base-toolkit-download.html?operatingsystem=linux&distributions=offline
#---------------------------------
BASE_VERSION=2022.3.1.17310

# Earlier in 2022:
#wget https://registrationcenter-download.intel.com/akdlm/irc_nas/18673/l_BaseKit_p_2022.2.0.262_offline.sh
# Nov. 02, 2022:
wget https://registrationcenter-download.intel.com/akdlm/irc_nas/18970/l_BaseKit_p_2022.3.1.17310_offline.sh

# Run the installer in command-line mode using the flag -a with the --cli option
chmod u+x l_BaseKit_p_${BASE_VERSION}_offline.sh
sudo sh ./l_BaseKit_p_${BASE_VERSION}_offline.sh -a --cli


#--------------------------------------------------
# Intel oneAPI HPC Toolkit for Linux
#    https://www.intel.com/content/www/us/en/developer/tools/oneapi/hpc-toolkit-download.html?operatingsystem=linux&distributions=offline
#---------------------------------
HPC_VERSION=2022.3.1.16997

# Earlier in 2022:
#wget https://registrationcenter-download.intel.com/akdlm/irc_nas/18679/l_HPCKit_p_2022.2.0.191_offline.sh
# Nov. 02, 2022:
wget https://registrationcenter-download.intel.com/akdlm/irc_nas/18975/l_HPCKit_p_2022.3.1.16997_offline.sh

# Run the installer in command-line mode using the flag -a with the --cli option
chmod u+x l_HPCKit_p_${HPC_VERSION}_offline.sh
sudo sh ./l_HPCKit_p_${HPC_VERSION}_offline.sh -a --cli


# Environment setup
mkdir ~/scratch
mkdir -p ~/scratch/gamess/restart
mkdir -p ~/scratch/molecalc_data

sudo apt install -y csh patch

# Load Intel environment variables
source /opt/intel/oneapi/setvars.sh

HOMEDIR=/home/ubuntu
GMSPATH=/home/ubuntu/Library/gamess

cd $GMSPATH
./config

# Compile DDI
cd ${GMSPATH}/ddi
./compddi >& compddi.log
tail -n 20 compddi.log
mv ddikick.x ..

# Compile GAMESS
cd ${GMSPATH}
./compall >& compall.log
grep "cannot stat" compall.log

# Link GAMESS
./lked gamess 00 >& lked.log
tail -n 20 lked.log

# Edit rungms to point to the correct scratch and runtime directories

#set SCR=${HOMEDIR}/scratch/gamess/restart
#set USERSCR=${HOMEDIR}/scratch/gamess/restart
#set GMSPATH=${HOMEDIR}/Library/gamess

# Test GAMESS
cd ${GMSPATH}
./runall 00
./tests/standard/checktst
