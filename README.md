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

#### Ubuntu 12.04 LTS Server ####
    sudo su -
    apt-get install git devscripts debhelper libmysqld-dev build-essential autoconf automake libtool dos2unix patch patchutils libmodule-install-perl gperf libgd2-xpm-dev yui-compressor
    useradd thruk
    cd /usr/local/src/
    git clone --recursive https://github.com/naemon/naemon.git
    cd naemon
    ./configure
    make
    make deb
    cd ..
    apt-get install bsd-mailx apache2 libapache2-mod-fcgid xvfb nagios-plugins
    dpkg -i naemon-dev_0.0.1_amd64.deb naemon-core_0.0.1_amd64.deb naemon-livestatus_0.0.1_amd64.deb naemon-thruk-libs_0.0.1_amd64.deb naemon-thruk_0.0.1_amd64.deb naemon_0.0.1_amd64.deb

### More info ###

Visit the Naemon homepage at http://www.naemon.org

