PYTHON?=python

all:
	$(PYTHON) setup.py build
test:
	$(PYTHON) -m declinator.test |tee testout
	wc -c < testout |grep '^0$$'
install:
	$(PYTHON) setup.py install --prefix=$(prefix) --root=$(DESTDIR)
clean distclean:
.PHONY: all clean distclean test install
