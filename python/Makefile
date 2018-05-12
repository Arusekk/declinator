PYTHON=python

all:
	$(PYTHON) -c 'import declinator'
test:
	$(PYTHON) -m declinator.test |tee testout
	wc -c < testout |grep '^0$$'
clean distclean:
.PHONY: all clean distclean test
