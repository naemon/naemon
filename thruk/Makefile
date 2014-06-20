# make sure this file exists, "make update" would require a
# configure run otherwise
$(shell touch gui/script/append.make.options)
include gui/script/append.make.options

P5TMPDIST = $(shell pwd)/libs/.build

all:
	[ ${THRUKLIBS} -ne '' ] || cd libs && make
	cd gui && yes n | PERL5LIB=$$P5DIR/dest/lib/perl5/:${P5TMPDIST}/dest/lib/perl5 perl Makefile.PL

staticfiles:
	cd gui && PERL5LIB=$$P5DIR/dest/lib/perl5/:${P5TMPDIST}/dest/lib/perl5 make staticfiles

install:
	cd gui && make install naemon-patch
	[ "x${THRUKLIBS}" != 'x' ] || mkdir -p ${DESTDIR}${THRUKLIBS}
	[ "x${THRUKLIBS}" != 'x' ] || cp -rp ${P5TMPDIST}/dest/lib/perl5/* ${DESTDIR}${THRUKLIBS}/
	# clean up some old files
	rm -rf ${DESTDIR}/etc/naemon/themes/themes-available/{Wakizashi,Neat}
	rm -rf ${DESTDIR}/etc/naemon/themes/themes-enabled/{Wakizashi,Neat}
	rm -rf ${DESTDIR}/usr/share/naemon/themes/themes-available/{Wakizashi,Neat}
	rm -rf ${DESTDIR}/usr/share/naemon/plugins/plugins-enabled/shinken_features
	rm -rf ${DESTDIR}/etc/naemon/plugins/plugins-enabled/shinken_features
	echo "Naemon $$(grep ^VERSION ../Makefile | awk -F= {' print $$2 '})" > ${DESTDIR}/${DATADIR}/naemon-version

update: update-git
	# this can later be changed to release version

update-release:
	cd gui && git clean -uxd && git pull
	version=`cd gui && git tag -l | sort -V | tail -n 1`; \
		echo "updating to last stable: $$version"; \
		cd gui && git reset --hard $$version; cd ..; \
		cd libs && git clean -uxd && git pull && git reset --hard $$version;

update-git:
	cd gui && git checkout master && git pull --rebase
	cd libs && git checkout master && git pull --rebase

clean:
	-cd libs && make clean
	-cd gui && make clean
	rm -f thruk_local.conf
