
default-target: all
.PHONY: default-target

TARGETS = all clean distclean test install
SUBDIRS = c python

prefix?=/usr/local
DESTDIR?=/

$(TARGETS):
	@for d in $(SUBDIRS); do $(MAKE) -C $$d $@ || exit 2; done
.PHONY: $(TARGETS)
