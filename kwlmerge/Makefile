
UIC=mergemain

UICPY=$(patsubst %,ui_%.py,$(UIC))

all: ui

.PHONY: all ui check clean

check:

ui: $(UICPY)

ui_%.py: %.ui
	pyuic4 -o $@ $<

clean:
	rm -f $(UICPY)
