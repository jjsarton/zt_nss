#!/bin/python3
import requests
import json
import socket
import os
import sys
import time
import configparser
import daemon

config = configparser.ConfigParser()
config.read_file(open('/etc/zt.conf'))
token	= config.get('nss','token')
net 	= config.get('nss','net')
timeout	= int(config.get('nss','timeout'))
#bindIp 	= config.get('nss','bindIp')
#ipv6Pre	= config.get('nss','ipv6Pre')
#pidfile='/tmp/zt.pid'

list = []

def searchName(list, name):
	str = name.split('.')
	num=len(str)
	if num > 1 :
		nm = str[num-2]+'.'+str[num-1]
		for sys in list:
			#if sys[0] == nm:
			if sys[0] == nm and sys[2]:
				return sys[1]

def searchIp(list, ip):
	for sys in list:
		if sys[1] == ip:
				return sys[0]

headers = {'Authorization': 'bearer '+token}
url = 'https://my.zerotier.com/api/network/'+net+'/member'

def requestHosts():
	r = requests.get(url, headers=headers)
	if r.status_code == requests.codes.ok:
		jsonObject = json.loads(r.text)
		# search for each object name and config.ipAssignments
		#list = []
		for ob in jsonObject:
			name = ob['name']
			name = name.lower()
			ip = ob['config']['ipAssignments'][0]
			online = ob['online']
			mac =  ob['config']['address']
			elem = [name,ip, online, mac]
			list.append(elem)

def zt_server():
	requestHosts()

	if os.path.exists("/tmp/zt_sock"):
		os.remove("/tmp/zt_sock")
	socket.setdefaulttimeout(timeout)
	sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
	sock.bind("/tmp/zt_sock");
	os.chmod("/tmp/zt_sock",0o777)
	sock.listen(1)

	while True:
		try:
			connection, client_address = sock.accept()
		except TimeoutError:
			requestHosts()
			continue;
		except KeyboardInterrupt:
			sock.close();
			os.remove("/tmp/zt_sock")
			break;
		except:
			continue;
		try:
			while True:
				datagram = connection.recv(1024)
				if datagram:
					nm = datagram.decode('utf-8')
					print(nm)
					sp = nm.split('.')
					l=len(sp);
					if sp[l-1] != 'zt':
						connection.sendall(b'')
						connection.close()
						break
					ip = searchName(list,nm)
					print(ip)
					# send answer
					if ip != None:
						connection.sendall(ip.encode())
						connection.close()
						break
					else:
						connection.sendall(b'')
						connection.close()
						break
		except KeyboardInterrupt:
			break
		except TimeoutError:
			requestHosts()
			continue;

def run():
	print('run()')
	with daemon.DaemonContext():
		zt_server()

if __name__ == "__main__":
	run()

print("Ende?")
