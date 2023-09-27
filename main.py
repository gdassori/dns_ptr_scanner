import sys
import csv
import random
import socket
import time
import concurrent.futures
from netaddr import IPRange, IPAddress
import argparse
import os

def load_dns_servers():
    # Carica i server DNS da un file
    with open('dns_servers.txt', 'r') as f:
        servers = [line.strip() for line in f]
    return servers

def load_dns_records():
    # Carica i record DNS da un file
    with open('check_records.csv', 'r') as f:
        reader = csv.reader(f)
        next(reader)  # Skip header
        records = [(row[0], row[1]) for row in reader]
    return records

def check_dns_server(server, records):
    # Controlla se un singolo server DNS è in grado di risolvere l'IP dato
    test_ip, expected_hostname = random.choice(records)
    try:
        dns_server, hostname = get_ptr(test_ip, [server])
        if hostname == expected_hostname.rstrip('.'):
            return (True, server)
        else:
            return (False, server)
    except socket.herror:
        print(f'Warning: Unable to resolve IP for DNS server {server}.')
        return (False, server)

def check_dns_servers(servers, records):
    print(f'Checking {len(servers)} DNS servers')
    compliant_servers = []

    # Utilizziamo un ThreadPoolExecutor per parallelizzare le richieste
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
        # Mappiamo la funzione check_dns_server a tutti i server in input
        future_to_server = {executor.submit(check_dns_server, server, records): server for server in servers}
        for future in concurrent.futures.as_completed(future_to_server):
            server = future_to_server[future]
            try:
                is_compliant, server = future.result()
                if is_compliant:
                    compliant_servers.append(server)
            except Exception as exc:
                print(f'Error occurred while checking server {server}: {exc}')

    return compliant_servers

def get_ptr(ip, servers):
    # Setta il server DNS
    socket.setdefaulttimeout(0.2)
    dns_server = random.choice(servers)
    socket.gethostbyaddr(dns_server)

    try:
        # Tenta la risoluzione PTR
        record = socket.gethostbyaddr(str(ip))
        return dns_server, record[0]
    except socket.herror:
        # Se non è possibile risolvere, ritorna None
        return dns_server, None

def read_last_ip():
    # Controlla se esiste un file .last_ip_scanned e trova l'ultimo IP scannerizzato
    try:
        with open('.last_ip_scanned', 'r') as f:
            last_ip = f.read()
            return IPAddress(last_ip) + 1
    except FileNotFoundError:
        return IPAddress('1.1.1.1')

def save_last_ip(ip):
    # Salva l'ultimo IP scannerizzato in .last_ip_scanned
    with open('.last_ip_scanned', 'w') as f:
        f.write(str(ip))
    return ip

def save_record(ip, record, dns_server):
    with open('dns_records.csv', 'a', newline='') as f:
        writer = csv.writer(f)
        if f.tell() == 0:
            writer.writerow(['IP', 'Data', 'Record', 'DNS'])
        writer.writerow([str(ip), time.strftime('%Y-%m-%d %H:%M:%S'), record, dns_server])

def fetch_ip(start_ip, end_ip):
    # Restituisce un generatore che produce tutti gli IP nell'intervallo
    for ip in IPRange(start_ip, end_ip):
        yield ip

def main(start_ip, end_ip):
    while 1:
        try:
            servers = load_dns_servers()
            records = load_dns_records()
            servers = check_dns_servers(servers, records)
        
            i = 1
            for ip in fetch_ip(start_ip, end_ip):
                if not i % 1000:
                    servers = check_dns_servers(servers, records)
                i += 1
                dns_server, record = get_ptr(ip, servers)
                if record is not None:
                    save_record(ip, record, dns_server)
                start_ip = save_last_ip(ip)
        except KeyboardInterrupt:
            print('Exiting gracefully')
            sys.exit(0)
        except:
            print('Error, sleeping 1 minute')
            time.sleep(60)    

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--start', type=str, help='Start IP address', default='1.1.1.1')
    parser.add_argument('--end', type=str, help='End IP address', default='255.255.255.255')
    args = parser.parse_args()

    if args.start or args.end:
        if os.path.exists('.last_ip_scanned'):
            print("Refusing to start: Range specified and .last_ip_scanned file exists. Scan already in progress and cannot change parameters. Delete the file to start over.")
            sys.exit(1)
        start_ip = IPAddress(args.start)
        end_ip = IPAddress(args.end)
    else:
        start_ip = read_last_ip()
        end_ip = IPAddress('255.255.255.255')
        
    main(start_ip, end_ip)

