
all: sub-all

.PHONY: all check clean

check: sub-check

clean: sub-clean

sub-%:
	$(MAKE) -C kwlmerge $(patsubst sub-%,%,$@)
	#$(MAKE) -C tests $(patsubst sub-%,%,$@)
