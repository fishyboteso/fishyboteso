#!/bin/bash

if [ -e /etc/os-release ]; then
    distro_info=$(cat /etc/os-release)
    
    if [[ $distro_info == *"Manjaro"* ]]; then
        echo "OS Manjaro: installing tk, python, python-pip, wmctrl"
        sudo pacman -Sy
        
        sudo pacman -S tk
        sudo pacman -S python
        sudo pacman -S python-pip
        sudo pacman -S wmctrl
    elif [[ $distro_info == *"Ubuntu"* ]]; then
        echo "OS Ubuntu: installing tk, python, python-pip, wmctrl"
        sudo apt update

        sudo apt-get install tk
        sudo apt-get install python
        sudo apt-get install python-pip
        sudo apt install wmctrl

    elif [[ $distro_info == *"Fedora"* ]]; then
        echo "OS Fedora: installing tk, python, python-pip, wmctrl"
        sudo dnf update

        sudo dnf install tk
        sudo dnf install python
        sudo dnf install python-pip
        sudo dnf install wmctrl

    else
        echo "Unknow OS: Try other Install Script for Your OS"
    fi
else
    echo "File /etc/os-release Not Found or OS Unknow Try other Install Script for Your OS"
fi
