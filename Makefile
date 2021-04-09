build: generated src/nbfc_service src/ec_probe

install: build
	# Binaries first
	mkdir -p $(DESTDIR)/usr/bin
	install nbfc.py          $(DESTDIR)/usr/bin/nbfc
	install src/nbfc_service $(DESTDIR)/usr/bin/nbfc_service
	install src/ec_probe     $(DESTDIR)/usr/bin/ec_probe
	# /etc/systemd/system
	mkdir -p $(DESTDIR)/etc/systemd/system
	cp etc/systemd/system/nbfc_service.service $(DESTDIR)/etc/systemd/system/nbfc_service.service
	# /etc/nbfc/configs/
	mkdir -p $(DESTDIR)/etc/nbfc
	cp -r etc/nbfc/configs $(DESTDIR)/etc/nbfc/
	# Doc
	mkdir -p $(DESTDIR)/usr/share/man/man{1,5}
	cp doc/ec_probe.1          $(DESTDIR)/usr/share/man/man1
	cp doc/nbfc.1              $(DESTDIR)/usr/share/man/man1
	cp doc/nbfc_service.1      $(DESTDIR)/usr/share/man/man1
	cp doc/nbfc_service.json.5 $(DESTDIR)/usr/share/man/man5
	# Completion
	mkdir -p $(DESTDIR)/usr/share/zsh/site-functions
	cp completion/zsh/_nbfc          $(DESTDIR)/usr/share/zsh/site-functions/
	cp completion/zsh/_nbfc_service  $(DESTDIR)/usr/share/zsh/site-functions/
	cp completion/zsh/_ec_probe      $(DESTDIR)/usr/share/zsh/site-functions/
	mkdir -p $(DESTDIR)/usr/share/bash-completion/completions
	cp completion/bash/nbfc          $(DESTDIR)/usr/share/bash-completion/completions/
	cp completion/bash/nbfc_service  $(DESTDIR)/usr/share/bash-completion/completions/
	cp completion/bash/ec_probe      $(DESTDIR)/usr/share/bash-completion/completions/

clean:
	rm -rf xml_configs __pycache__ tools/argany/__pycache__
	(cd src; make clean)

clean_generated: clean
	rm -rf ec_probe.md nbfc.md nbfc_service.md nbfc_service.json.md
	rm -rf etc/nbfc/configs
	rm -rf doc completion

generated: etc/nbfc/configs \
	completion/zsh/_ec_probe completion/zsh/_nbfc completion/zsh/_nbfc_service \
	completion/bash/ec_probe completion/bash/nbfc completion/bash/nbfc_service \
	ec_probe.md nbfc.md nbfc_service.md nbfc_service.json.md \
	doc/ec_probe.1 doc/nbfc.1 doc/nbfc_service.json.5 doc/nbfc_service.1

# =============================================================================
# Binaries ====================================================================
# =============================================================================

src/nbfc_service:
	(cd src; make nbfc_service)

src/ec_probe:
	(cd src; make ec_probe)

# =============================================================================
# Configs / XML->JSON Conversion ==============================================
# =============================================================================

etc/nbfc/configs:
	mkdir -p etc/nbfc/configs
	[ -e nbfc ] || git clone https://github.com/hirschmann/nbfc
	./tools/config_to_json.py nbfc/Configs/*
	mv nbfc/Configs/*.json etc/nbfc/configs/

# =============================================================================
# Completion ==================================================================
# =============================================================================

completion/bash/:
	mkdir -p completion/bash

completion/zsh/:
	mkdir -p completion/zsh

completion/zsh/_nbfc: completion/zsh/
	./tools/argany/argany.py zsh ./nbfc.py > completion/zsh/_nbfc

completion/zsh/_nbfc_service: completion/zsh/
	./tools/argany/argany.py zsh ./tools/argany/nbfc_service.py > completion/zsh/_nbfc_service

completion/zsh/_ec_probe: completion/zsh/
	./tools/argany/argany.py zsh ./tools/argany/ec_probe.py > completion/zsh/_ec_probe

completion/bash/nbfc: completion/bash/
	./tools/argany/argany.py bash ./nbfc.py > completion/bash/nbfc

completion/bash/nbfc_service: completion/bash/
	./tools/argany/argany.py bash ./tools/argany/nbfc_service.py > completion/bash/nbfc_service

completion/bash/ec_probe: completion/bash/
	./tools/argany/argany.py bash ./tools/argany/ec_probe.py > completion/bash/ec_probe

# =============================================================================
# Markdown ====================================================================
# =============================================================================

ec_probe.md: ./tools/argany/ec_probe.py
	./tools/argany/ec_probe.py markdown > ec_probe.md

nbfc.md: ./tools/argany/nbfc.argany.py
	./tools/argany/nbfc.argany.py markdown > nbfc.md

nbfc_service.md: ./tools/argany/nbfc_service.py
	./tools/argany/nbfc_service.py markdown > nbfc_service.md

nbfc_service.json.md: ./tools/config_to_md.py ./tools/config.json
	./tools/config_to_md.py  > nbfc_service.json.md

# =============================================================================
# Manual pages ================================================================
# =============================================================================

doc/:
	mkdir -p doc

doc/ec_probe.1: doc/ ec_probe.md
	go-md2man < ec_probe.md > doc/ec_probe.1

doc/nbfc.1: doc/ nbfc.md
	go-md2man < nbfc.md > doc/nbfc.1

doc/nbfc_service.json.5: doc/ nbfc_service.json.md
	go-md2man < nbfc_service.json.md > doc/nbfc_service.json.5

doc/nbfc_service.1: doc/ nbfc_service.md
	go-md2man < nbfc_service.md > doc/nbfc_service.1

