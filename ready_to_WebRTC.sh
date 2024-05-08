#!/usr/bin/sh

sudo rpi-update -y

OS="`uname -a`"
CHECK_OS="`echo $OS | cut -d" " -f1`"

echo  ${CHECK_OS}

if [ "${OS}" = "Darwin" ]; then
	/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome -version
	brew install -cask chromedriver
	sudo spctl --master-disable 
else
	sudo apt-get purge -y chromium-browser
	sudo apt-get install -y chromium-browser
	sudo apt-get install -y chromium-chromedriver
fi
