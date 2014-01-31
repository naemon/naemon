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

#### Build and install via packages ####
##### CentOS 6.5 minimal #####
    # CentOS are a bit of tricky since a lot of packages are not available from standard
    # repository. We needs to download a lot of components and build from source.
    ## Build Naemon
    # Install dependencies for Naemon
    yum install svn httpd-devel rpm-build doxygen wget httpd mod_fcgid perl-YAML git autoconf automake libtool rpmlint gperf mysql-devel gcc-c++ perl-Module-Install perl-CPAN gd-devel expat-devel dos2unix patch patchutils
    
    # Install some perl modules that are required for Naemon
    PERL_MM_USE_DEFAULT=1 perl -MCPAN -e 'install Config::Any'
    PERL_MM_USE_DEFAULT=1 perl -MCPAN -e 'install JSON::XS'
    PERL_MM_USE_DEFAULT=1 perl -MCPAN -e 'install Config::General'
    PERL_MM_USE_DEFAULT=1 perl -MCPAN -e 'install File::Slurp'
    
    # Add users, needed to build the package
    useradd thruk
    useradd naemon
    
    # Get latest version of Naemon
    cd /usr/local/src/
    git clone --recursive https://github.com/naemon/naemon.git
    cd naemon
    
    # Ignore yui-compressor, are not available as a package
    export THRUK_SKIP_COMPRESS=1
    
    # Create compiler configuration
    ./configure --with-pluginsdir=/usr/lib64/nagios/plugins/ --without-tests
    
    # Create RPM
    make rpm
    
    # Remove users, let the package create them instead
    userdel thruk
    userdel naemon
    
    # Install mod_fcgid, required by Thruk
    cd /usr/local/src/
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
    
    # Enable new services on boot and start them
    service iptables stop #This is just for testing and will restart the firewall after reboot, please adjust your IP-tables accordingly
    chkconfig httpd on && service httpd start
    chkconfig naemon on && service naemon start
        chkconfig thruk on && service thruk start
    
    # Install Nagios plugins
    rpm -Uvh http://dl.fedoraproject.org/pub/epel/6/x86_64/epel-release-6-8.noarch.rpm
    yum -y install nagios-plugins-all nagios-plugins-nrpe nrpe
  
    # Done!
    # Browse to <hostname>/naemon and use thrukadmin/thrukadmin

#### Ubuntu 12.04 ####
    # It's quite straight forward to build Naemon from source with Ubuntu, all required
    # softwares can be found as packages from the standard repository
    
    # Make us root so we don't have to sudo all the time
    sudo su -
    
    # Install dependencies 
    apt-get install bsd-mailx apache2 libapache2-mod-fcgid xvfb nagios-plugins git devscripts debhelper libmysqld-dev build-essential autoconf automake libtool dos2unix patch patchutils libmodule-install-perl gperf libgd2-xpm-dev yui-compressor
    
    # Add users, needed to build the package
    useradd thruk
    useradd naemon
    
    # Get latest version of Naemon
    cd /usr/local/src/
    git clone --recursive https://github.com/naemon/naemon.git
    
    # Build Naemon
    cd naemon
    ./configure --with-pluginsdir=/usr/lib/nagios/plugins/ --without-tests
    
    # Create DEB
    make deb
    
    # Remove users, let the package create them instead
    deluser thruk
    deluser naemon
    
    # Install Naemon
    cd ..
    dpkg -i naemon-dev_*.deb naemon-core_*.deb naemon-livestatus_*.deb naemon-thruk-libs_*.deb naemon-thruk_*.deb naemon_*.deb
    
    # Almost done, reboot to make sure everything starts as expected
    reboot
    
    # Done!
    # Browse to <hostname>/naemon and use thrukadmin/thrukadmin

### More info ###

Visit the Naemon homepage at http://www.naemon.org

