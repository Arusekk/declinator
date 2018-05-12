
default-target: all
.PHONY: default-target

TARGETS = all clean distclean test
SUBDIRS = c

$(TARGETS):
	@for d in $(SUBDIRS); do $(MAKE) -C $$d $@; done
.PHONY: $(TARGETS)
