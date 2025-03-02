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

# Initialize accumulated scores
accumulated_scores = {service: 0 for service in services}
last_check_time = time.time()

def check_services():
    global last_check_time
    current_time = time.time()
    time_elapsed_minutes = (current_time - last_check_time) / 60.0
    
    potential_score = sum(details['points'] for details in services.values())
    
    # Track status changes for logging
    status_changes = []
    
    for service, details in services.items():
        if 'ip' in details:  # ICMP check
            status = icmp_check(details['ip'])
            if service_statuses[service] != status:
                status_changes.append(f"{service}: {service_statuses[service]} → {status}")
                service_statuses[service] = status
            
            # Accumulate points based on time
            points_earned = calculate_score(status, details['points'] * time_elapsed_minutes)
            accumulated_scores[service] += points_earned
            
        elif 'host' in details:  # SSH, FTP, Apache, MYSQL checks
            if service == 'SSH':
                status = ssh_check(details['host'], details['users'], details['passwords'])
            elif service == 'FTP':
                status = ftp_check(details['host'], details['user'], details['password'], details['file'])
            elif service == 'WEB':
                status = apache_check(details['host'], details['port'], details['content'])
            elif service == 'DB':
                status = postgres_check(details['host'], details['port'], details['user'], details['password'], details['db'])
            elif service == "DNS":
                status = dns_check(details['host'])
                
            if service_statuses[service] != status:
                status_changes.append(f"{service}: {service_statuses[service]} → {status}")
                service_statuses[service] = status
                
            # Accumulate points based on time
            points_earned = calculate_score(status, details['points'] * time_elapsed_minutes)
            accumulated_scores[service] += points_earned
    
    # Print status changes if any occurred
    if status_changes:
        print(f"Status changes detected: {', '.join(status_changes)}")
        
    # Calculate total accumulated score
    total_score = sum(accumulated_scores.values())
    
    # Update the last check time
    last_check_time = current_time
    
    # Print current scores
    print(f"Current scores: {accumulated_scores}")
    print(f"Total accumulated score: {total_score:.2f}")
    
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
    working_count = 0
    total_count = len(users)
    
    for i, user in enumerate(users):
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            # Set longer timeout and more robust error handling
            try:
                ssh.connect(
                    hostname=host, 
                    username=user, 
                    password=passwords[i], 
                    timeout=5,
                    allow_agent=False,
                    look_for_keys=False,
                    banner_timeout=10
                )
                # Try a simple command to verify connection
                stdin, stdout, stderr = ssh.exec_command('echo test', timeout=5)
                if stdout.channel.recv_exit_status() == 0:
                    working_count += 1
                ssh.close()
            except (paramiko.AuthenticationException, paramiko.SSHException) as e:
                print(f"SSH Error with {user}@{host}: {str(e)}")
                continue
            except (socket.error, socket.timeout, TimeoutError) as e:
                print(f"Network error with {user}@{host}: {str(e)}")
                continue
            except Exception as e:
                print(f"General exception with {user}@{host}: {str(e)}")
                continue
        except Exception as e:
            print(f"Failed to initialize SSH connection to {host}: {str(e)}")
            continue

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

def postgres_check(host, port, user, password, db):
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

def dns_check(host):
    import socket
    
    domains = [
        f"{team_number}.team-{team_number}.openlabs.best",
        f"backup.team-{team_number}.openlabs.best",
        f"db.team-{team_number}.openlabs.best",
        f"fileshare.team-{team_number}.openlabs.best",
        f"web.team-{team_number}.openlabs.best",
        f"wkst.team-{team_number}.openlabs.best"
    ]
    
    expected_ips = {
        f"{team_number}.team-{team_number}.openlabs.best": f"192.168.{team_number}.15",
        f"backup.team-{team_number}.openlabs.best": f"192.168.{team_number}.11",
        f"db.team-{team_number}.openlabs.best": f"192.168.{team_number}.12",
        f"fileshare.team-{team_number}.openlabs.best": f"192.168.{team_number}.13",
        f"web.team-{team_number}.openlabs.best": f"192.168.{team_number}.14",
        f"wkst.team-{team_number}.openlabs.best": f"192.168.{team_number}.15"
    }
    
    working_count = 0
    total_count = len(domains)
    
    for domain in domains:
        try:
            socket.gethostbyname_ex(domain)
            resolved_ip = socket.gethostbyname(domain)
            if resolved_ip == expected_ips[domain]:
                working_count += 1
        except:
            pass
    
    if working_count == total_count:
        return 1
    if working_count == 0:
        return -1
    return 0

def update_scoreboard():
    while True:
        # Wait for 10 seconds before checking again
        time.sleep(10)
        try:
            total_score, potential_score = check_services()
            print(f'Total Score: {total_score:.2f} / Potential Score: {potential_score}')
        except Exception as e:
            print(f"Error in scoreboard update: {e}")

def start_update_thread():
    update_thread = threading.Thread(target=update_scoreboard)
    update_thread.daemon = True
    update_thread.start()

@app.route('/')
def index():
    total_score, potential_score = check_services()
    return render_template('index.html', services=service_statuses, total_score=total_score, potential_score=potential_score, time=time.strftime('%H:%M:%S'))

@app.route('/api/score')
def get_score_api():
    """API endpoint for getting score data via AJAX"""
    from flask import jsonify
    total_score, potential_score = check_services()
    return jsonify({
        'services': {k: v for k, v in service_statuses.items()},
        'total_score': total_score,
        'potential_score': potential_score
    })

if __name__ == '__main__':
    # Run initial service check
    check_services()
    # Start service checking thread
    start_update_thread()
    # Run the Flask app
    app.run(debug=True, host='0.0.0.0')