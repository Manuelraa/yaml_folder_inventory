#!/bin/bash 
set -xe

mkdir ./dist || true
cp -r galaxy.yml CHANGELOG.rst LICENSE README.md plugins meta ./dist
cd ./dist
ansible-galaxy collection build -v .
