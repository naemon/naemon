VERSION=1.0.7

.PHONY: thruk

DAILYVERSION=$(shell ./get_version)

all: thruk
	@echo "***************************************"
	@echo "Naemon build complete"
	@echo ""
	@echo "continue with"
	@echo "make [rpm|deb|install]"
	@echo ""


thruk:
	cd thruk && make

clean:
	-cd thruk && make clean
	rm -rf naemon-${VERSION} naemon-${VERSION}.tar.gz

install:
	cd thruk && make install

dist:
	rm -rf naemon-${VERSION} naemon-${VERSION}.tar.gz
	mkdir naemon-${VERSION}
	git archive --format=tar HEAD | tar x -C "naemon-${VERSION}"
	tar cf "naemon-${VERSION}.tar" \
		--exclude=.gitignore \
		"naemon-${VERSION}"
	gzip -9 "naemon-${VERSION}.tar"
	rm -rf "naemon-${VERSION}"

naemon-${VERSION}.tar.gz: dist

rpm: naemon-${VERSION}.tar.gz
	rpmbuild -tb naemon-${VERSION}.tar.gz

deb:
	debuild -i -us -uc -b

versionprecheck:
	[ -e .git ] || { echo "changing versions only works in git clones!"; exit 1; }
	which dch >/dev/null 2>&1 || { echo "dch is required for changing versions"; exit 1; }
	[ `git status | grep -c 'working directory clean'` -eq 1 ] || { echo "git project is not clean, cannot tag version"; exit 1; }

resetdaily: versionprecheck
	git checkout .
	if [ $$(git log -1 | grep -c "automatic build commit:") -gt 0 ]; then git reset HEAD^ && git checkout .; fi

dailyversion: versionprecheck
	./update-version ${DAILYVERSION}
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
	@echo "daily dist created: naemon-${DAILYVERSION}.tar.gz"

releaseversion: versionprecheck
	RELEASEVERSION=`dialog --stdout --inputbox "New Version:" 0 0 "${VERSION}"` && \
		./update-version $$RELEASEVERSION && \
		git commit -as -m "released $$RELEASEVERSION" && git tag "v$$RELEASEVERSION"
	@echo ""
	@echo "******************"
	@echo "ATTENTION: release tag (`grep ^VERSION Makefile | awk -F= '{ print $$2 }'`) set, please double check before pushing anything."
	@echo "naemon-core/NEWS file has to be updated manually!"
	@echo "also do not forget about naemon.org: _config.yml and documentation/usersguide/whatsnew.md"
	@echo "******************"

version: releaseversion
