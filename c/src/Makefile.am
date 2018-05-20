bin_PROGRAMS = declinator

declinator_SOURCES = main.c
declinator_CFLAGS = $(JSON_C_CFLAGS) -I../include
declinator_LDADD = libdeclinator.la $(JSON_C_LIBS)
declinatordir = .

lib_LTLIBRARIES = libdeclinator.la
libdeclinator_la_SOURCES = declinator.c duplidict.c duplidict.h
libdeclinator_la_CFLAGS = $(JSON_C_CFLAGS) $(PCRE_CFLAGS) -I../include
libdeclinator_la_LIBADD = $(JSON_C_LIBS) $(PCRE_LIBS)
libdeclinator_la_LDFLAGS = -version-info 1:1:0
