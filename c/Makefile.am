SUBDIRS = src
#dist_doc_DATA = ../README.md
AM_CFLAGS = -Wall -Wextra -Werror
ACLOCAL_AMFLAGS = -I .m4/m4
nobase_dist_pkgdata_DATA = rules.tar.gz
include_HEADERS = include/declinator.h

rules.tar.gz: rules/
	tar czf $@ $^

install-data-hook:
	(cd $(DESTDIR)$(pkgdatadir) && \
	  tar xzf rules.tar.gz && \
	  $(RM) rules.tar.gz)
