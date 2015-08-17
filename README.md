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

Before installing from source, consider using prebuilt native
packages which make things a lot easier and cleaner.
Daily updated packages for common linux systems can be found at
http://labs.consol.de/naemon/testing/

For a fresh source installation, follow these steps. You will need
a standard build environment with gcc, automake, autoconf, etc... and
gperf and doxygen.

    git clone --recursive https://github.com/naemon/naemon.git
    cd naemon
    make update
    ./configure
    make
    make [rpm|deb|install]

### More info ###

Visit the Naemon homepage at http://naemon.org

