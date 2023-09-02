#!/bin/bash

if [ -e /etc/os-release ]; then
    distro_info=$(cat /etc/os-release)
    
    if [[ $distro_info == *"Manjaro"* ]]; then
        echo "OS Manjaro: installing tk, python, python-pip"
        sudo pacman -S tk
        sudo pacman -S python
        sudo pacman -S python-pip
    elif [[ $distro_info == *"Ubuntu"* ]]; then
        echo "OS Ubuntu: installing tk, python, python-pip"
        sudo apt-get install tk
        sudo apt-get install python
        sudo apt-get install python-pip
    elif [[ $distro_info == *"Fedora"* ]]; then
        echo "OS Fedora: installing tk, python, python-pip"
        sudo dnf install tk
        sudo dnf install python
        sudo dnf install python-pip
    else
        echo "Unknow OS: Try other Install Script for Your OS"
    fi
else
    echo "File /etc/os-release Not Found or OS Unknow Try other Install Script for Your OS"
fi
