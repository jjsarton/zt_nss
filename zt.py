#!/bin/python3
import requests
import json
import socket
import os
import sys
import time
import configparser
import daemon
import argparse
from daemon import pidfile

"""
Preset for some globale variable, they may be changed via
commandline argumemts
"""
conf_file='/etc/zt.conf'
pid_file='/tmp/zt.pid'

"""
This must be set according to the define within nss_zt.c
"""
sock_file='/tmp/zt.sock' 

"""
Srorage from data collected from zerotier
"""
list = []

def read_config(conf_file):
	config = configparser.ConfigParser()
	config.read_file(open(conf_file))
	token	= config.get('nss','token')
	net 	= config.get('nss','net')
	headers = {'Authorization': 'bearer '+token}
	url = 'https://my.zerotier.com/api/network/'+net+'/member'
	return url, headers


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
				
def requestHosts(url, headers, debug):
	r = requests.get(url, headers=headers)
	if debug:
		print(r.status_code)
	if r.status_code == requests.codes.ok:
		jsonObject = json.loads(r.text)
		# search for each object name and config.ipAssignments
		list.clear()
		for ob in jsonObject:
			name = ob['name']
			name = name.lower()
			ip = ob['config']['ipAssignments'][0]
			online = ob['online']
			mac =  ob['config']['address']
			elem = [name,ip, online, mac]
			list.append(elem)

def zt_server(url,headers, timeout, debug):
	requestHosts(url,headers, debug)

	if os.path.exists(sock_file):
		os.remove(sock_file)
	sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
	sock.bind(sock_file);
	os.chmod(sock_file,0o777)
	sock.listen(1)
	sock.settimeout(timeout);
	while True:
		try:
			connection, client_address = sock.accept()
			datagram = connection.recv(1024)
			if datagram:
				print(datagram)
				what, nm = datagram.decode('utf-8').split('|')
				if what  == 'N':
					ip = searchIp(list,nm)
				else:
					if debug:
						print('Look for name')
					sp = nm.split('.')
					l=len(sp);
					if sp[l-1] != 'zt':
						connection.sendall(b'')
						connection.close()
						if debug:
							print('wrong to domain')
						break
					ip = searchName(list,nm)
				if debug:
					print(ip)
				# send answer
				if ip != None:
					connection.sendall(ip.encode())
					connection.close()
				else:
					connection.sendall(b'')
					connection.close()
		except TimeoutError:
			if debug:
				print('TimeoutError')
			requestHosts(url,headers, debug)
			continue;
		except KeyboardInterrupt:
			if debug:
				print('KeyboardInterrupt')
			sock.close();
			os.remove(sock_file)
			break;
		except SystemExit:
			sock.close();
			os.remove(sock_file)
			return
		except:
			reason=str(sys.exc_info()[1])
			if debug:
				print(reason)
			if reason == 'timed out':
				requestHosts(url,headers,debug)
				continue
			else:
				return

def run(pidf,url,headers,timeout,debug):
	if debug:
		print('run()')
		dbg_file='/tmp/zt.txt'
		err_file='/tmp/zterr.txt'
	else:
		dbg_file='/dev/null'
		err_file='/dev/null'
	
	with daemon.DaemonContext(
			working_directory='/tmp',
			umask=0o002,
			pidfile=pidfile.TimeoutPIDLockFile(pidf),
			stdout= open(dbg_file, 'w+'),
			stderr= open(err_file, 'w+'),
        ) as context:
		zt_server(url,headers, timeout, debug)

if __name__ == "__main__":
	parser = argparse.ArgumentParser(description="Zerotier DNS server")
	parser.add_argument('-p', '--pid-file', default=pid_file)
	#parser.add_argument('-s', '--socket-file', default=sock_file)
	parser.add_argument('-c', '--config-file', default=conf_file)
	parser.add_argument('-t', '--timeout',type=int, default=600)
	parser.add_argument('-f', '--foreground', action='store_true')
	parser.add_argument('-d', '--debug', action='store_true')
	parser.add_argument('-v', '--version', action='store_true')
	args = parser.parse_args()
	timeout=args.timeout
	if args.version:
		print('version: 20190001')
		sys.exit(0)
	conf_file=args.config_file
	if os.path.exists(sock_file):
		print('Error: Socket file exist')
		sys.exit(1)
	url, headers = read_config(conf_file)
	if args.foreground == True:
		zt_server(url, headers,args.timeout, args.debug)
	else:
		run(args.pid_file, url, headers, args.timeout,args.debug)
		os.remove(sock_file)
