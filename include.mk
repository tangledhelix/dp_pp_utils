
IMG=images
ZIPDIR=zipdir
ZIPCACHEDIR=$(ZIPDIR)/$(PROJECT)
BOOKSDIR=ebooks

TXT=$(PROJECT)-utf8.txt
HTML=$(PROJECT).html

# legacy
PPGEN_SRC=$(PROJECT)-src.txt
PPGEN=$(HOME)/dp/ppgen/ppgen.py
PPGEN_PY=python3.11

EBOOKMAKER_URL=https://ebookmaker.pglaf.org

# Default book ID, taken from the form at PGLAF's ebookmaker
# Can be overridden at runtime with 'id' parameter
DEFAULT_BOOK_ID = 10001
book_id ?= $(DEFAULT_BOOK_ID)

# App name (for "open" command) for text viewer
TEXTVIEWPROG=Visual Studio Code
# App name (for "open" command) for HTML viewer
HTMLVIEWPROG=Safari

default:
	@echo "make zip:   create zipfile (PPtools, PPwb, DU, ebookmaker)"
	@echo "make sr:    create zip file to submit to SR (incl. ebooks/)"
	@echo ""
	@echo "make vt:    open UTF8 text file in viewer"
	@echo "make vh:    open HTML file in viewer"
	@echo "make view:  open both UTF8 text and HTML versions in viewers"
	@echo "make serve: start a python3 web server on port 8000"
	@echo "                (handy for e.g. iPhone Simulator on Mac)"
	@echo ""
	@echo "make ebooksget: fetch ebooks from PGLAF ebookmaker"
	@echo ""
	@echo "    -- you MUST specify the cache ID"
	@echo "       	  ex: make ebooksget cache=20220507205607"
	@echo ""
	@echo "    -- you MAY specify an ebook ID (default: $(DEFAULT_BOOK_ID))"
	@echo "       	  ex: make ebooksget cache=20220507205607 book_id=1234"
	@echo ""
	@echo "make legacy: show list of legacy make targets"

legacy:
	@echo "These legacy targets are included for backward compatibility"
	@echo "with ppgen, or else as examples."
	@echo ""
	@echo "make ppv:    create zip file to submit to PPV"
	@echo "make ppgen:  output UTF8 text & HTML files from ppgen source"

# View text
vt:
	open -a "$(TEXTVIEWPROG)" $(TXT)

# View HTML
vh:
	open -a "$(HTMLVIEWPROG)" $(HTML)

# View both text & HTML files
view: vt vh

# Start a Python3 web server on localhost:8000.
#
# This can be useful when you want to use a viewer such as the
# iPhone Simulator, which can speak to the network, but can't
# access the Mac filesystem. It may be useful for simulators
# on other platforms as well.
serve:
	@echo ""
	@echo "    **************************************************"
	@echo "    ***  Starting server on http://localhost:8000  ***"
	@echo "    ***  Press Ctrl-C to terminate.                ***"
	@echo "    **************************************************"
	@echo ""
	python3 -m http.server

# Smooth Readers can also include ebooks. Anything in the ebooks/
# directory will get sucked into this.
sr:
	rm -f $(ZIPDIR)/$(PROJECT)-sr.zip
	rm -rf $(ZIPCACHEDIR)
	mkdir -p $(ZIPCACHEDIR)/$(IMG)/
	cp $(TXT) $(HTML) $(ZIPCACHEDIR)
	cp -r $(IMG)/ $(ZIPCACHEDIR)/$(IMG)/
	rm -rf $(ZIPCACHEDIR)/$(IMG)/{.DS_Store,*.pxd,*.xcf}
	cp -r $(BOOKSDIR)/ $(ZIPCACHEDIR)/
	rm -f $(ZIPCACHEDIR)/{.DS_Store,output.txt}
	cd $(ZIPCACHEDIR) && zip -r ../$(PROJECT)-sr.zip .

# Zip file suitable for:
# - PP workbench
# - PPtools
# - ebookmaker online
# - Direct Upload

# What to include in a zip file for PG direct upload:
# - a single zip file containing all files
# - do not include any .bin or Thumbs.db files
# - verify there are no restricted permissions on the files or directories

zip:
	rm -f $(ZIPDIR)/$(PROJECT).zip
	rm -rf $(ZIPCACHEDIR)
	mkdir -p $(ZIPCACHEDIR)/$(IMG)/
	cp $(TXT) $(HTML) $(ZIPCACHEDIR)
	cp -r $(IMG)/ $(ZIPCACHEDIR)/$(IMG)/
	rm -rf $(ZIPCACHEDIR)/$(IMG)/{.DS_Store,*.pxd,*.xcf}
	cd $(ZIPCACHEDIR) && zip -r ../$(PROJECT).zip .

ebooksdir:
	mkdir -p $(BOOKSDIR)

ebooksget: ebooksdir
ifndef cache
	@echo 'Missing param: "cache" not defined'
else
	curl -s -o $(BOOKSDIR)/output.txt                   $(EBOOKMAKER_URL)/cache/$(cache)/output.txt
	curl -s -o $(BOOKSDIR)/$(PROJECT)-images.mobi       $(EBOOKMAKER_URL)/cache/$(cache)/$(book_id)-images.mobi
	curl -s -o $(BOOKSDIR)/$(PROJECT)-epub.epub         $(EBOOKMAKER_URL)/cache/$(cache)/$(book_id)-epub.epub
	curl -s -o $(BOOKSDIR)/$(PROJECT)-images-epub.epub  $(EBOOKMAKER_URL)/cache/$(cache)/$(book_id)-images-epub.epub
	curl -s -o $(BOOKSDIR)/$(PROJECT)-images-epub3.epub $(EBOOKMAKER_URL)/cache/$(cache)/$(book_id)-images-epub3.epub
	cp         $(BOOKSDIR)/$(PROJECT)-images-epub3.epub $(BOOKSDIR)/$(PROJECT)-images-epub3_renamed.kepub.epub
	kepubify --output "$(BOOKSDIR)/" $(BOOKSDIR)/$(PROJECT)-images-epub3.epub
	@ls -ltr $(BOOKSDIR)
endif

# Per PPV, the zip should have files at the root, not contain
# a directory which then contains the files. -April 2022
# PPV should include the .bin files.
ppv:
	rm -f $(ZIPDIR)/$(PROJECT)-ppv.zip
	rm -rf $(ZIPCACHEDIR)
	mkdir -p $(ZIPCACHEDIR)/$(IMG)/
	cp $(TXT) $(TXT).bin $(HTML) $(HTML).bin $(ZIPCACHEDIR)
	cp -r $(IMG)/ $(ZIPCACHEDIR)/$(IMG)/
	rm -rf $(ZIPCACHEDIR)/$(IMG)/{.DS_Store,*.pxd,*.xcf}
	cd $(ZIPCACHEDIR) && zip -r ../$(PROJECT)-ppv.zip .

$(TXT): $(PPGEN_SRC)
	$(PPGEN_PY) $(PPGEN) -i $(PPGEN_SRC) -o u

$(HTML): $(PPGEN_SRC)
	$(PPGEN_PY) $(PPGEN) -i $(PPGEN_SRC) -o h -img

ppgen: $(TXT) $(HTML)
