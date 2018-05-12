default-target: all
.PHONY: default-target

AR ?= ar

PKGS-LIBRARY = json-c libpcre
PKGS-EXEC = json-c
OBJECTS-LIBRARY = duplidict.o declinator.o
OBJECTS-EXEC = main.o
LIBRARY = libdeclinator.so
LIBRARY-STATIC = libdeclinator.a
EXEC = declinator
CFLAGS ?= -Wall -Wextra -std=gnu99

CFLAGS-LIBRARY := $(CFLAGS) $(shell pkg-config --cflags $(PKGS-LIBRARY)) -fPIC -g
LDFLAGS-LIBRARY := $(LDFLAGS) $(shell pkg-config --libs $(PKGS-LIBRARY))

CFLAGS-EXEC := $(CFLAGS)
LDFLAGS-EXEC := $(LDFLAGS) -ldeclinator -L. $(shell pkg-config --libs $(PKGS-EXEC))

TARGETS := $(LIBRARY) $(EXEC) $(EXEC)-static

$(OBJECTS-LIBRARY): %.o: %.c
	$(CC) -c $(CFLAGS-LIBRARY) -o $@ $<

$(LIBRARY): $(OBJECTS-LIBRARY)
	$(CC) $(CFLAGS-LIBRARY) -shared -o $@ $(OBJECTS-LIBRARY) $(LDFLAGS-LIBRARY)

$(LIBRARY-STATIC): $(OBJECTS-LIBRARY)
	$(AR) rcu $@ $?

$(EXEC): $(OBJECTS-EXEC) $(LIBRARY)
	$(CC) $(CFLAGS-EXEC) -o $@ $(OBJECTS-EXEC) $(LDFLAGS-EXEC)

$(EXEC)-static: $(OBJECTS-EXEC) $(LIBRARY-STATIC)
	$(CC) $(CFLAGS-EXEC) -static -o $@ $(OBJECTS-EXEC) $(LDFLAGS-EXEC) $(LDFLAGS-LIBRARY) || :

all: $(TARGETS)
.PHONY: all

clean:
	$(RM) $(OBJECTS-LIBRARY) $(OBJECTS-EXEC)
.PHONY: clean

distclean:
	$(RM) $(OBJECTS-LIBRARY) $(OBJECTS-EXEC) $(TARGET)
.PHONY: distclean
