%define logmsg logger -t %{name}/rpm
%define logdir %{_localstatedir}/log/naemon
%if %{defined suse_version}
%define apacheuser wwwrun
%define apachegroup www
%define apachedir apache2
%else
%define apacheuser apache
%define apachegroup apache
%define apachedir httpd
%endif

# https://bugzilla.redhat.com/show_bug.cgi?id=894903
# sharedstatedir set to /usr/com
%if "%{_sharedstatedir}" == "/usr/com"
%define _sharedstatedir /var/lib
%endif

Summary: Open Source host, service and network monitoring program
Name: naemon
Version: 0.0.1
Release: 1%{?dist}
License: GPL
Group: Applications/System
URL: http://www.naemon.org/
Packager: Sven Nierlein <sven.nierlein@consol.de>
Vendor: Naemon Core Development Team
Source0: http://www.naemon.org/download/naemon/naemon-%{version}.tar.gz
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}
BuildRequires: gd-devel > 1.8
BuildRequires: zlib-devel
BuildRequires: libpng-devel
BuildRequires: libjpeg-devel
BuildRequires: mysql-devel
BuildRequires: doxygen
BuildRequires: gperf
BuildRequires: perl
BuildRequires: logrotate
BuildRequires: gd
BuildRequires: autoconf
BuildRequires: automake
BuildRequires: libtool
Requires(pre): shadow-utils
Requires: %{name}-core       = %{version}-%{release}
Requires: %{name}-livestatus = %{version}-%{release}
Requires: %{name}-thruk      = %{version}-%{release}
# https://fedoraproject.org/wiki/Packaging:DistTag
# http://stackoverflow.com/questions/5135502/rpmbuild-dist-not-defined-on-centos-5-5

%description
Naemon is an application, system and network monitoring application.
It can escalate problems by email, pager or any other medium. It is
also useful for incident or SLA reporting. It is originally a fork
of Nagios, but with extended functionality, stability and performance.

It is written in C and is designed as a background process,
intermittently running checks on various services that you specify.

The actual service checks are performed by separate "plugin" programs
which return the status of the checks to Naemon. The plugins are
compatible with Nagios, and can be found in the nagios-plugins package.

Naemon ships the Thruk gui with extended reporting and dashboard features.

# disable binary striping
%global __os_install_post %{nil}



%package core
Summary: %{name} core
Group: Applications/System

%description core
contains the %{name} core


%package livestatus
Summary: %{name} livestatus eventbroker module
Group: Applications/System

%description livestatus
contains the %{name} livestatus eventbroker module


%package     thruk-libs
Summary:     perl librarys for naemons thruk gui
Group:       Applications/System
AutoReqProv: no
Requires:    %{name}-thruk = %{version}-%{release}

%description thruk-libs
This package contains the library files for the thruk gui


%package     thruk
Summary:     thruk gui for %{name}
Group:       Applications/System
Requires:    %{name}-thruk-libs = %{version}-%{release}
Requires(preun): %{name}-thruk-libs = %{version}-%{release}
Requires(post): %{name}-thruk-libs = %{version}-%{release}
Requires:    perl
Conflicts:   thruk
AutoReqProv: no
%if %{defined suse_version}
Requires:    apache2 apache2-mod_fcgid cron
%else
Requires:    httpd mod_fcgid
%endif

%description thruk
This package contains the thruk gui for %{name}


#%package devel
#Summary: development files for %{name}
#Group: Development/Libraries
#Requires: %{name} = %{version}-%{release}
#
#%description devel
#This package contains the header files, static libraries and development
#documentation for %{name}. If you are a NEB-module author or wish to
#write addons for Naemon using Naemons own APIs, you should install
#this package.


%prep
%setup

%build
%configure \
    --bindir="%{_bindir}" \
    --datadir="%{_datadir}/naemon" \
    --libexecdir="%{_libdir}/naemon/plugins" \
    --libdir="%{_libdir}/naemon" \
    --localstatedir="%{_localstatedir}/naemon" \
    --sharedstatedir="%{_sharedstatedir}/naemon" \
    --with-temp-dir="/var/cache/naemon/" \
    --with-checkresult-dir="%{_localstatedir}/naemon/spool/checkresults" \
    --sysconfdir="%{_sysconfdir}/naemon" \
    --mandir="%{_mandir}" \
    --with-init-dir="%{_initrddir}" \
    --with-log-dir="%{logdir}/" \
    --with-logrotate-dir="%{_sysconfdir}/logrotate.d/" \
    --with-naemon-user="naemon" \
    --with-naemon-group="naemon" \
    --with-lockfile="%{_localstatedir}/naemon/naemon.pid" \
    --with-thruk-user="%{apacheuser}" \
    --with-thruk-group="%{apachegroup}" \
    --with-thruk-libs="%{_datadir}/naemon/perl5" \
    --with-thruk-temp-dir="/var/cache/naemon/thruk" \
    --with-thruk-var-dir="%{_sharedstatedir}/naemon/thruk" \
    --with-httpd-conf="%{_sysconfdir}/%{apachedir}/conf.d/" \
    --with-htmlurl="/naemon"
# TODO: remove -j 1
%{__make} %{?_smp_mflags} -j 1 all

%install
%{__rm} -rf %{buildroot}
%{__make} install \
    DESTDIR="%{buildroot}" \
    INSTALL_OPTS="" \
    COMMAND_OPTS="" \
    INIT_OPTS=""
mkdir -p %{buildroot}%{_localstatedir}/naemon/spool/checkresults

%clean
%{__rm} -rf %{buildroot}



%pre core
if ! /usr/bin/id naemon &>/dev/null; then
    /usr/sbin/useradd -r -d %{logdir} -s /bin/sh -c "naemon" naemon || \
        %logmsg "Unexpected error adding user \"naemon\". Aborting installation."
fi
if ! /usr/bin/getent group naemon &>/dev/null; then
    /usr/sbin/groupadd naemon &>/dev/null || \
        %logmsg "Unexpected error adding group \"naemon\". Aborting installation."
fi

%post core
/sbin/chkconfig --add naemon

if /usr/bin/id %{apacheuser} &>/dev/null; then
    if ! /usr/bin/id -Gn %{apacheuser} 2>/dev/null | grep -q naemon ; then
%if %{defined suse_version}
        /usr/sbin/groupmod -A %{apacheuser} naemon >/dev/null
%else
        /usr/sbin/usermod -a -G naemon %{apacheuser} >/dev/null
%endif
    fi
else
    %logmsg "User \"%{apacheuser}\" does not exist and is not added to group \"naemon\". Sending commands to naemon from the CGIs is not possible."
fi

%preun core
if [ $1 -eq 0 ]; then
    /sbin/service naemon stop &>/dev/null || :
    /sbin/chkconfig --del naemon
fi
exit 0

%postun core
/sbin/service naemon condrestart &>/dev/null || :



%pre thruk
# save themes, plugins and ssi so we don't reenable them on every update
rm -rf /tmp/thruk_update
if [ -d /etc/naemon/themes/themes-enabled/. ]; then
  mkdir -p /tmp/thruk_update/themes
  cp -rp /etc/naemon/themes/themes-enabled/* /tmp/thruk_update/themes/
fi
if [ -d /etc/naemon/plugins/plugins-enabled/. ]; then
  mkdir -p /tmp/thruk_update/plugins
  cp -rp /etc/naemon/plugins/plugins-enabled/* /tmp/thruk_update/plugins/
fi
if [ -d /etc/naemon/ssi/. ]; then
  mkdir -p /tmp/thruk_update/ssi
  cp -rp /etc/naemon/ssi/* /tmp/thruk_update/ssi/
fi
exit 0

%post thruk
chkconfig --add thruk
mkdir -p /var/cache/naemon/thruk/reports %{logdir} /etc/naemon/bp /var/lib/naemon/thruk
touch %{logdir}/thruk.log
chown -R %{apacheuser}:%{apachegroup} /var/cache/naemon/thruk %{logdir}/thruk.log /etc/naemon/plugins/plugins-enabled /etc/naemon/thruk_local.conf /etc/naemon/bp /var/lib/naemon/thruk
/usr/bin/crontab -l -u %{apacheuser} 2>/dev/null | /usr/bin/crontab -u %{apacheuser} -
%if %{defined suse_version}
a2enmod alias
a2enmod fcgid
a2enmod auth_basic
a2enmod rewrite
/etc/init.d/apache2 restart || /etc/init.d/apache2 start
%else
/etc/init.d/httpd restart || /etc/init.d/httpd start
if [ "$(getenforce 2>/dev/null)" = "Enforcing" ]; then
  echo "******************************************";
  echo "Thruk will not work when SELinux is enabled";
  echo "SELinux: "$(getenforce);
  echo "******************************************";
fi
%endif
/usr/bin/thruk -a clearcache,installcron --local > /dev/null
echo "Thruk has been configured for http://$(hostname)/naemon/. User and password is 'thrukadmin'."
exit 0

%posttrans thruk
# restore themes and plugins
if [ -d /tmp/thruk_update/themes/. ]; then
  rm -f /etc/naemon/themes/themes-enabled/*
  cp -rp /tmp/thruk_update/themes/* /etc/naemon/themes/themes-enabled/
fi
if [ -d /tmp/thruk_update/plugins/. ]; then
  rm -f /etc/naemon/plugins/plugins-enabled/*
  cp -rp /tmp/thruk_update/plugins/* /etc/naemon/plugins/plugins-enabled/
fi
echo "plugins enabled:" $(ls /etc/naemon/plugins/plugins-enabled/)
if [ -d /tmp/thruk_update/ssi/. ]; then
  rm -f /etc/naemon/ssi/*
  cp -rp /tmp/thruk_update/ssi/* /etc/naemon/ssi/
fi
rm -rf /tmp/thruk_update

%preun thruk
if [ $1 = 0 ]; then
    # last version will be deinstalled
    /usr/bin/thruk -a uninstallcron --local
fi
/etc/init.d/thruk stop
chkconfig --del thruk >/dev/null 2>&1
exit 0

%postun thruk
case "$*" in
  0)
    # POSTUN
    rm -rf /var/cache/naemon/thruk
    rm -rf %{_datadir}/naemon/root/thruk/plugins
    %{insserv_cleanup}
    ;;
  1)
    # POSTUPDATE
    rm -rf /var/cache/naemon/thruk/*
    mkdir -p /var/cache/naemon/thruk/reports
    chown -R %{apacheuser}:%{apachegroup} /var/cache/naemon/thruk
    ;;
  *) echo case "$*" not handled in postun
esac
exit 0




%files

%files core
%defattr(-, root, root, 0755)
%attr(755,root,root) %{_bindir}/naemon
%attr(0755,root,root) %{_initrddir}/naemon
%attr(0755,root,root) %dir %{_sysconfdir}/naemon/
%attr(0755,root,root) %dir %{_sysconfdir}/naemon/conf.d
%attr(0644,naemon,naemon) %config(noreplace) %{_sysconfdir}/naemon/naemon.cfg
%attr(0644,naemon,naemon) %config(noreplace) %{_sysconfdir}/naemon/resource.cfg
%attr(0644,naemon,naemon) %config(noreplace) %{_sysconfdir}/naemon/conf.d/*.cfg
%attr(0644,naemon,naemon) %config(noreplace) %{_sysconfdir}/naemon/conf.d/templates/*.cfg
%attr(0755,naemon,naemon) %dir %{_localstatedir}/naemon/spool/checkresults
%attr(0755,naemon,naemon) %dir %{_localstatedir}/naemon/
%attr(0755,naemon,naemon) %dir /var/cache/naemon
%attr(0755,naemon,naemon) %{logdir}

#%files devel
#%attr(0755,root,root) %{_includedir}/naemon/

%files livestatus
%{_libdir}/naemon/mk-livestatus/livestatus.o

%files thruk
%defattr(-, root, root, 0755)
%{_bindir}/thruk
%{_bindir}/naglint
%{_bindir}/nagexp
%{_initrddir}/thruk
%attr(0755,%{apacheuser},%{apachegroup}) %{_sysconfdir}/naemon/ssi
%config %{_sysconfdir}/naemon/thruk.conf
%attr(0644,%{apacheuser},%{apachegroup}) %config(noreplace) %{_sysconfdir}/naemon/thruk_local.conf
%attr(0644,%{apacheuser},%{apachegroup}) %config(noreplace) %{_sysconfdir}/naemon/cgi.cfg
%attr(0644,%{apacheuser},%{apachegroup}) %config(noreplace) %{_sysconfdir}/naemon/htpasswd
%config(noreplace) %{_sysconfdir}/naemon/naglint.conf
%config(noreplace) %{_sysconfdir}/naemon/log4perl.conf
%config(noreplace) %{_sysconfdir}/logrotate.d/thruk
%config(noreplace) %{_sysconfdir}/%{apachedir}/conf.d/thruk.conf
%config(noreplace) %{_sysconfdir}/naemon/plugins
%config(noreplace) %{_sysconfdir}/naemon/themes
%config(noreplace) %{_sysconfdir}/naemon/menu_local.conf
%{_datadir}/naemon/script/thruk_auth
%{_datadir}/naemon/script/thruk_fastcgi.pl
%{_datadir}/naemon/root
%{_datadir}/naemon/templates
%{_datadir}/naemon/themes
%{_datadir}/naemon/plugins
%{_datadir}/naemon/lib
%{_datadir}/naemon/Changes
%{_datadir}/naemon/LICENSE
%{_datadir}/naemon/menu.conf
%{_datadir}/naemon/dist.ini
%attr(0755,root,root) %{_datadir}/naemon/fcgid_env.sh
%doc %{_mandir}/man3/nagexp.3
%doc %{_mandir}/man3/naglint.3
%doc %{_mandir}/man3/thruk.3
%doc %{_mandir}/man8/thruk.8
%attr(0755,naemon,naemon) %{logdir}

%files thruk-libs
%attr(0755,root,root) %{_datadir}/naemon/perl5

%changelog
* Tue Nov 26 2013 Sven Nierlein <sven.nierlein@consol.de> 0.0.1-1
- initial naemon meta package
