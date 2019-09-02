# ZT_NSS

Nss_zt allow you to enter the name of an zerotier node name instead of
the IPv4 address. You may also retrieve the host name for a given IPv4 address.

Sub-domains are supported. If you ask for example ``www.alice.zt`` you will always return the IPv4 Address of ```alice.zt```.

This will work for UNIX like systems which use nsswtich. See man
nsswitch.conf

## Components

There are two components. The library libnss_zt.so.2 which must be compiled
and be used by nsswitch and a little server (zt.py) which collect the
data from my.zerotier.com and return the IpV4 addresses for the queried
system if it is online and of course exists.

There is an other server (*ztr.py*) which will contact the *zt.py* server via TCP. This allows to have only one central server collecting the data from the my.zerotier.com server.

## Installation

You have to compile the library, simply enter the zt_nss directory and
issue as root: ```make install```


For both server you have to edit the file */etc/nsswitch.conf*

Within the line which will look like

```
hosts:      files mdns4_minimal [NOTFOUND=return] dns myhostname
```
add the word **zt** as follow:

```
hosts:      files zt mdns4_minimal [NOTFOUND=return] dns myhostname
```

### Configuration File /etc/zt.conf

This file must be created and contain some important data required by the **zt.py** server

```
[nss]
	token	= <API Access Tokens>
	net		= <Network ID>
```

For **ztr.py** a configuration file is not necessary.


### Zerotier System Naming
In order to work properly the name of the systems within the 
zerotier network must end with '.zt', For example 'alice.zt' or 'bob.zt'.

This allow you to connect to 'alice' or 'bob' according to there official network name within your private regular network.

## Launching the daemon
The daemon zt.py will be started by simply calling zt.py.
It detach it from the terminal. You may also pass parameters

* zt.py


```

usage: zt.py [-h] [-p PID_FILE] [-c CONFIG_FILE] [-t TIMEOUT] [-f] [-d]
             [-b BIND] [-P PORT] [-v]

Zerotier DNS server

optional arguments:
  -h, --help            show this help message and exit
  -p PID_FILE, --pid-file PID_FILE
  -c CONFIG_FILE, --config-file CONFIG_FILE
  -t TIMEOUT, --timeout TIMEOUT
  -f, --foreground
  -d, --debug
  -b BIND, --bind BIND
  -P PORT, --port PORT
  -v, --version

```
* ztr.py

```
usage: ztr.py [-h] [-p PID_FILE] [-f] [-d] [-v] [-b BIND] [-P PORT]

Zerotier DNS Client

optional arguments:
  -h, --help            show this help message and exit
  -p PID_FILE, --pid-file PID_FILE
  -f, --foreground
  -d, --debug
  -v, --version
  -b BIND, --bind BIND
  -P PORT, --port PORT

```

The default value for the config file is '/etc/zt.conf'.

The default timeout (the list of node will be refreshed if an timeout occur) is set to 600 (5 Minutes).

The name of the pid file is '/tmp/zt.pid' and can be modified.

Debugging (-d) is performed into the file '/tmp/zt.txt' and **/tmp/zterr.txt if not launched in foreground.

If you enter the option -v you will get the version number
(really the date as YYYYMMDD) and zt.py will exit.

The parameter -b and -P are for setting the TCP connection between the main server **zt.py** and the slave **ztr.py**.
The default port is 9999. The bind address must be set to the IPv4 Address of the ZT interface from the main server.

## Stopping the daemon

If running in foreground you may press '[Ctrl]+[c]' or issue the command ```pkill zt.py``` or ```pkill ztr.py```

## Systemd Units

The file **ztr.services** and **zt.service** will be installed under
```/etc/systemd/system```.

You must provide a file ```/etc/zt/``` whith at last the line

```
OPT=""
```
The OPT variable shall contain the command line parameters for starting the daemon via systemd eg:

```
OPT="-b 10.1.2.3 -p 5678"
```

After editing the file according to your requirements you can call ```systemctl reload-daemon``` and then enable and start the wanted service eg:

```
systemctl enable ztr.services
systemctl start ztr.services
```

## Communication between server and library file

The communication occur via a UNIX socket. The file name is '/tmp/zt.sock'
if the socket is not present or the server is not running, the library file will return ```NSS_STATUS_NOTFOUND``` to the resolver and the next resolver module will be processed.

## Requirement
* python 3
* python-daemon module (may not be installed)

The main Server may be installed on a low cost device as the Raspberry PI.  
I have installed it on a Raspberry PI 3, this worked out of the box after launching the **zt.py** server on it. The other Linux devices what run with **ztr.py**.

## Bug

There is probably a bug (within python 3) which may produce a segment violation while calling ```dnf install python3-daemon``` (fedora) or ```apt install python3-daemon``` (Debian, Ubuntu, Mint) . For other distributions refer to the respective documents

## Todo

* Process IPv6 (at this time no address is passed from the data send by my.zerotier.com)
* Better documentation




