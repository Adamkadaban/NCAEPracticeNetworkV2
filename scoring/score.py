from flask import Flask, render_template
import socket
import os
import paramiko
from ftplib import FTP
import pymysql
import schedule
import time
import threading
from scapy.all import IP, ICMP, sr
import requests
from io import BytesIO

app = Flask(__name__)

team_number = '1'

# Define service details
services = {
    'ICMP BACKUP': {'ip': f'192.168.{team_number}.11', 'port': 0, 'points': 10},
    'ICMP DB': {'ip': f'192.168.{team_number}.12', 'port': 0, 'points': 10},
    'ICMP FILESHARE': {'ip': f'192.168.{team_number}.13', 'port': 0, 'points': 10},
    'ICMP WEB': {'ip': f'192.168.{team_number}.14', 'port': 0, 'points': 10},
    'ICMP WKST': {'ip': f'192.168.{team_number}.15', 'port': 0, 'points': 10},
    'SSH': {'host': f'192.168.{team_number}.15', 'users': ['j.wilson', 'c.resch', 'j.rice'], 'passwords': ['hackertracker', 'entsecrules', 'ufsitnumberone'], 'points': 20},
    'FTP': {'host': f'192.168.{team_number}.13', 'user': 'j.rice', 'password': 'ufsitnumberone', 'file': 'important_document.txt', 'points': 10},
    'WEB': {'host': f'192.168.{team_number}.14', 'port': 80, 'content': 'woah, my php site is working', 'points': 20},
    'DB': {'host': f'192.168.{team_number}.12', 'port': 5432, 'user': 'commentUser', 'password': 'password123', 'db': 'comments', 'points': 15},
    'DNS': {'host': f'192.168.{team_number}.15', 'points': 30}
}

# Initialize service statuses and points
service_statuses = {service: -1 for service in services}
service_points = {service: details['points'] for service, details in services.items()}

def check_services():
    total_score = 0
    potential_score = 0
    for service, details in services.items():
        if 'ip' in details:  # ICMP check
            status = icmp_check(details['ip'])
            if service_statuses[service] != status:
                service_statuses[service] = status
            total_score += calculate_score(status, details['points'])
            potential_score += details['points']
        elif 'host' in details:  # SSH, FTP, Apache, MYSQL checks
            if service == 'SSH':
                status = ssh_check(details['host'], details['users'], details['passwords'])
            elif service == 'FTP':
                status = ftp_check(details['host'], details['user'], details['password'], details['file'])
            elif service == 'WEB':
                status = apache_check(details['host'], details['port'], details['content'])
            elif service == 'DB':
                #status = mysql_check(details['host'], details['port'], details['user'], details['password'], details['db'])
                status = postgres_check(details['host'], details['port'], details['user'], details['password'], details['db'])
            elif service == "DNS":
                stauts = dns_check(details['host'])
            if service_statuses[service] != status:
                service_statuses[service] = status
            total_score += calculate_score(status, details['points'])
            potential_score += details['points']

    return total_score, potential_score

def calculate_score(status, points):
    if status == 1:
        return points
    elif status == 0:
        return points / 2
    else:
        return 0

def icmp_check(ip):
    ping_packet = IP(dst=ip) / ICMP()

    response, _ = sr(ping_packet, timeout=2, verbose=False)

    if response:
        return 1
    return -1

def ssh_check(host, users, passwords):
    # update this code to use defined password instead of private key
    working_count = 0
    total_count = 0
    try:
        total_count += 1
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        for user in users:
            private_key = os.path.expanduser(f'users/{user}/.ssh/id_rsa')
            ssh.connect(hostname=host, username=user, key_filename=private_key, timeout=5)
        ssh.close()
        working_count += 1
    except (paramiko.AuthenticationException, paramiko.SSHException, TimeoutError):
        pass

    if working_count == total_count:
        return 1
    if working_count == 0:
        return -1
    return 0

def ftp_check(host, user, password, filename):
    try:
        ftp = FTP(host, timeout=5)
        ftp.login(user=user, passwd=password)
    except:
        return -1

    try:
        remote_file = 'important_document.txt'

        if remote_file in ftp.nlst():
            buffer = BytesIO()
            ftp.retrbinary('RETR ' + remote_file, buffer.write)
            current_file_contents = buffer.getvalue().decode('utf-8')
    except Exception as e:
        return 0

    with open('important_document.txt') as fin:
        true_file_contents = fin.read()

    if true_file_contents == current_file_contents:
        return 1
    return 0

def apache_check(host, port, content):
    try:
        r = requests.get(f'http://{host}')
        if r.status_code != 200:
            return -1
        if content not in r.text:
            return 0
        return 1
    except:
        return -1

def mysql_check(host, port, user, password, db):
    try:
        conn = pymysql.connect(host=host, port=port, user=user, password=password, db=db, connect_timeout=5)
        cursor = conn.cursor()
    except:
        return -1
    try:
        cursor.execute('SELECT * from comments')
        result = cursor.fetchone()
        conn.close()
    except:
       return 0
    return 1

def postgres_check(host, port, content):
    # Same as mysql check, but through postgres
    pass

def dns_check(host):
    # nslookup using the host as the server
    '''
    where <n> is team_number
    <name>.team-<n>.openlabs.best

    192.168.<n>.11: backup
    192.168.<n>.12: db
    192.168.<n>.13: fileshare
    192.168.<n>.14: web
    192.168.<n>.15: wkst

    '''
    pass

def update_scoreboard():
    while True:
        time.sleep(10)  # Wait for 10 seconds before checking again
        total_score, potential_score = check_services()
        print(f'Total Score: {total_score} / Potential Score: {potential_score}')

def start_update_thread():
    update_thread = threading.Thread(target=update_scoreboard)
    update_thread.daemon = True
    update_thread.start()

@app.route('/')
def index():
    total_score, potential_score = check_services()
    return render_template('index.html', services=service_statuses, total_score=total_score, potential_score=potential_score)

if __name__ == '__main__':
    start_update_thread()  # Start service checking thread
    app.run(debug=True)  # Run the Flask app
