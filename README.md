# WEBDEV deployment automation - Fabric

## What's a Fabric?

    Fabric is a Python library and command-line tool for streamlining the use of SSH for application deployment or systems administration tasks.

## Install - python3 and modules

    1. pyton3 - brew install python3

    2. fabric3 - pip install fabric3

    3. python setup.py

## SSH key

    1. ssh-keygen -t rsa -b 2048 -m PEM

    2. ssh-copy-id id@server

    3. The script will use id_rsa key
    	- so do not need to pass a host name through command

    4. open config add these (nano ~/.ssh/config)

    	# fabric ssh
    	Host ad30
    		user xxxxxx
    		hostname 172.31.100.115
    		port 22
    		IdentityFile ~/.ssh/id_rsa
    		ServerAliveCountMax 3
    		ServerAliveInterval 180

## How to run the script

    1. Aliases
    	- br: branch name
    	- cl: linkID
    	- cm: commit

    2. NON EV1.5 sites
    	1. Upload file(s)
    		- fab dp:br=client-live,cl=fsuse
    			- if pac7 files then will sync
        2. Need to upload files (evenue) to individual server?
            - fab dp:br=client-live,cl=fsuse,ss=126
    	3. Commit
    		- add 'cm' to the command (do not put any COMMA in the commit msaage)
    		- fab dp:br=client-live,cl=fsuse,cm='commit message'
    		- will 'stash' first then push

    3. EV1.5 sites
    	- will determine either 'nc' or 'pac7' automatically
    	- fab dp:br=master
    	- will sync either 'nc' or 'pac7' as well
