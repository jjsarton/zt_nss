# NSS_ZT

Nss_zt allow you to enter the name of an zerotier node name instead of
the IPv4 address. You may also retrieve the host name for a given IPv4 address.

Subdomains are supported. If you ask for example ``www.alice.zt`` you will always return the IPv4 Address of ```alice.zt```.

This will work for UNIX like systems which use nsswtich. See man
nsswitch.conf

## Components

There are two components. The library libnss_zt.so.2 which must be compiled
and be used by nsswitch and a little server (zt.py) which collect the
data from my.zerotier.com and return the IpV4 addresses for the queried
system if it is online and of course exists.

## Installation

You have to compile the library, simply enter the src directory and
issue as root: ```make install``` 


Within the line which will look like

```
hosts:      files mdns4_minimal [NOTFOUND=return] dns myhostname
```
add the word **zt** as follow:

```
hosts:      files zt mdns4_minimal [NOTFOUND=return] dns myhostname
```

### Configuration File /etc/zt.conf

This file must be created and contain some important data requiered by the server

```
[nss]
	token	= <API Access Tokens>
	net		= <Network ID>
```

Timeout is for refreshing of the internal database of the server zt.py and ist the amount of seconds betwenn 2 queries.
Without the token and the network IS you will not be able to
get informations about the systems included in your zerotier
network.

### Zerotier System Naming
In order to work properly the name of the systems within the 
zerotier network must end with '.zt', For example 'alice.zt' or 'bob.zt'.

This allow you to connect to 'alice' or 'bob' according to there official network name within your private regular network.

## Launching the daemon
The daemon zt.py will be started by simply calling zt.py.
It detach it from the terminal. You may also pass parameters

```
usage: zt.py [-h] [-p PID_FILE] [-c CONFIG_FILE] [-t TIMEOUT] [-f] [-d] [-v]

Zerotier DNS server

optional arguments:
  -h, --help            show this help message and exit
  -p PID_FILE, --pid-file PID_FILE
  -c CONFIG_FILE, --config-file CONFIG_FILE
  -t TIMEOUT, --timeout TIMEOUT
  -f, --foreground
  -d, --debug
  -v, --version

```
The default value for the config file is '/etc/zt.conf'.

The default timeout (the list of node will be refreshed if an timeout occur) is set to 600 (5 Minutes).

The name of the pid file is '/tmp/zt.pid' and can be modified.

Debuging (-d) is performed into the file '/tmp/zt.txt' and **/tmp/zterr.txt if not launched in foreground.

If you enter the option -v you will get the version number
(really the date as YYYYMMDD) and zt.py will exit.

## Stopping the daemon

If running in forground you may press '[Ctrl]+[c]' or issue the command ```pkill zt.py```

## Communication between server and library file

The communication occur via a UNIX socket. The file name is '/tmp/zt.sock'
if the socket is not present or the server is not running, the library file will return ```NSS_STATUS_NOTFOUND``` to the resolver and the next resolver module will be processed.

## Bug

There is probably a bug (within python 3) which may produce a segment violation while calling ```dnf install <package>```.

## Todo

* Process IPv6 (at this time no address is passed from the data send by my.zerotier.com)
* Better documentation
* Provide systemd files.



