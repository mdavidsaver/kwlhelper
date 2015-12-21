
all: sub-all

.PHONY: all check clean

check: sub-check

clean: sub-clean

sub-%:
	$(MAKE) -C kwlhelper $(patsubst sub-%,%,$@)
	#$(MAKE) -C tests $(patsubst sub-%,%,$@)
