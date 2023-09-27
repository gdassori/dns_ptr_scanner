# dns_ptr_scanner
DNS Resolvers - PTR Records Scanner

### What this software does

This software dumps, using a pool of DNS servers, the PTR records from the root-servers: the domain names resolution system white pages.

Why PTR records? Because IPv4 PTR records can be easily enumerated, as their space is limited to 4 billion of records or so. 

Takes months to complete a full internet scan, I voluntarily decided to avoid parallelization.

Basic help:
```
~/dns_ptr_scanner$ venv/bin/python main.py  --help
usage: main.py [-h] [--start START] [--end END]

options:
  -h, --help     show this help message and exit
  --start START  Start IP address
  --end END      End IP address
```
First run:

```
~/dns_ptr_scanner$ venv/bin/python main.py
Checking 24 DNS servers
```
What to expect after the first run:

```
~/dns_ptr_scanner$ ls -lnsa
total 100
 4 drwxrwxr-x  3 1000 1000  4096 Sep 22 13:21 .
 4 drwxr-x--- 14 1000 1000  4096 Sep 22 13:36 ..
 4 -rw-rw-r--  1 1000 1000    11 Sep 22 13:59 .last_ip_scanned
20 -rw-rw-r--  1 1000 1000 20234 Sep 22 13:20 check_records.csv
52 -rw-rw-r--  1 1000 1000 47886 Sep 22 13:58 dns_records.csv
 4 -rw-rw-r--  1 1000 1000   283 Sep 22 12:34 dns_servers.txt
 4 -rw-rw-r--  1 1000 1000  3860 Sep 22 13:17 main.py
 4 -rw-rw-r--  1 1000 1000    21 Sep 22 11:48 requirements.txt
 4 drwxrwxr-x  4 1000 1000  4096 Sep 22 11:43 venv
~/scan_dns$ 
```
If you use a range option (--start \ --end) again after the first run:

```
~/scan_dns$ venv/bin/python main.py --end=2.2.2.2
Refusing to start: Range specified and .last_ip_scanned file exists. 
Scan already in progress and cannot change parameters. Delete the file to start over.
```

#### filez

- .last_ip_scanned to keep the app state (delete it to start over, and you should clear dns_records.csv too but this is not checked as the file is appended)
- dns_records.csv is the output file. CSV format: IP, Date, Host, DNS (which DNS has been used to fetch the response)
- as you can see, a 'venv' has also been created. I use a virtual environment to keep the stuff clean.


#### about dns_servers.txt

A list on generic public DNS servers from the Internet, I think the 2nd or 3rd google result on the "public dns servers" search. Maybe DYOR to extend the file. 
It's ok to get a couple of warnings if DNS servers are not reachable anymore. 
As long as 1 server from the list is valid, the scan will start.


#### about check_records.csv
To ensure DNS servers are still responding across the scan, queries with known expected records are performed once a while. 
DNS servers that fails to responde these queries are banned.

Warning:
This list not going to be mantained so at some point the check_records.csv file could be broken (however, these are records from generic Google servers so I expect a bit of stability on them).
It can be regenerated by a script like the following:

```

#!/bin/bash

echo "IP,Host" > check_records.csv
for i in {212..215}; do
    for j in {1..255}; do
        IP="142.251.$i.$j"
        HOST_RESULT=$(host $IP)

        if [[ $HOST_RESULT != *"not found"* ]]; then
            HOST_NAME=$(echo $HOST_RESULT | awk '{print $5}')
            echo "$IP,$HOST_NAME" >> check_records.csv
        fi
    done
done

```

#### why 

to take a photo of the internet.
