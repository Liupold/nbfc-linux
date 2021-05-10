build: src/nbfc_service src/ec_probe

install: build
	# Binaries
	mkdir -p $(DESTDIR)/usr/bin
	install nbfc.py           $(DESTDIR)/usr/bin/nbfc
	install src/nbfc_service  $(DESTDIR)/usr/bin/nbfc_service
	install src/ec_probe      $(DESTDIR)/usr/bin/ec_probe
	
	# /etc/systemd/system
	mkdir -p $(DESTDIR)/etc/systemd/system
	cp etc/systemd/system/nbfc_service.service $(DESTDIR)/etc/systemd/system/nbfc_service.service
	
	# /etc/nbfc/configs/
	mkdir -p $(DESTDIR)/etc/nbfc
	cp -r etc/nbfc/configs $(DESTDIR)/etc/nbfc/
	
	# Documentation
	mkdir -p $(DESTDIR)/usr/share/man/man1
	mkdir -p $(DESTDIR)/usr/share/man/man5
	cp doc/ec_probe.1            $(DESTDIR)/usr/share/man/man1
	cp doc/nbfc.1                $(DESTDIR)/usr/share/man/man1
	cp doc/nbfc_service.1        $(DESTDIR)/usr/share/man/man1
	cp doc/nbfc_service.json.5   $(DESTDIR)/usr/share/man/man5
	
	# Completion
	mkdir -p $(DESTDIR)/usr/share/zsh/site-functions
	cp completion/zsh/_nbfc                $(DESTDIR)/usr/share/zsh/site-functions/
	cp completion/zsh/_nbfc_service        $(DESTDIR)/usr/share/zsh/site-functions/
	cp completion/zsh/_ec_probe            $(DESTDIR)/usr/share/zsh/site-functions/
	mkdir -p $(DESTDIR)/usr/share/bash-completion/completions
	cp completion/bash/nbfc                $(DESTDIR)/usr/share/bash-completion/completions/
	cp completion/bash/nbfc_service        $(DESTDIR)/usr/share/bash-completion/completions/
	cp completion/bash/ec_probe            $(DESTDIR)/usr/share/bash-completion/completions/
	mkdir -p $(DESTDIR)/usr/share/fish/completions
	cp completion/fish/nbfc.fish           $(DESTDIR)/usr/share/fish/completions/
	cp completion/fish/nbfc_service.fish   $(DESTDIR)/usr/share/fish/completions/
	cp completion/fish/ec_probe.fish       $(DESTDIR)/usr/share/fish/completions/

clean:
	rm -rf __pycache__ tools/argany/__pycache__
	(cd src; make clean)

clean_generated: clean
	rm -rf doc completion etc/nbfc/configs

generated: doc completion etc/nbfc/configs .force

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

etc/nbfc/configs: .force
	mkdir -p etc/nbfc/configs
	[ -e nbfc ] || git clone https://github.com/hirschmann/nbfc
	./tools/config_to_json.py nbfc/Configs/*
	mv nbfc/Configs/*.json etc/nbfc/configs/

# =============================================================================
# Completion ==================================================================
# =============================================================================

completion: .force
	mkdir -p completion/bash completion/fish completion/zsh
	
	./tools/argany/argany.py\
		zsh  ./nbfc.py -o completion/zsh/_nbfc      ';'\
	  fish ./nbfc.py -o completion/fish/nbfc.fish ';'\
	  bash ./nbfc.py -o completion/bash/nbfc      ';'\
		\
	  zsh  ./tools/argany/nbfc_service.py -o completion/zsh/_nbfc_service      ';'\
	  fish ./tools/argany/nbfc_service.py -o completion/fish/nbfc_service.fish ';'\
	  bash ./tools/argany/nbfc_service.py -o completion/bash/nbfc_service      ';'\
		\
	  zsh  ./tools/argany/ec_probe.py -o completion/zsh/_ec_probe      ';'\
	  fish ./tools/argany/ec_probe.py -o completion/fish/ec_probe.fish ';'\
	  bash ./tools/argany/ec_probe.py -o completion/bash/ec_probe

# =============================================================================
# Documentation ===============================================================
# =============================================================================

doc: .force
	mkdir -p doc
	
	./tools/argany/argany.py \
		markdown ./tools/ec_probe.py     -o doc/ec_probe.md     ';' \
	  markdown ./tools/nbfc_service.py -o doc/nbfc_service.md ';' \
	  markdown nbfc.py                 -o doc/nbfc.md
	
	./tools/config_to_md.py  > doc/nbfc_service.json.md
	
	go-md2man < doc/ec_probe.md          > doc/ec_probe.1
	go-md2man < doc/nbfc.md              > doc/nbfc.1
	go-md2man < doc/nbfc_service.md      > doc/nbfc_service.1
	go-md2man < doc/nbfc_service.json.md > doc/nbfc_service.json.5

.force:
	# force building targets
