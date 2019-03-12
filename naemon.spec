%if %{defined suse_version}
%define apacheuser wwwrun
%define apachegroup www
%define apachedir apache2
%else
%define apacheuser apache
%define apachegroup apache
%define apachedir httpd
%endif

Summary: Open Source Host, Service And Network Monitoring Program
Name: naemon
Version: 1.0.10
Release: 0
License: GPLv2
BuildArch: noarch
Group: Applications/System
URL: http://www.naemon.org/
Packager: Naemon Core Development Team <naemon-dev@monitoring-lists.org>
Vendor: Naemon Core Development Team
Source0: http://labs.consol.de/naemon/download/%{name}-%{version}.tar.gz
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}
%if %{defined suse_version}
BuildRequires: apache2
%else
BuildRequires: httpd
%endif
Requires: %{name}-core            >= %{version}-%{release}
Requires: %{name}-livestatus      >= %{version}-%{release}
Requires: %{name}-thruk           = %{version}-%{release}

# do not generate debug packages
%define debug_package %{nil}

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


%package thruk
Summary:     Thruk Gui For Naemon
Group:       Applications/System
Requires:    thruk
Requires(pre): naemon-core >= %{version}-%{release}
%if 0%{?systemd_requires}
%systemd_requires
%endif
Obsoletes: naemon-thruk-reporting
Obsoletes: naemon-thruk-libs

%description thruk
This package contains the thruk gui for %{name}.

%prep
%setup -q

%build
%{__make}

%install
%{__rm} -rf %{buildroot}
%{__make} install DESTDIR="%{buildroot}"


%clean
%{__rm} -rf %{buildroot}


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

# restart apache webserver
%if %{defined suse_version}
  %if %{?_unitdir:1}0
    systemctl daemon-reload &>/dev/null || true
    systemctl condrestart apache2.service &>/dev/null || true
  %else
    /etc/init.d/apache2 restart &>/dev/null || true
  %endif
%else
  %if %{?_unitdir:1}0
    systemctl daemon-reload &>/dev/null || true
    systemctl condrestart httpd.service &>/dev/null || true
  %else
    /etc/init.d/httpd condrestart &>/dev/null || true
  %endif
%endif
exit 0

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

%files thruk
%config(noreplace) %{_sysconfdir}/%{apachedir}/conf.d/naemon.conf
%attr(-,root,root) %{_datadir}/%{name}/naemon-thruk.include
%config(noreplace) %{_sysconfdir}/thruk/thruk_local.d/naemon.conf
%if 0%{?suse_version} >= 1315
%attr(-,-,-) %dir %{_sysconfdir}/thruk/
%attr(-,-,-) %dir %{_sysconfdir}/thruk/thruk_local.d/
%endif

%changelog
* Tue Sep 19 2017 Sven Nierlein <sven.nierlein@consol.de> 1.0.7-1
- Decouple core and livestatus

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
