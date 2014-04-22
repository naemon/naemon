%define logmsg logger -t %{name}/rpm
%if %{defined suse_version}
%define apacheuser wwwrun
%define apachegroup www
%define apachedir apache2
%else
%define apacheuser apache
%define apachegroup apache
%define apachedir httpd
%endif

# Setup some debugging options in case we build with --with debug
%if %{defined _with_debug}
  %define mycflags -O0 -pg -ggdb3
%else
  %define mycflags %{nil}
%endif

Summary: Open Source Host, Service And Network Monitoring Program
Name: naemon
Version: 0.8.0
Release: 1%{?dist}
License: GPLv2
Group: Applications/System
URL: http://www.naemon.org/
Packager: Naemon Core Development Team <naemon-dev@monitoring-lists.org>
Vendor: Naemon Core Development Team
Source0: http://labs.consol.de/naemon/download/%{name}-%{version}.tar.gz
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}
BuildRequires: gd-devel > 1.8
BuildRequires: zlib-devel
BuildRequires: libpng-devel
BuildRequires: libjpeg-devel
BuildRequires: mysql-devel
BuildRequires: gperf
BuildRequires: perl
BuildRequires: logrotate
BuildRequires: autoconf
BuildRequires: automake
BuildRequires: libtool
BuildRequires: gcc-c++
BuildRequires: help2man
BuildRequires: rsync
BuildRequires: libicu-devel
# sles / rhel specific requirements
%if %{defined suse_version}
BuildRequires: libexpat-devel
%else
BuildRequires: expat-devel
%endif
# rhel6 specific requirements
%if 0%{?el6}
BuildRequires: perl-ExtUtils-MakeMaker
BuildRequires: perl-Module-Install
%endif
%if 0%{?el7}%{?fc20}%{?fc21}%{?fc22}
BuildRequires: perl-autodie
BuildRequires: systemd
BuildRequires: chrpath
%endif

Requires(pre): shadow-utils
Requires: %{name}-core            = %{version}-%{release}
Requires: %{name}-tools           = %{version}-%{release}
Requires: %{name}-livestatus      = %{version}-%{release}
Requires: %{name}-thruk           = %{version}-%{release}
Requires: %{name}-thruk-reporting = %{version}-%{release}
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
compatible with Nagios, and can be found in the monitoring-plugins package.

Naemon ships the Thruk gui with extended reporting and dashboard features.

# disable binary striping
%global __os_install_post %{nil}



%package core
Summary:   Naemon Monitoring Core
Group:     Applications/System
Requires:  logrotate

%description core
contains the %{name} core.


%package tools
Summary:   Naemon Monitoring Tools
Group:     Applications/System

%description tools
contains tools for %{name}.
 - naemonstats:  display statistics
 - oconfsplit:   divide configurations by groups
 - shadownaemon: shadow a remote naemon core over livestatus



%package core-dbg
Summary:   Naemon Monitoring Debug Core
Group:     Applications/System

%description core-dbg
contains the %{name} core with debug symbols.



%package livestatus
Summary:        Naemon Livestatus Eventbroker Module
Group:          Applications/System

%description livestatus
contains the %{name} livestatus eventbroker module.


%package thruk
Summary:     Thruk Gui For Naemon
Group:       Applications/System
Requires:    %{name}-thruk-libs = %{version}-%{release}
Requires(preun): %{name}-thruk-libs = %{version}-%{release}
Requires(post): %{name}-thruk-libs = %{version}-%{release}
Requires:    perl logrotate gd wget
Conflicts:   thruk
AutoReqProv: no
%if %{defined suse_version}
Requires:    apache2 apache2-mod_fcgid cron
%else
Requires:    httpd mod_fcgid
%endif

%description thruk
This package contains the thruk gui for %{name}.


%package thruk-libs
Summary:     Perl Librarys For Naemons Thruk Gui
Group:       Applications/System
AutoReqProv: no
Requires:    %{name}-thruk = %{version}-%{release}
Conflicts:   thruk

%description thruk-libs
This package contains the library files for the thruk gui.


%package thruk-reporting
Summary:     Thruk Gui For Naemon Reporting Addon
Group:       Applications/System
Requires:    %{name}-thruk = %{version}-%{release}
%if %{defined suse_version}
Requires: xorg-x11-server-extra
%else
Requires: xorg-x11-server-Xvfb libXext dejavu-fonts-common
%endif
AutoReqProv: no

%description thruk-reporting
This package contains the reporting addon for naemons thruk gui useful for sla
and event reporting.



%package devel
Summary: Development Files For Naemon
Group: Development/Libraries

%description devel
This package contains the header files, static libraries for %{name}.
If you are a NEB-module author or wish to write addons for Naemon
using Naemons own APIs, you should install this package.



%prep
%setup -q

%build
CFLAGS="%{mycflags}" LDFLAGS="$CFLAGS" %configure \
    --datadir="%{_datadir}/%{name}" \
    --libdir="%{_libdir}/%{name}" \
    --localstatedir="%{_localstatedir}/lib/%{name}" \
    --sysconfdir="%{_sysconfdir}/%{name}" \
    --enable-event-broker \
    --with-pluginsdir="%{_libdir}/%{name}/plugins" \
    --with-tempdir="%{_localstatedir}/cache/%{name}" \
    --with-checkresultdir="%{_localstatedir}/cache/%{name}/checkresults" \
    --with-logdir="%{_localstatedir}/log/%{name}" \
    --with-initdir="%{_initrddir}" \
    --with-logrotatedir="%{_sysconfdir}/logrotate.d" \
    --with-naemon-user="naemon" \
    --with-naemon-group="naemon" \
    --with-lockfile="%{_localstatedir}/run/%{name}/%{name}.pid" \
    --with-thruk-user="%{apacheuser}" \
    --with-thruk-group="naemon" \
    --with-thruk-libs="%{_libdir}/%{name}/perl5" \
    --with-thruk-tempdir="%{_localstatedir}/cache/%{name}/thruk" \
    --with-thruk-vardir="%{_localstatedir}/lib/%{name}/thruk" \
    --with-httpd-conf="%{_sysconfdir}/%{apachedir}/conf.d" \
    --with-htmlurl="/naemon"
%{__make} %{?_smp_mflags} -j 1 all

%install
%{__rm} -rf %{buildroot}
%{__make} install \
    DESTDIR="%{buildroot}" \
    INSTALL_OPTS="" \
    COMMAND_OPTS="" \
    INIT_OPTS=""
# because we globally disabled binary striping, we have to do this manually for some files
%{__cp} -p %{buildroot}%{_bindir}/%{name} %{buildroot}%{_bindir}/%{name}-dbg
%{__strip} %{buildroot}%{_bindir}/%{name}
%{__strip} %{buildroot}%{_bindir}/naemonstats
%{__strip} %{buildroot}%{_bindir}/oconfsplit
%{__strip} %{buildroot}%{_bindir}/shadownaemon
%{__strip} %{buildroot}%{_bindir}/%{name}-unixcat
%{__strip} %{buildroot}%{_libdir}/%{name}/libnaemon.so.0.0.0
%{__mv} %{buildroot}%{_sysconfdir}/logrotate.d/thruk %{buildroot}%{_sysconfdir}/logrotate.d/%{name}-thruk
%{__mv} %{buildroot}%{_sysconfdir}/logrotate.d/%{name} %{buildroot}%{_sysconfdir}/logrotate.d/%{name}-core

# Put the new RC sysconfig in place
%{__install} -d -m 0755 %{buildroot}/%{_sysconfdir}/sysconfig/
%{__install} -m 0644 %{name}-core/sample-config/%{name}.sysconfig %{buildroot}/%{_sysconfdir}/sysconfig/%{name}

%{__mkdir_p} -m 0755 %{buildroot}%{_libdir}/%{name}/
%{__ln_s} %{_libdir}/nagios/plugins %{buildroot}%{_libdir}/%{name}/plugins

%if 0%{?el7}%{?fc20}%{?fc21}%{?fc22}
# Install systemd entry
%{__install} -D -m 0644 -p %{name}-core/daemon-systemd %{buildroot}%{_unitdir}/%{name}.service
%{__install} -D -m 0644 -p %{name}-core/%{name}.tmpfiles.conf %{buildroot}%{_tmpfilesdir}/%{name}.conf
%{__install} -d -m 0755 %{buildroot}/%{_localstatedir}/run/%{name}/
# Move SystemV init-script
%{__mv} -f %{buildroot}%{_initrddir}/%{name} %{buildroot}/%{_bindir}/%{name}-ctl

# Cleanup rpath errors in perl modules
chrpath --delete %{buildroot}%{_libdir}/%{name}/perl5/%{_arch}-linux-thread-multi/auto/GD/GD.so
chrpath --delete %{buildroot}%{_libdir}/%{name}/perl5/%{_arch}-linux-thread-multi/auto/DBD/mysql/mysql.so
chrpath --delete %{buildroot}%{_libdir}/%{name}/perl5/%{_arch}-linux-thread-multi/auto/Time/HiRes/HiRes.so
chrpath --delete %{buildroot}%{_libdir}/%{name}/perl5/%{_arch}-linux-thread-multi/auto/XML/Parser/Expat/Expat.so
%endif

%clean
%{__rm} -rf %{buildroot}



%pre core
if ! /usr/bin/id naemon &>/dev/null; then
    /usr/sbin/useradd -r -d %{_localstatedir}/lib/%{name} -s /bin/sh -c "naemon" naemon || \
        %logmsg "Unexpected error adding user \"naemon\". Aborting installation."
fi
if ! /usr/bin/getent group naemon &>/dev/null; then
    /usr/sbin/groupadd naemon &>/dev/null || \
        %logmsg "Unexpected error adding group \"naemon\". Aborting installation."
fi

%post core
case "$*" in
  2)
    # Upgrading so try and restart if already running
    # For systemctl systems we need to reload the configs
    # becaues it'll complain if we just installed a new
    # init script
    %if 0%{?el7}%{?fc20}%{?fc21}%{?fc22}
      systemctl daemon-reload
      systemctl condrestart %{name}.service
    %else
      /etc/init.d/%{name} condrestart &>/dev/null || true
    %endif
  ;;
  1)
    %if 0%{?el7}%{?fc20}%{?fc21}%{?fc22}
      %systemd_post %{name}.service
    %else
      chkconfig --add %{name}
    %endif
  ;;
  *) echo case "$*" not handled in post
esac

if /usr/bin/id %{apacheuser} &>/dev/null; then
    if ! /usr/bin/id -Gn %{apacheuser} 2>/dev/null | grep -q naemon ; then
%if %{defined suse_version}
        /usr/sbin/groupmod -A %{apacheuser} naemon >/dev/null
%else
        /usr/sbin/usermod -a -G naemon %{apacheuser} >/dev/null
%endif
    fi
fi
touch /var/log/%{name}/%{name}.log
chmod 0664 /var/log/%{name}/%{name}.log
chown naemon:naemon /var/log/%{name}/%{name}.log

%preun core
case "$*" in
  1)
    # Upgrade, don't do anything
  ;;
  0)
    # Uninstall, go ahead and stop before removing
    %if 0%{?el7}%{?fc20}%{?fc21}%{?fc22}
      %systemd_preun %{name}.service
    %else
      /etc/init.d/naemon stop >/dev/null 2>&1 || :
      service %{name} stop >/dev/null 2>&1 || :
      chkconfig --del %{name} || :
    %endif
    rm -f /var/lib/naemon/status.dat
    rm -f /var/lib/naemon/naemon.qh
    rm -f /var/lib/naemon/naemon.tmp*
  ;;
  *) echo case "$*" not handled in preun
esac
exit 0

%postun core
case "$*" in
  0)
    # POSTUN
    rm -f /var/cache/%{name}/%{name}.configtest \
          /var/lib/%{name}/objects.cache \
          /var/lib/%{name}/objects.precache \
          /var/lib/%{name}/retention.dat \
          /var/log/%{name}/%{name}.log \
          /var/log/%{name}/archives \
          /var/run/%{name} \
          /var/lib/%{name}/%{name}.cmd
    %{insserv_cleanup}
    chkconfig --del %{name} >/dev/null 2>&1 || :
    systemctl try-restart %{name}.service >/dev/null 2>&1 || :
    ;;
  1)
    # POSTUPDATE
    ;;
  *) echo case "$*" not handled in postun
esac
exit 0


%post livestatus
case "$*" in
  2)
    # Upgrading so try and restart if already running
    %if 0%{?el7}%{?fc20}%{?fc21}%{?fc22}
      systemctl condrestart %{name}.service
    %else
      /etc/init.d/%{name} condrestart &>/dev/null || :
    %endif
  ;;
  1)
    # New install, enable module
    if [ -e /etc/%{name}/%{name}.cfg ]; then
      sed -i /etc/%{name}/%{name}.cfg -e 's~#\(broker_module=/usr/lib[0-9]*/%{name}/%{name}-livestatus/livestatus.so.*\)~\1~'
    fi
  ;;
  *) echo case "$*" not handled in postun
esac
exit 0

%preun livestatus
case "$*" in
  0)
    # POSTUN
    rm -f /var/log/%{name}/livestatus.log
    ;;
  1)
    # POSTUPDATE
    ;;
  *) echo case "$*" not handled in postun
esac
exit 0

%postun livestatus
case "$*" in
  0)
    # POSTUN
    if [ -e /etc/%{name}/%{name}.cfg ]; then
      sed -i /etc/%{name}/%{name}.cfg -e 's~\(broker_module=/usr/lib[0-9]*/%{name}/%{name}-livestatus/livestatus.so.*\)~#\1~'
    fi
    ;;
  1)
    # POSTUPDATE
    ;;
  *) echo case "$*" not handled in postun
esac
exit 0


%pre thruk
if ! /usr/bin/id naemon &>/dev/null; then
    /usr/sbin/useradd -r -d %{_localstatedir}/lib/%{name} -s /bin/sh -c "naemon" naemon || \
        %logmsg "Unexpected error adding user \"naemon\". Aborting installation."
fi
if ! /usr/bin/getent group naemon &>/dev/null; then
    /usr/sbin/groupadd naemon &>/dev/null || \
        %logmsg "Unexpected error adding group \"naemon\". Aborting installation."
fi


# save themes, plugins so we don't reenable them on every update
rm -rf /var/cache/%{name}/thruk_update
if [ -d /etc/%{name}/themes/themes-enabled/. ]; then
  mkdir -p /var/cache/%{name}/thruk_update/themes
  cp -rp /etc/%{name}/themes/themes-enabled/* /var/cache/%{name}/thruk_update/themes/ 2>/dev/null
fi
if [ -d /etc/%{name}/plugins/plugins-enabled/. ]; then
  mkdir -p /var/cache/%{name}/thruk_update/plugins
  cp -rp /etc/%{name}/plugins/plugins-enabled/* /var/cache/%{name}/thruk_update/plugins/ 2>/dev/null
fi
exit 0

%post thruk
chkconfig --add thruk
mkdir -p /var/lib/%{name}/thruk /var/cache/%{name}/thruk /etc/%{name}/bp /var/log/%{name} /etc/%{name}/conf.d
touch /var/log/%{name}/thruk.log
chown -R %{apacheuser}:%{apachegroup} /var/cache/%{name}/thruk /var/log/%{name}/thruk.log /etc/%{name}/plugins/plugins-enabled /etc/%{name}/thruk_local.conf /etc/%{name}/bp /var/lib/%{name}/thruk
/usr/bin/crontab -l -u %{apacheuser} 2>/dev/null | /usr/bin/crontab -u %{apacheuser} -

# add webserver user to group naemon
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

%if %{defined suse_version}
a2enmod alias
a2enmod fcgid
a2enmod auth_basic
a2enmod rewrite
/etc/init.d/apache2 try-restart
%else
service httpd condrestart
if [ "$(getenforce 2>/dev/null)" = "Enforcing" ]; then
  echo "******************************************";
  echo "Thruk will not work when SELinux is enabled";
  echo "SELinux: "$(getenforce);
  echo "******************************************";
fi
%endif
if [ -d %{_libdir}/%{name}/perl5 ]; then
  /usr/bin/thruk -a clearcache,installcron --local > /dev/null
fi

echo "Naemon/Thruk have been configured for http://$(hostname)/naemon/."
echo "The default user is 'admin' with password 'admin'. You can usually change that by 'htpasswd /etc/naemon/htpasswd admin'. And you really should change that!"
exit 0

%posttrans thruk
# restore themes and plugins
if [ -d /var/cache/%{name}/thruk_update/themes/. ]; then
  rm -f /etc/%{name}/themes/themes-enabled/*
  cp -rp /var/cache/%{name}/thruk_update/themes/* /etc/%{name}/themes/themes-enabled/ 2>/dev/null  # might fail if no themes are enabled
fi
if [ -d /var/cache/%{name}/thruk_update/plugins/. ]; then
  rm -f /etc/%{name}/plugins/plugins-enabled/*
  cp -rp /var/cache/%{name}/thruk_update/plugins/* /etc/%{name}/plugins/plugins-enabled/ 2>/dev/null  # might fail if no plugins are enabled
fi
echo "thruk plugins enabled:" $(ls /etc/%{name}/plugins/plugins-enabled/)
rm -rf /var/cache/%{name}/thruk_update

%preun thruk
if [ $1 = 0 ]; then
  # last version will be deinstalled
  if [ -d %{_libdir}/%{name}/perl5 ]; then
    /usr/bin/thruk -a uninstallcron --local
  fi
fi
/etc/init.d/thruk stop
chkconfig --del thruk >/dev/null 2>&1
rmdir /etc/%{name}/bp 2>/dev/null
rmdir /etc/%{name} 2>/dev/null
exit 0

%postun thruk
case "$*" in
  0)
    # POSTUN
    rm -rf /var/cache/%{name}/thruk \
           %{_datadir}/%{name}/root/thruk/plugins \
           /var/lib/%{name}/thruk
    # try to clean some empty folders
    rmdir /etc/%{name}/plugins/plugins-available 2>/dev/null
    rmdir /etc/%{name}/plugins/plugins-enabled 2>/dev/null
    rmdir /etc/%{name}/plugins 2>/dev/null
    rmdir /etc/%{name} 2>/dev/null
    %{insserv_cleanup}
    ;;
  1)
    # POSTUPDATE
    rm -rf /var/cache/%{name}/thruk/*
    mkdir -p /var/cache/%{name}/thruk/reports
    chown -R %{apacheuser}:%{apachegroup} /var/cache/%{name}/thruk
    ;;
  *) echo case "$*" not handled in postun
esac
exit 0


%preun thruk-libs
if [ $1 = 0 ]; then
  # last version will be deinstalled
  if [ -e /usr/bin/thruk ]; then
    /usr/bin/thruk -a uninstallcron --local
  fi
fi
exit 0

%post thruk-libs
if [ -e /usr/bin/thruk ]; then
  /usr/bin/thruk -a clearcache,installcron --local > /dev/null
fi
exit 0

%post thruk-reporting
rm -f /etc/%{name}/plugins/plugins-enabled/reports2
ln -s ../plugins-available/reports2 /etc/%{name}/plugins/plugins-enabled/reports2
/etc/init.d/thruk condrestart &>/dev/null || :
exit 0

%preun thruk-reporting
rm -f /etc/%{name}/plugins/plugins-enabled/reports2
/etc/init.d/thruk condrestart &>/dev/null || :
exit 0

%postun thruk-reporting
case "$*" in
  0)
    # POSTUN
    # try to clean some empty folders
    rmdir /etc/%{name}/plugins/plugins-available 2>/dev/null
    rmdir /etc/%{name}/plugins/plugins-enabled 2>/dev/null
    rmdir /etc/%{name}/plugins 2>/dev/null
    rmdir /etc/%{name} 2>/dev/null
    ;;
  1)
    # POSTUPDATE
    ;;
  *) echo case "$*" not handled in postun
esac
exit 0




%files

%files core
%attr(0755,root,root) %{_bindir}/%{name}
%if 0%{?el7}%{?fc20}%{?fc21}%{?fc22}
  %attr(0644,root,root) %{_unitdir}/%{name}.service
  %attr(0644,root,root) %{_tmpfilesdir}/%{name}.conf
  %attr(0755,root,root) %{_bindir}/%{name}-ctl
  %attr(0755,naemon,naemon) %dir %{_localstatedir}/run/%{name}
%else
  %attr(0755,root,root) %{_initrddir}/naemon
%endif
%config(noreplace) %{_sysconfdir}/logrotate.d/%{name}-core
%attr(0755,root,root) %dir %{_sysconfdir}/%{name}/
%attr(2775,naemon,naemon) %dir %{_sysconfdir}/%{name}/conf.d
%attr(0644,naemon,naemon) %config(noreplace) %{_sysconfdir}/%{name}/%{name}.cfg
%attr(0640,naemon,naemon) %config(noreplace) %{_sysconfdir}/%{name}/resource.cfg
%attr(0664,naemon,naemon) %config(noreplace) %{_sysconfdir}/%{name}/conf.d/*.cfg
%attr(0664,naemon,naemon) %config(noreplace) %{_sysconfdir}/%{name}/conf.d/templates/*.cfg
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/sysconfig/%{name}
%attr(2775,naemon,%{apachegroup}) %dir %{_localstatedir}/cache/%{name}/checkresults
%attr(2775,naemon,naemon) %dir %{_localstatedir}/cache/%{name}
%attr(0755,naemon,naemon) %dir %{_localstatedir}/lib/%{name}
%attr(0755,naemon,naemon) %dir %{_localstatedir}/log/%{name}
%attr(0755,naemon,naemon) %dir %{_localstatedir}/log/%{name}/archives
%attr(-,root,root) %{_libdir}/%{name}/plugins
%{_mandir}/man8/naemon.8*

%files tools
%attr(0755,root,root) %{_bindir}/naemonstats
%attr(0755,root,root) %{_bindir}/oconfsplit
%attr(0755,root,root) %{_bindir}/shadownaemon
%attr(-,root,root) %{_libdir}/%{name}/libnaemon.so*
%{_mandir}/man8/naemonstats.8*
%{_mandir}/man8/oconfsplit.8*
%{_mandir}/man8/shadownaemon.8*

%files core-dbg
%attr(0755,root,root) %{_bindir}/%{name}-dbg

%files devel
%attr(-,root,root) %{_includedir}/%{name}/
%attr(-,root,root) %{_libdir}/%{name}/libnaemon.a
%attr(-,root,root) %{_libdir}/%{name}/libnaemon.la

%files livestatus
%attr(0755,root,root) %{_bindir}/%{name}-unixcat
%attr(0755,naemon,naemon) %dir /%{name}/%{name}-livestatus
%attr(0644,root,root) %{_libdir}/%{name}/%{name}-livestatus/livestatus.so
%attr(-,root,root)    %{_libdir}/%{name}/%{name}-livestatus/livestatus.la
%attr(0755,naemon,naemon) %dir %{_localstatedir}/log/%{name}

%files thruk
%attr(0755,root, root) %{_bindir}/thruk
%attr(0755,root, root) %{_bindir}/naglint
%attr(0755,root, root) %{_bindir}/nagexp
%attr(0755,root, root) %{_initrddir}/thruk
%config %{_sysconfdir}/%{name}/ssi
%config %{_sysconfdir}/%{name}/thruk.conf
%attr(0644,%{apacheuser},%{apachegroup}) %config(noreplace) %{_sysconfdir}/%{name}/thruk_local.conf
%attr(0644,%{apacheuser},%{apachegroup}) %config(noreplace) %{_sysconfdir}/%{name}/cgi.cfg
%attr(0644,%{apacheuser},%{apachegroup}) %config(noreplace) %{_sysconfdir}/%{name}/htpasswd
%attr(0755,%{apacheuser},%{apachegroup}) %dir %{_sysconfdir}/%{name}/bp
%config(noreplace) %{_sysconfdir}/%{name}/naglint.conf
%config(noreplace) %{_sysconfdir}/%{name}/log4perl.conf
%config(noreplace) %{_sysconfdir}/logrotate.d/%{name}-thruk
%config(noreplace) %{_sysconfdir}/%{apachedir}/conf.d/thruk.conf
%config(noreplace) %{_sysconfdir}/%{apachedir}/conf.d/thruk_cookie_auth_vhost.conf
%config(noreplace) %{_sysconfdir}/%{name}/themes
%config(noreplace) %{_sysconfdir}/%{name}/menu_local.conf
%config(noreplace) %{_sysconfdir}/%{name}/usercontent
%attr(0755,root, root) %{_datadir}/%{name}/thruk_auth
%attr(0755,root, root) %{_datadir}/%{name}/script/thruk_fastcgi.pl
%attr(0755,%{apacheuser},%{apachegroup}) %dir %{_localstatedir}/cache/%{name}/thruk
%{_datadir}/%{name}/root
%{_datadir}/%{name}/templates
%{_datadir}/%{name}/themes
%{_datadir}/%{name}/plugins/plugins-available/business_process
%config %{_sysconfdir}/%{name}/plugins/plugins-enabled/business_process
%config %{_sysconfdir}/%{name}/plugins/plugins-available/business_process
%{_datadir}/%{name}/plugins/plugins-available/conf
%config %{_sysconfdir}/%{name}/plugins/plugins-enabled/conf
%config %{_sysconfdir}/%{name}/plugins/plugins-available/conf
%{_datadir}/%{name}/plugins/plugins-available/dashboard
%config %{_sysconfdir}/%{name}/plugins/plugins-available/dashboard
%{_datadir}/%{name}/plugins/plugins-available/minemap
%config %{_sysconfdir}/%{name}/plugins/plugins-enabled/minemap
%config %{_sysconfdir}/%{name}/plugins/plugins-available/minemap
%{_datadir}/%{name}/plugins/plugins-available/mobile
%config %{_sysconfdir}/%{name}/plugins/plugins-enabled/mobile
%config %{_sysconfdir}/%{name}/plugins/plugins-available/mobile
%{_datadir}/%{name}/plugins/plugins-available/panorama
%config %{_sysconfdir}/%{name}/plugins/plugins-enabled/panorama
%config %{_sysconfdir}/%{name}/plugins/plugins-available/panorama
%{_datadir}/%{name}/plugins/plugins-available/shinken_features
%config %{_sysconfdir}/%{name}/plugins/plugins-available/shinken_features
%{_datadir}/%{name}/plugins/plugins-available/statusmap
%config %{_sysconfdir}/%{name}/plugins/plugins-enabled/statusmap
%config %{_sysconfdir}/%{name}/plugins/plugins-available/statusmap
%{_datadir}/%{name}/plugins/plugins-available/wml
%config %{_sysconfdir}/%{name}/plugins/plugins-available/wml
%{_datadir}/%{name}/lib
%{_datadir}/%{name}/Changes
%{_datadir}/%{name}/LICENSE
%{_datadir}/%{name}/menu.conf
%{_datadir}/%{name}/dist.ini
%{_datadir}/%{name}/thruk_cookie_auth.include
%{_datadir}/%{name}/docs/THRUK_MANUAL.html
%{_datadir}/%{name}/docs/FAQ.html
%{_datadir}/%{name}/%{name}-version
%attr(0755,root,root) %{_datadir}/%{name}/fcgid_env.sh
%{_mandir}/man3/nagexp.3*
%{_mandir}/man3/naglint.3*
%{_mandir}/man3/thruk.3*
%{_mandir}/man8/thruk.8*

%files thruk-libs
%attr(-,root,root) %{_libdir}/%{name}/perl5

%files thruk-reporting
%{_datadir}/%{name}/plugins/plugins-available/reports2
%{_sysconfdir}/%{name}/plugins/plugins-available/reports2
%{_sysconfdir}/%{name}/plugins/plugins-enabled/reports2

%changelog
* Sun Feb 23 2014 Daniel Wittenberg <dwittenberg2008@gmail.com> 0.8.0-2
- Add native and full systemctl control on el7

* Thu Feb 06 2014 Daniel Wittenberg <dwittenberg2008@gmail.com> 0.1.0-1
- Add reload for systemctl-based setups

* Thu Feb 06 2014 Sven Nierlein <sven.nierlein@consol.de> 0.1.0-1
- moved thruks reporting addon into seperate package

* Tue Nov 26 2013 Sven Nierlein <sven.nierlein@consol.de> 0.0.1-1
- initial naemon meta package
