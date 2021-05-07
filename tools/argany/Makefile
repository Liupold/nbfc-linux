build: test

install: build
	mkdir -p $(DESTDIR)/usr/bin
	mkdir -p $(DESTDIR)/usr/share/zsh/site-functions
	mkdir -p $(DESTDIR)/usr/share/bash-completion/completions
	mkdir -p $(DESTDIR)/usr/share/fish/completions
	cp argany-test.py              $(DESTDIR)/usr/bin/argany-test
	cp test/argany-test.zsh        $(DESTDIR)/usr/share/zsh/site-functions/_argany-test
	cp test/argany-test.bash       $(DESTDIR)/usr/share/bash-completion/completions/argany-test
	cp test/argany-test.fish       $(DESTDIR)/usr/share/fish/completions/argany-test.fish

uninstall:
	rm -f $(DESTDIR)/usr/bin/argany-test
	rm -f $(DESTDIR)/usr/share/zsh/site-functions/_argany-test
	rm -f $(DESTDIR)/usr/share/bash-completion/completions/argany-test
	rm -f $(DESTDIR)/usr/share/fish/completions/argany-test.fish

clean:
	rm -rf test

test: ./argany.py bash.py fish.py zsh.py
	mkdir -p test
	./argany.py \
	zsh  argany-test.py  -o test/argany-test.zsh ';' \
	bash argany-test.py -o test/argany-test.bash ';' \
	fish argany-test.py -o test/argany-test.fish ';'
