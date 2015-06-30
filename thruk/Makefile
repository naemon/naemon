HTTPDCONF=$(shell if [ -d "/etc/apache2/conf-available" ]; then echo "/etc/apache2/conf-available"; elif [ -d "/etc/httpd/conf.d" ]; then echo "/etc/httpd/conf.d"; elif [ -d "/etc/httpd/conf-available" ]; then echo "/etc/httpd/conf-available"; else echo "/etc/apache2/conf.d"; fi )

all:

install:
	mkdir -p $(DESTDIR)$(HTTPDCONF)/
	install -m 0644 apache2.conf $(DESTDIR)$(HTTPDCONF)/naemon.conf
	mkdir -p $(DESTDIR)/usr/share/naemon
	install -m 0644 apache2.include $(DESTDIR)/usr/share/naemon/naemon-thruk.include
	mkdir -p $(DESTDIR)/etc/thruk/thruk_local.d/
	install -m 0644 naemon.conf $(DESTDIR)/etc/thruk/thruk_local.d/naemon.conf

clean:
