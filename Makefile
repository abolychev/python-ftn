RST2HTML=rst2html.py
STYLESHEET=--stylesheet http://projects.oddbit.com/css/lsr.css --link-stylesheet

RSTDOCS=$(wildcard *.rst)
HTMLDOCS=$(RSTDOCS:.rst=.html)

%.html: %.rst
	$(RST2HTML) $(STYLESHEET) $< $@

all: $(HTMLDOCS)

deploy: all
	git checkout gh-pages
	git add $(HTMLDOCS)
	git ci -m 'Page rendering via Makefile'
	@echo git push origin gh-pages

clean:
	rm -f $(HTMLDOCS)

