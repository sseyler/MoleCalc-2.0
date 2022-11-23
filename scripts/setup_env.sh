#!/usr/bin/env bash

REPO_DIR=$(pwd)/..

cd ${REPO_DIR}
conda env create -p env -f environment.yml
git clone -b main https://github.com/mscloudlab/ppqm ppqm.git
ln -s ppqm.git/ppqm ppqm

# Create directory for external assets; run setup_assets from Makefile
make setup_assets