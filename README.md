## Welcome to Naemon ##

Naemon is a host/service/network monitoring program written in C and
released under the GNU General Public License. It works by scheduling
checks of the configured objects and then invoking plugins to do the
actual checking. The plugin interface is 100% Nagios compatible, since
Naemon is a fork of the aforementioned project.

## Contents

 * Naemon: Meta package for packaging
 * Naemon-Core: Core scheduler, worker, etc...
 * Naemon-Livestatus: Livestatus API
 * Thruk: Web Gui

### Installation ###

Before installing from source, consider using prebuild native
packages which make things a log easier and cleaner.
Daily update packages are here: http://labs.consol.de/naemon/testing/

For a fresh source installation, clone this repository and run:

 ./configure
 make
 make [rpm|deb|install]

### More info ###

Visit the Naemon homepage at http://www.naemon.org
