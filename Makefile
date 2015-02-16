VERSION=1.0.1
RELEASE=2015-02-16

.PHONY: naemon-core naemon-livestatus thruk

P5DIR?=$(shell pwd)/thruk/libs/.build
export P5DIR
P5TMPDIST=$(P5DIR)
export P5TMPDIST

DAILYVERSION=$(shell ./get_version)

all: naemon-core naemon-livestatus thruk
	@echo "***************************************"
	@echo "Naemon build complete"
	@echo ""
	@echo "continue with"
	@echo "make [rpm|deb|install]"
	@echo ""


thruk:
	cd thruk && P5TMPDIST=${P5DIR} make
	cd thruk && make staticfiles

naemon-core:
	cd naemon-core && make

naemon-livestatus:
	cd naemon-livestatus && make CPPFLAGS="$$CPPFLAGS -I$$(pwd)/../naemon-core/src"

update: update-naemon-core update-naemon-livestatus update-thruk
	@if [ `git status 2>/dev/null | grep -c "new commits"` -gt 0 ]; then \
		git commit -av -m 'automatic update';\
		git log -1; \
	else \
		echo "no updates available"; \
	fi

update-naemon-core: submoduleinit
	cd naemon-core && git checkout master && git pull --rebase

update-naemon-livestatus: submoduleinit
	cd naemon-livestatus && git checkout master &&  git pull --rebase

update-thruk: submoduleinit
	cd thruk && make update

submoduleinit:
	git submodule init

clean:
	-cd naemon-core && make clean
	-cd naemon-livestatus && make clean
	-cd thruk && make clean
	rm -rf naemon-${VERSION} naemon-${VERSION}.tar.gz

install:
	cd naemon-core && make install
	cd naemon-livestatus && make install
	cd thruk && make install
	# some corrections to avoid conflicts

dist:
	rm -rf naemon-${VERSION} naemon-${VERSION}.tar.gz
	mkdir naemon-${VERSION}
	git archive --format=tar HEAD | tar x -C "naemon-${VERSION}"
	cd naemon-core       && git archive --format=tar HEAD | tar x -C    "../naemon-${VERSION}/naemon-core/"
	cd naemon-livestatus && git archive --format=tar HEAD | tar x -C    "../naemon-${VERSION}/naemon-livestatus/"
	cd thruk/gui         && git archive --format=tar HEAD | tar x -C "../../naemon-${VERSION}/thruk/gui/"
	cd thruk/libs        && git archive --format=tar HEAD | tar x -C "../../naemon-${VERSION}/thruk/libs/"
	cd naemon-${VERSION}/naemon-core && autoreconf -i -v
	cd naemon-${VERSION}/naemon-livestatus && autoreconf -i -v
	cp -p thruk/gui/Makefile naemon-${VERSION}/thruk/gui
	cd naemon-${VERSION}/thruk/gui && ./script/thruk_patch_makefile.pl
	-cd naemon-${VERSION}/thruk/gui && make staticfiles >/dev/null 2>&1
	tar cf "naemon-${VERSION}.tar" \
		--exclude=thruk/gui/support/thruk.spec \
		--exclude=thruk/gui/debian \
		--exclude=naemon-core/naemon.spec \
		--exclude=.gitmodules \
		--exclude=.gitignore \
		"naemon-${VERSION}"
	gzip -9 "naemon-${VERSION}.tar"
	cd naemon-${VERSION} && mv naemon-core naemon-core-${VERSION} && tar cf "naemon-core-${VERSION}.tar" naemon-core-${VERSION}
	gzip -9 "naemon-${VERSION}/naemon-core-${VERSION}.tar"
	mv naemon-${VERSION}/naemon-core-${VERSION}.tar.gz .
	cd naemon-${VERSION} && mv naemon-livestatus naemon-livestatus-${VERSION} && tar cf "naemon-livestatus-${VERSION}.tar" naemon-livestatus-${VERSION}
	gzip -9 "naemon-${VERSION}/naemon-livestatus-${VERSION}.tar"
	mv naemon-${VERSION}/naemon-livestatus-${VERSION}.tar.gz .
	rm -rf "naemon-${VERSION}"

naemon-${VERSION}.tar.gz: dist

rpm: naemon-${VERSION}.tar.gz
	# NO_BRP_STALE_LINK_ERROR ignores errors when symlinking non existing
	# folders. And since we link the plugins folder to a not yet installed pkg,
	# the build will break
	NO_BRP_STALE_LINK_ERROR="yes" P5TMPDIST=${P5DIR} rpmbuild -tb naemon-${VERSION}.tar.gz

deb:
	P5TMPDIST=${P5DIR} debuild -i -us -uc -b

versionprecheck:
	[ -e .git ] || { echo "changing versions only works in git clones!"; exit 1; }
	which dch >/dev/null 2>&1 || { echo "dch is required for changing versions"; exit 1; }
	[ `git status | grep -c 'working directory clean'` -eq 1 ] || { echo "git project is not clean, cannot tag version"; exit 1; }

resetdaily: versionprecheck
	git checkout .
	cd naemon-core       && if [ $$(git log -1 | grep -c "automatic build commit:") -gt 0 ]; then git reset HEAD^ && git checkout .; fi
	cd naemon-livestatus && if [ $$(git log -1 | grep -c "automatic build commit:") -gt 0 ]; then git reset HEAD^ && git checkout .; fi
	cd thruk/gui         && if [ $$(git log -1 | grep -c "automatic build commit:") -gt 0 ]; then git reset HEAD^; git checkout .; git clean -xdf; yes n | perl Makefile.PL || yes n | perl Makefile.PL; fi
	cd thruk/libs        && git checkout .
	if [ $$(git log -1 | grep -c "automatic build commit:") -gt 0 ]; then git reset HEAD^ && git checkout .; fi
	git submodule update
	cd thruk/gui         && git checkout master
	cd thruk/libs        && git checkout master
	cd naemon-core       && git checkout master
	cd naemon-livestatus && git checkout master

dailyversion: versionprecheck
	cd thruk/gui         && git checkout master
	cd thruk/libs        && git checkout master
	cd naemon-core       && git checkout master
	cd naemon-livestatus && git checkout master
	cd thruk/gui && yes 'n' | perl Makefile.PL >/dev/null 2>&1 && make newversion && git add . && git commit -a -m "automatic build commit: ${DAILYVERSION}"
	./update-version ${DAILYVERSION}
	cd naemon-core       && git commit -a -m "automatic build commit: ${DAILYVERSION}"
	cd naemon-livestatus && git commit -a -m "automatic build commit: ${DAILYVERSION}"
	git commit -a -m "automatic build commit: ${DAILYVERSION}"
	@echo ""
	@echo "******************"
	@echo "ATTENTION: daily version (`grep ^VERSION Makefile | awk -F= '{ print $$2 }'`) set, do not push! Instead use 'make resetdaily' to unstage after building."
	@echo "******************"

dailydist:
	make update
	make resetdaily
	make dailyversion
	make dist
	make resetdaily
	@echo "finished"
	@echo "optional submodule tarballs created: naemon-core-${DAILYVERSION}.tar.gz and naemon-livestatus-${DAILYVERSION}.tar.gz"
	@echo "daily dist created: naemon-${DAILYVERSION}.tar.gz"

releaseversion: versionprecheck
	RELEASEVERSION=`dialog --stdout --inputbox "New Version:" 0 0 "${VERSION}"` && \
		./update-version $$RELEASEVERSION && \
		cd naemon-core && git commit -as -m "released $$RELEASEVERSION" && git tag "v$$RELEASEVERSION" && cd .. && \
		cd naemon-livestatus && git commit -as -m "released $$RELEASEVERSION" && git tag "v$$RELEASEVERSION" && cd .. && \
		git commit -as -m "released $$RELEASEVERSION" && git tag "v$$RELEASEVERSION"
	@echo ""
	@echo "******************"
	@echo "ATTENTION: release tag (`grep ^VERSION Makefile | awk -F= '{ print $$2 }'`) set, please double check before pushing anything."
	@echo "******************"

version: releaseversion
