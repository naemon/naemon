VERSION=0.0.1
RELEASE=2013-12-11

.PHONY: naemon-core naemon-livestatus thruk

all: naemon-core naemon-livestatus thruk
	@echo "***************************************"
	@echo "Naemon build complete"
	@echo ""
	@echo "continue with"
	@echo "make [rpm|deb|install]"
	@echo ""


thruk:
	cd thruk && make

naemon-core:
	cd naemon-core && make

naemon-livestatus:
	cd naemon-livestatus && make CPPFLAGS="$$CPPFLAGS -I$$(pwd)/../naemon-core"

update: update-naemon-core update-naemon-livestatus update-thruk
	@if [ `git status 2>/dev/null | grep -c "Changed but not updated"` -eq 1 ]; then \
		git commit -av -m 'automatic update';\
		git log -1; \
	else \
		echo "no updates available"; \
	fi

update-naemon-core: submoduleinit
	cd naemon-core && git checkout master && git pull

update-naemon-livestatus: submoduleinit
	cd naemon-livestatus && git checkout master &&  git pull

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
	cd naemon-${VERSION}/thruk/gui && make staticfiles
	tar cf "naemon-${VERSION}.tar" \
		--exclude=thruk/gui/support/thruk.spec \
		--exclude=thruk/gui/debian \
		--exclude=naemon-core/naemon.spec \
		--exclude=.gitmodules \
		--exclude=.gitignore \
		"naemon-${VERSION}"
	gzip -9 "naemon-${VERSION}.tar"
	rm -rf "naemon-${VERSION}"

naemon-${VERSION}.tar.gz: dist

rpm: naemon-${VERSION}.tar.gz
	rpmbuild -tb naemon-${VERSION}.tar.gz

deb:
	debuild -i -us -uc -b
