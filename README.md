## Welcome to Naemon ##

Naemon is a host/service/network monitoring program with a very fast C
core and a Perl web interface. It is released under the GNU General
Public License. It works by scheduling checks of the configured
objects and then invoking plugins to do the actual checking. The
plugin interface is 100% Nagios compatible, since Naemon is a fork of
the aforementioned project.

## Contents

 * Naemon: Meta package for packaging
 * Naemon-Core: Core scheduler, worker, etc...
 * Naemon-Livestatus: Livestatus API
 * Thruk: Web Gui

### Installation ###

Before installing from source, consider using prebuild native
packages which make things a lot easier and cleaner.
Daily updated packages for common linux systems can be found at
http://labs.consol.de/naemon/testing/

For a fresh source installation, follow these steps. You will need
a standard build environment with gcc, automake, autoconf, etc... and
gperf and doxygen. For specific instructions for different distros, please see below.

    git clone --recursive https://github.com/naemon/naemon.git
    cd naemon
    ./configure
    make
    make [rpm|deb|install]


#### CentOS 6.5 minimal ####
    # CentOS are a bit of tricky since a lot of packages are not available from standard
    # repository. We needs to download a lot of components and build from source.
    ## Build Naemon
    # Install dependencies for Naemon
    yum install svn httpd-devel rpm-build doxygen wget httpd mod_fcgid perl-YAML git autoconf automake libtool rpmlint gperf mysql-devel gcc-c++ perl-Module-Install perl-CPAN gd-devel expat-devel dos2unix patch patchutils
    # Install some perl modules that are required for Naemon
    PERL_MM_USE_DEFAULT=1 perl -MCPAN -e 'install Config::Any'
    PERL_MM_USE_DEFAULT=1 perl -MCPAN -e 'install JSON::XS'
    PERL_MM_USE_DEFAULT=1 perl -MCPAN -e 'install Config::General'
    # Add user thruk
    useradd thruk
    cd /usr/local/src/
    # Get latest version of Naemon
    git clone --recursive https://github.com/naemon/naemon.git
    cd naemon
    # Ignore yui-compressor, are not available as a package
    export THRUK_SKIP_COMPRESS=1
    # Create compiler configuration
    ./configure
    # Create RPM, can't "make install" right now due to bugs
    make rpm
    cd /usr/local/src/
    # Install mod_fcgid, required by Thruk
    svn checkout http://svn.apache.org/repos/asf/httpd/mod_fcgid/trunk mod_fcgid
    cd mod_fcgid
    ./configure.apxs
    make
    make install
    chmod 705 /var/log/httpd
    # Disable SELinux, not supported by Thruk
    # Disable it right now
    setenforce 0
    # Make it persistent 
    vi /etc/selinux/config
        edit row "SELINUX=enforcing"
        replace with "SELINUX=disabled"
    # Install Naemon
    cd ~/rpmbuild/RPMS/`uname -p`
    rpm -i --nodeps naemon-devel-*.rpm naemon-core-*.rpm naemon-livestatus-*.rpm naemon-thruk-*.rpm naemon-thruk-libs-*.rpm naemon-*.rpm
    # Start new services
    chkconfig naemon on
    chkconfig thruk on
    chkconfig httpd on
    chkconfig iptables off #This is just for test, please adjust your IP-tables accordingly
    
    ## Build nagios-plugins
    cd ~/
    # Get nagios-plugins source
    wget https://www.nagios-plugins.org/download/nagios-plugins-1.5.tar.gz
    tar -xzvf nagios-plugins-1.5.tar.gz -C /usr/local/src/
    rm -rf nagios-plugins-1.5.tar.gz
    # Get qstat precompiled package, can't find source code to build from source
    wget http://pkgs.repoforge.org/qstat/qstat-2.11-1.el6.rf.`uname -p`.rpm
    rpm -i --nosignature qstat-2.11-1.el6.rf.*.rpm
    rm -rf qstat-2.11-1.el6.rf.*.rpm
    # Get fping source
    wget http://fping.org/dist/fping-3.8.tar.gz
    tar -xzvf fping-3.8.tar.gz -C /usr/local/src/
    rm -rf fping-3.8.tar.gz
    # Get radiusclient-ng source
    wget http://downloads.sourceforge.net/project/radiusclient-ng.berlios/radiusclient-ng-0.5.6.tar.gz
    tar -xzvf radiusclient-ng-0.5.6.tar.gz -C /usr/local/src/
    rm -rf radiusclient-ng-0.5.6.tar.gz
    # Get lmutil, this is a tricky one. lmstat is the component that are required but it's
    # not longer available. All little tools have been incorporated within lmutil but
    # we can create a substitute that will work
    wget http://www.globes.com/products/utilities/v11.12/lmutil-x64_lsb-11.12.0.0v6.tar.gz
    tar -xzvf lmutil-x64_lsb-11.12.0.0v6.tar.gz -C /usr/local/bin/
    rm -rf lmutil-x64_lsb-11.12.0.0v6.tar.gz
    chmod +x /usr/local/bin/lmutil
    echo \#\!/bin/bash > /usr/local/bin/lmstat
    echo /usr/local/bin/lmutil lmstat \"\$\@\" >> /usr/local/bin/lmstat
    chmod +x /usr/local/bin/lmstat
    # Build and install radiusclient-nt
    cd /usr/local/src/radiusclient-ng-0.5.6
    ./configure
    make
    make install
    # Build and install fping
    cd /usr/local/src/fping-3.8/
    ./configure
    make
    make install
    # Install dependencies
    yum install net-snmp-utils postgresql-devel libdbi-devel bind-utils samba-client
    # Install perl modules
    PERL_MM_USE_DEFAULT=1 perl -MCPAN -e 'install Net::SNMP'
    # Build and install nagios-plugins
    cd /usr/local/src/nagios-plugins-1.5
    ./configure --with-nagios-user=naemon --with-nagios-group=naemon --libexec=/usr/lib64/nagios/plugins/
    make
    make install
    # Almost done, reboot to make sure everything starts as expected
    reboot

#### Ubuntu 12.04 ####
    # It's quite straight forward to build Naemon from source with Ubuntu, all required
    # softwares can be found as packages from the standard repository
    # Make us root so we don't have to sudo all the time
    sudo su -
    # Install dependencies 
    apt-get install bsd-mailx apache2 libapache2-mod-fcgid xvfb nagios-plugins git devscripts debhelper libmysqld-dev build-essential autoconf automake libtool dos2unix patch patchutils libmodule-install-perl gperf libgd2-xpm-dev yui-compressor
    # Add user thruk
    useradd thruk
    # Get latest version of Naemon
    cd /usr/local/src/
    git clone --recursive https://github.com/naemon/naemon.git
    # Build Naemon
    cd naemon
    ./configure
    # Create DEB, can't "make install" right now due to bugs
    make deb
    # Install Naemon
    cd ..
    dpkg -i naemon-dev_*.deb naemon-core_*.deb naemon-livestatus_*.deb naemon-thruk-libs_*.deb naemon-thruk_*.deb naemon_*.deb
    # Almost done, reboot to make sure everything starts as expected
    reboot

### More info ###

Visit the Naemon homepage at http://www.naemon.org

