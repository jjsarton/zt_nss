#!/usr/bin/python3
import socket, sys, argparse, os, daemon, select
from daemon import pidfile

sock_file='/var/run/zt.sock' 

def relay(query, server, port):
	sock=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	try:
		sock.connect((server,port));
	except:
		return b''
	sock.sendall(query)
	data=sock.recv(1000)
	#sock.sendall(b'')
	sock.shutdown(socket.SHUT_RDWR)
	sock.close()
	return data

def processMessage(sock,server,port,debug):
	s, c = sock.accept()
	query = s.recv(1024)
	response=relay(query,server,port)
	print('response',response)
	s.sendall(response)
	s.shutdown(socket.SHUT_RDWR)
	s.close()

def zt_server(server, port, debug):
	if os.path.exists(sock_file):
		os.remove(sock_file)
	sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
	sock.bind(sock_file);
	os.chmod(sock_file,0o777)
	sock.listen(1)
	sock.setblocking(0)
	sockets = [sock]
	while True:
		try:
			r,w,e = select.select(sockets,[],[],50000)
			for s in r:
				processMessage(s,server,port,debug)
			continue;
		except KeyboardInterrupt:
			if debug:
				print('KeyboardInterrupt')
			sock.close()
			if os.path.exists(sock_file):
				os.remove(sock_file)
			break;
		except SystemExit:
			sock.close();
			if os.path.exists(sock_file):
				os.remove(sock_file)
			return
		except:
			reason=str(sys.exc_info()[1])
			if debug:
				print(reason)
			if reason == 'timed out':
				continue
			else:
				return

def run(pidf,bind,port,debug):
	if debug:
		print('run()')
		dbg_file='/tmp/ztr.txt'
		err_file='/tmp/ztrerr.txt'
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
		zt_server(bind, port, debug)

if __name__ == "__main__":
	parser = argparse.ArgumentParser(description="Zerotier DNS Client")
	parser.add_argument('-p', '--pid-file', default='/tmp/ztr.pid')
	parser.add_argument('-f', '--foreground', action='store_true')
	parser.add_argument('-d', '--debug', action='store_true')
	parser.add_argument('-v', '--version', action='store_true')
	parser.add_argument('-b', '--bind', default=None)
	parser.add_argument('-P', '--port',type=int, default=9999)
	args = parser.parse_args()
	if args.version:
		print('version: 20190003')
		sys.exit(0)
	if args.bind == None:
		print('Bind Address not provided')
		sys.exit(1)
	if os.path.exists(sock_file):
		print('Error: Socket file exist')
		sys.exit(1)
	if args.foreground == True:
		zt_server(args.bind, args.port, args.debug)
	else:
		run(args.pid_file, args.bind, args.port,args.debug)
		if os.path.exists(sock_file):
			os.remove(sock_file)
		sys.exit(0)
