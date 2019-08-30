# NSS_ZT

Nss_zt allow you to enter the name of an zerotier node name instead of
the IPv4 adsress.

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
	timeout = 600
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
It detach it from the terminal.

## Stopping the daemon
At this time you must issue:

```
ps -elf | grep zt.py
```
and then killing it with

```
kill -9 <pid>
```

The following command will to the job of stopping the daemon:

```
ps -ef|grep zt.py|grep python|awk '{if($2!=""){system("kill -9 "$2)}}'
```

## Communication between server and library file

The communication occur via a UNIX socket. The file name is '/tmp/zt.sock'
if the socket is not present or the server is not running, the library file will return ```NSS_STATUS_NOTFOUND``` to the resolver and the next resolver module will be processed.

## Bug

There is probably a bug (within python 3) which may produce a segment violation while calling ```dnf install <package>```.

## Todo

* Process IPv6 (at this time no address is passed from the data send by my.zerotier.com)
* Improve zt.py regarding daemon properties
* Better documentation
* Provide systemd files.



