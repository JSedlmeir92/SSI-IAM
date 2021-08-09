#!/bin/bash

import os
import time

print("If you are executing this demo inside a virtual machine, make sure the following ports are open:"
      "\n7000 and 7080 (used for the HR agent)"
      "\n8000 and 8001 (used for the servers)"
      "\n9000 and 9080 (used for the intranet login agent)\n")

# Getting the IP ADDRESS
FileHandler = open("ip_address.txt", "a+")
if os.stat("ip_address.txt").st_size == 0:
    ip_address = input("\nPlease enter your IP address: ")
    FileHandler.write(ip_address)
else:
    FileHandler = open("ip_address.txt", "r")
    print("Your current IP address is set to:", FileHandler.read())
    print("Please change the IP address if necessary.\n")
FileHandler.close()


# HR Department
os.system("python3 hr/manage.py makemigrations")
os.system("python3 hr/manage.py migrate")
print("\nStarting the HR Server...")
os.system("gnome-terminal --geometry=50x54-100+0 --title=HR-Server -- python3 hr/manage.py runserver 0.0.0.0:8000")
print("Starting HR Agent...\n")
os.system("gnome-terminal --geometry=50x54+450+0 --title=HR-Agent -- docker-compose up hr-agent tails-server")

time.sleep(5)

# Intranet Login
os.system("python3 login/manage.py makemigrations")
os.system("python3 login/manage.py migrate")
print("\nStarting the Intranet Login Server...")
os.system("gnome-terminal --geometry=50x54+1000+0 --title=Intranet-Server -- python3 login/manage.py runserver 0.0.0.0:8001")
print("Starting Intranet Login Agent...")
os.system("gnome-terminal --geometry=50x54+1500+0 --title=Intranet-Agent -- docker-compose up intranet-agent")
print("Starting complete")