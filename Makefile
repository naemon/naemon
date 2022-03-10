VERSION=1.3.0

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
	[ `git status | grep -cP 'working (directory|tree) clean'` -eq 1 ] || { echo "git project is not clean, cannot tag version"; exit 1; }

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
	NEWVERSION=`dialog --stdout --inputbox "New Version:" 0 0 "$(VERSION)"` && \
		if [ -n "$$NEWVERSION" ] && [ "$$NEWVERSION" != "$(VERSION)" ]; then \
			sed -ri "s/$(VERSION)/$$NEWVERSION/" Makefile naemon.spec; \
			sed -e 's/UNRELEASED/unstable/g' -i debian/changelog; \
			DEBFULLNAME="Naemon Development Team" DEBEMAIL="Naemon Development <naemon-dev@monitoring-lists.org>" dch --newversion "$$NEWVERSION" --package "naemon" -D "UNRELEASED" --urgency "low" "new upstream release"; \
			sed -e 's/unstable/UNRELEASED/g' -i debian/changelog; \
		fi;
	@echo ""
	@echo "******************"
	@echo "do not forget about naemon.io: _config.yml and documentation/usersguide/whatsnew.md"
	@echo "******************"

version: releaseversion
