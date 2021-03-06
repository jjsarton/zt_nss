CC=gcc
CFLAGS=-O2 -g

OBJ=nss_zt.o

%.o: %.c
	@$(CC) -Wall -fPIC -c -o $@ $< $(CFLAGS)

all: libnss_zt.so.2

libnss_zt.so.2: $(OBJ)
	@$(CC) -shared -o $@ $^ -Wl,-soname,libnss_zt.so.2 $(CFLAGS)

clean:
	@rm -f *.o *~ libnss_zt.so.2

install: libnss_zt.so.2
	@if [ -d /usr/lib64 ]; then \
		cp $(CURDIR)/libnss_zt.so.2 /usr/lib64;\
	else \
		cp $(CURDIR)/libnss_zt.so.2 /usr/lib;\
	fi
	@cp zt.py /usr/bin/; chmod a+x /usr/bin/zt.py
	@cp ztr.py /usr/bin/; chmod a+x /usr/bin/ztr.py
	@cp zt.service  ztr.service /etc/systemd/system/
	@if [ ! -d /etc/zt_nss ]; then mkdir /etc/zt_nss;fi
	@cp zt /etc/zt_nss/

uninstall:
	-@systemctl stop zt.service
	-@systemctl stop ztr.service
	-@systemctl disable zt.service
	-@systemctl disable ztr.service
	-@systemctl daemon-reload
	@if [ -d /usr/lib64 ]; then \
		rm /usr/lib64/libnss_zt.so.2; \
	else \
		rm /usr/lib/libnss_zt.so.2; \
	fi
	@rm /usr/bin/zt*.py
	@rm /etc/systemd/system/zt.service
	@rm /etc/systemd/system/ztr.service
	@rm -fr /etc/zt_nss;

