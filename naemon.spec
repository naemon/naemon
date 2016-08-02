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

%if 0%{?el7}%{?fc20}%{?fc21}%{?fc22}
%global use_systemd 1
%endif
%if 0%{?suse_version} >= 1315
%global use_systemd 1
%endif

# Setup some debugging options in case we build with --with debug
%if %{defined _with_debug}
  %define mycflags -O0 -pg -ggdb3
%else
  %define mycflags %{nil}
%endif

%if ! ( 0%{?rhel} > 5 )
%{!?python_sitelib: %global python_sitelib %(/usr/bin/python26 -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())")}
%else
%{!?python_sitelib: %global python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())")}
%endif

Summary: Open Source Host, Service And Network Monitoring Program
Name: naemon
Version: 1.0.5
Release: 1%{?dist}
License: GPLv2
Group: Applications/System
URL: http://www.naemon.org/
Packager: Naemon Core Development Team <naemon-dev@monitoring-lists.org>
Vendor: Naemon Core Development Team
Source0: http://labs.consol.de/naemon/download/%{name}-%{version}.tar.gz
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}
BuildRequires: gperf
BuildRequires: logrotate
BuildRequires: autoconf
BuildRequires: automake
BuildRequires: libtool
BuildRequires: gcc-c++
BuildRequires: help2man
BuildRequires: libicu-devel
BuildRequires: pkgconfig
BuildRequires: glib2-devel
# sles / rhel specific requirements
%if 0%{?el7}%{?fc20}%{?fc21}%{?fc22}%{?fc23}
BuildRequires: chrpath
%endif
%if 0%{?use_systemd}
BuildRequires: systemd
%endif

%if %{defined suse_version}
%if 0%{suse_version} < 1230
Requires(pre): pwdutils
%else
Requires(pre): shadow
%endif
%if 0%{?suse_version} < 1315
Requires(pre): shadow-utils
%endif
%endif
Requires: %{name}-core            = %{version}-%{release}
Requires: %{name}-tools           = %{version}-%{release}
Requires: %{name}-livestatus      = %{version}-%{release}
Requires: %{name}-thruk           = %{version}-%{release}
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
Requires:  libnaemon = %{version}-%{release}

%description tools
contains tools for %{name}.
 - naemonstats:  display statistics
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
Requires:    thruk
Requires(pre): naemon-core = %{version}-%{release}
Obsoletes: naemon-thruk-reporting
Obsoletes: naemon-thruk-libs

%description thruk
This package contains the thruk gui for %{name}.


%package devel
Summary: Development Files For Naemon
Group: Development/Libraries
Requires: libnaemon = %version
Requires: glib2-devel

%description devel
This package contains the header files, static libraries for %{name}.
If you are a NEB-module author or wish to write addons for Naemon
using Naemons own APIs, you should install this package.


%package -n libnaemon
Summary: Shared Library for Naemon and NEB modules
Group: Development/Libraries

%description -n libnaemon
libnaemon contains the shared library for building NEB modules or addons for
Naemon.



%prep
%setup -q

%build
CFLAGS="%{mycflags}" LDFLAGS="$CFLAGS" %configure \
    --datadir="%{_datadir}/%{name}" \
    --libdir="%{_libdir}/%{name}" \
    --localstatedir="%{_localstatedir}/lib/%{name}" \
    --sysconfdir="%{_sysconfdir}/%{name}" \
    --with-naemon-config-dir="%{_sysconfdir}/%{name}/module-conf.d" \
    --with-pkgconfdir="%{_sysconfdir}/%{name}" \
    --enable-event-broker \
    --with-pluginsdir="%{_libdir}/%{name}/plugins" \
    --with-tempdir="%{_localstatedir}/cache/%{name}" \
    --with-logdir="%{_localstatedir}/log/%{name}" \
    --with-initdir="%{_initrddir}" \
    --with-logrotatedir="%{_sysconfdir}/logrotate.d" \
    --with-naemon-user="naemon" \
    --with-naemon-group="naemon" \
    --with-lockfile="%{_localstatedir}/run/%{name}/%{name}.pid"
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
%{__strip} %{buildroot}%{_bindir}/shadownaemon
%{__strip} %{buildroot}%{_bindir}/unixcat
%{__strip} %{buildroot}%{_libdir}/%{name}/libnaemon.so.0.0.0
%{__strip} %{buildroot}%{_libdir}/%{name}/%{name}-livestatus/livestatus.so
%{__mv} %{buildroot}%{_sysconfdir}/logrotate.d/%{name} %{buildroot}%{_sysconfdir}/logrotate.d/%{name}-core
%{__mv} %{buildroot}%{_libdir}/%{name}/pkgconfig %{buildroot}%{_libdir}/pkgconfig
%{__mkdir_p} -m 0755 %{buildroot}%{_datadir}/%{name}/examples
%{__mv} %{buildroot}%{_sysconfdir}/%{name}/conf.d %{buildroot}%{_datadir}/%{name}/examples/
%{__mkdir_p} -m 0755 %{buildroot}%{_sysconfdir}/%{name}/conf.d
%{__mkdir_p} -m 0755 %{buildroot}%{_localstatedir}/lib/%{name}
%{__mkdir_p} -m 2775 %{buildroot}%{_localstatedir}/lib/%{name}/spool/checkresults
%{__mkdir_p} -m 0755 %{buildroot}%{_localstatedir}/cache/%{name}

# Put the new RC sysconfig in place
%{__install} -d -m 0755 %{buildroot}/%{_sysconfdir}/sysconfig/
%{__install} -m 0644 %{name}-core/sample-config/%{name}.sysconfig %{buildroot}/%{_sysconfdir}/sysconfig/%{name}

# Make sure the default run directory exists
mkdir -p -m 0755 %{buildroot}%{_localstatedir}/run/%{name}

%{__mkdir_p} -m 0755 %{buildroot}%{_libdir}/%{name}/
%{__ln_s} %{_libdir}/nagios/plugins %{buildroot}%{_libdir}/%{name}/plugins

# We don't really want to distribute this
rm -f %{buildroot}%{_libdir}/%{name}/%{name}-livestatus/livestatus.la

# Livestatus Python API
install -d %buildroot%{python_sitelib}/livestatus
install -pm 0644 api/python/livestatus.py %buildroot%{python_sitelib}/livestatus/
install -pm 0644 api/python/__init__.py %buildroot%{python_sitelib}/livestatus/

%if 0%{?use_systemd}
# Install systemd entry
%{__install} -D -m 0644 -p %{name}-core/daemon-systemd %{buildroot}%{_unitdir}/%{name}.service
%{__install} -D -m 0644 -p %{name}-core/%{name}.tmpfiles.conf %{buildroot}%{_tmpfilesdir}/%{name}.conf
%{__install} -d -m 0755 %{buildroot}/%{_localstatedir}/run/%{name}/
# Move SystemV init-script
%{__mv} -f %{buildroot}%{_initrddir}/%{name} %{buildroot}/%{_bindir}/%{name}-ctl
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
    %if 0%{?use_systemd}
      systemctl daemon-reload
      systemctl condrestart %{name}.service
    %else
      /etc/init.d/%{name} condrestart &>/dev/null || true
    %endif
  ;;
  1)
    # install example conf.d only once on the first installation
    if [ ! -d %{_sysconfdir}/%{name}/conf.d/templates ]; then
        mkdir -p %{_sysconfdir}/%{name}/conf.d/
        cp -rp %{_datadir}/%{name}/examples/conf.d/* %{_sysconfdir}/%{name}/conf.d/
    fi
    chown naemon:naemon \
        /etc/naemon/conf.d \
        /etc/naemon/conf.d/*.cfg \
        /etc/naemon/conf.d/templates \
        /etc/naemon/conf.d/templates/*.cfg
    chown naemon:naemon \
        /etc/naemon/module-conf.d/*.cfg 2>/dev/null
    chmod 0664 /etc/naemon/conf.d/*.cfg /etc/naemon/conf.d/templates/*.cfg
    chmod 2775 /etc/naemon/conf.d /etc/naemon/conf.d/templates
    %if 0%{?use_systemd}
      %systemd_post %{name}.service
    %else
      chkconfig --add %{name}
    %endif
  ;;
  *) echo case "$*" not handled in post
esac

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
    %if 0%{?use_systemd}
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
          /var/lib/%{name}/%{name}.cmd
    rm -rf /var/run/%{name}
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
    if [ -e /etc/%{name}/%{name}.cfg ]; then
      # livestatus configuration has been moved to single drop dir file
      sed -i /etc/%{name}/%{name}.cfg -e 's~^\s*\(broker_module=/usr/lib[0-9]*/%{name}/%{name}-livestatus/livestatus.so.*\)~#\1~'
    fi
  ;;
  1)
    # First installation, no acton required
    :
  ;;
  *) echo case "$*" not handled in postun
esac
%if 0%{?use_systemd}
  systemctl condrestart %{name}.service
%else
  /etc/init.d/%{name} condrestart &>/dev/null || :
%endif
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
      sed -i /etc/%{name}/%{name}.cfg -e 's~^\s*\(broker_module=/usr/lib[0-9]*/%{name}/%{name}-livestatus/livestatus.so.*\)~#\1~'
    fi
    rm -f /var/cache/%{name}/live
    ;;
  1)
    # POSTUPDATE
    ;;
  *) echo case "$*" not handled in postun
esac
exit 0


%post thruk
# migrate config files to new location
mkdir -p -m 0755 /etc/thruk/
[ ! -e %{_sysconfdir}/%{name}/cgi.cfg ]          || %{__mv} %{_sysconfdir}/%{name}/cgi.cfg          /etc/thruk/cgi.cfg
[ ! -e %{_sysconfdir}/%{name}/thruk_local.conf ] || %{__mv} %{_sysconfdir}/%{name}/thruk_local.conf /etc/thruk/thruk_local.d/_migrated_naemon_thruk_local.conf
[ ! -e %{_sysconfdir}/%{name}/menu_local.conf ]  || sed -e 's%/usr/share/naemon/%/usr/share/thruk/%g' -i %{_sysconfdir}/%{name}/menu_local.conf
[ ! -e %{_sysconfdir}/%{name}/menu_local.conf ]  || %{__mv} %{_sysconfdir}/%{name}/menu_local.conf  /etc/thruk/menu_local.conf
[ ! -e %{_sysconfdir}/%{name}/htpasswd ]         || %{__mv} %{_sysconfdir}/%{name}/htpasswd         /etc/thruk/htpasswd

# add apache user to group naemon so thruk can access the livestatus socket
if /usr/bin/id %{apacheuser} &>/dev/null; then
    if ! /usr/bin/id -Gn %{apacheuser} 2>/dev/null | grep -q naemon ; then
%if %{defined suse_version}
%if 0%{?suse_version} < 1230
        /usr/sbin/groupmod -A %{apacheuser} naemon >/dev/null
%else
        /usr/sbin/usermod -a -G naemon %{apacheuser} >/dev/null
%endif
%else
        /usr/sbin/usermod -a -G naemon %{apacheuser} >/dev/null
%endif
    fi
fi
%if %{defined suse_version}
/etc/init.d/apache2 restart || /etc/init.d/apache2 start
%else
service httpd condrestart
%endif


%postun thruk
case "$*" in
  0)
    # POSTUN
    rm -f %{_sysconfdir}/%{apachedir}/conf-enabled/naemon.conf
    ;;
  1)
    # POSTUPDATE
    ;;
  *) echo case "$*" not handled in postun
esac
exit 0




%files

%files core
%doc README.md naemon.rpmlintrc
%doc naemon-core/AUTHORS naemon-core/COPYING
%doc naemon-core/ChangeLog naemon-core/INSTALL naemon-core/LEGAL
%doc naemon-core/NEWS naemon-core/README naemon-core/THANKS
%doc naemon-core/UPGRADING
%attr(0755,root,root) %{_bindir}/%{name}
%if 0%{?use_systemd}
  %attr(0644,root,root) %{_unitdir}/%{name}.service
  %attr(0644,root,root) %{_tmpfilesdir}/%{name}.conf
  %attr(0755,root,root) %{_bindir}/%{name}-ctl
%else
  %attr(0755,root,root) %{_initrddir}/naemon
%endif
%config(noreplace) %{_sysconfdir}/logrotate.d/%{name}-core
%attr(0755,root,root) %dir %{_sysconfdir}/%{name}/
%attr(2775,naemon,naemon) %dir %{_sysconfdir}/%{name}/conf.d
%attr(0755,naemon,naemon) %dir %{_sysconfdir}/%{name}/module-conf.d
%attr(0644,naemon,naemon) %config(noreplace) %{_sysconfdir}/%{name}/%{name}.cfg
%attr(0640,naemon,naemon) %config(noreplace) %{_sysconfdir}/%{name}/resource.cfg
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/sysconfig/%{name}
%attr(0755,naemon,naemon) %dir %{_localstatedir}/lib/%{name}/spool
%attr(2775,naemon,naemon) %dir %{_localstatedir}/lib/%{name}/spool/checkresults
%attr(2775,naemon,naemon) %dir %{_localstatedir}/cache/%{name}
%attr(0755,naemon,naemon) %dir %{_localstatedir}/lib/%{name}
%attr(0755,naemon,naemon) %dir %{_localstatedir}/log/%{name}
%attr(0755,naemon,naemon) %dir %{_localstatedir}/log/%{name}/archives
%attr(-,root,root) %{_libdir}/%{name}/plugins
%{_mandir}/man8/naemon.8*
%{_datadir}/%{name}/examples

%files tools
%attr(0755,root,root) %{_bindir}/naemonstats
%attr(0755,root,root) %{_bindir}/shadownaemon
%{_mandir}/man8/naemonstats.8*
%{_mandir}/man8/shadownaemon.8*

%files -n libnaemon
%attr(-,root,root) %{_libdir}/%{name}/libnaemon.so*
%{_mandir}/man8/naemonstats.8*
%{_mandir}/man8/shadownaemon.8*

%files core-dbg
%attr(0755,root,root) %{_bindir}/%{name}-dbg

%files devel
%attr(-,root,root) %{_includedir}/%{name}/
%attr(-,root,root) %{_libdir}/%{name}/libnaemon.a
%attr(-,root,root) %{_libdir}/%{name}/libnaemon.la
%attr(-,root,root) %{_libdir}/pkgconfig/naemon.pc

%files livestatus
%attr(0755,root,root) %{_bindir}/unixcat
%attr(0755,naemon,naemon) %dir %{_libdir}/%{name}/%{name}-livestatus
%attr(0644,root,root) %{_libdir}/%{name}/%{name}-livestatus/livestatus.so
%attr(0755,naemon,naemon) %dir %{_localstatedir}/log/%{name}
%attr(0755,root,root) %{python_sitelib}/livestatus
%attr(0640,naemon,naemon) %config(noreplace) %{_sysconfdir}/%{name}/module-conf.d/livestatus.cfg

%files thruk
%config(noreplace) %{_sysconfdir}/%{apachedir}/conf.d/naemon.conf
%attr(-,root,root) %{_datadir}/%{name}/naemon-thruk.include
%config(noreplace) %{_sysconfdir}/thruk/thruk_local.d/naemon.conf

%changelog
* Sun Jun 21 2015 Sven Nierlein <sven.nierlein@consol.de> 1.0.4-1
- Decouple thruk and replace with metapackage

* Sun Feb 23 2014 Daniel Wittenberg <dwittenberg2008@gmail.com> 0.8.0-2
- Add native and full systemctl control on el7

* Thu Feb 06 2014 Daniel Wittenberg <dwittenberg2008@gmail.com> 0.1.0-1
- Add reload for systemctl-based setups

* Thu Feb 06 2014 Sven Nierlein <sven.nierlein@consol.de> 0.1.0-1
- moved thruks reporting addon into seperate package

* Tue Nov 26 2013 Sven Nierlein <sven.nierlein@consol.de> 0.0.1-1
- initial naemon meta package
