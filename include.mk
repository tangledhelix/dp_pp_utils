
IMG=images
ZIPDIR=zipdir
ZIPCACHEDIR=$(ZIPDIR)/$(PROJECT)
BOOKSDIR=ebooks
ILLODIR=illustrations
UTILDIR=$(HOME)/dp/util
PPGEN=$(HOME)/dp/ppgen/ppgen.py

PPGEN_SRC=$(PROJECT)-src.txt
TXT=$(PROJECT)-utf8.txt
HTML=$(PROJECT).html
LAT1TXT=$(PROJECT)-lat1.txt

PGLAF_URL=https://ebookmaker.pglaf.org

# Default book ID, taken from the form at PGLAF's ebookmaker
# Can be overridden at runtime with 'id' parameter
DEFAULT_BOOK_ID = 10001
book_id ?= $(DEFAULT_BOOK_ID)

# App name (for "open" command) for text viewer
TEXTVIEWPROG=Visual Studio Code
# App name (for "open" command) for HTML viewer
HTMLVIEWPROG=Safari

default:
	@echo "make ppgen:     output UTF8 text & HTML files from ppgen source"
	@echo "make ppgend:    run ppgen in debug/verbose mode"
	@echo ""
	@echo "make zip:       create zipfile (PPtools, PPwb, DU, ebookmaker)"
	@echo "make ppv:       create zip file to submit to PPV"
	@echo "make sr:        create zip file to submit to SR (incl. ebooks/)"
	@echo ""
	@echo "make vt:        build UTF8 text version & open for viewing"
	@echo "make vh:        build HTML version & open for viewing"
	@echo "make view:      build UTF8 text and HTML versions, open for viewing"
	@echo ""
	@echo "make clean:     remove built ebooks, zip archives"
	@echo "make ebooks:    create epub files (no .mobi)"
	@echo ""
	@echo "make ebooksget: fetch ebooks from PGLAF epubmaker"
	@echo ""
	@echo "    -- you MUST specify the cache ID"
	@echo "       	  ex: make ebooksget cache=20220507205607"
	@echo ""
	@echo "    -- you MAY specify an ebook ID (default: $(DEFAULT_BOOK_ID))"
	@echo "       	  ex: make ebooksget cache=20220507205607 book_id=1234"

# Basic build commands
# -i <file> : specify input file
# -o <type> : output type : 'h' for html, 'u' for utf8, 'uh' for both
# -img : extra output related to image handling

$(TXT): $(PPGEN_SRC)
	$(UTILDIR)/venv/bin/python3 $(PPGEN) -i $(PPGEN_SRC) -o u

$(HTML): $(PPGEN_SRC)
	$(UTILDIR)/venv/bin/python3 $(PPGEN) -i $(PPGEN_SRC) -o h -img

ppgen: $(TXT) $(HTML)

# More verbose build command
# -std : output to stdout (for debugging)
# -d <level> : debug level  ('a' is all)
# -l : display Latin-1, diacritic, and Greek conversion logs
ppgend:
	$(UTILDIR)/venv/bin/python3 $(PPGEN) -l -d a -std -i $(PPGEN_SRC)

# Build & view text
vt: $(TXT)
	open -a "$(TEXTVIEWPROG)" $(TXT)

# Build & view HTML
vh: $(HTML)
	open -a "$(HTMLVIEWPROG)" $(HTML)

# Build both text & HTML, then view
view: vt vh

# Per PPV, the zip should have files at the root, not contain
# a directory which then contains the files. -April 2022
# PPV should include the .bin files.
ppv: ppgen
	rm -f $(ZIPDIR)/$(PROJECT)-ppv.zip
	rm -rf $(ZIPCACHEDIR)
	mkdir -p $(ZIPCACHEDIR)/$(IMG)/
	cp $(TXT) $(TXT).bin $(HTML) $(HTML).bin $(ZIPCACHEDIR)
	cp -r $(IMG)/ $(ZIPCACHEDIR)/$(IMG)/
	rm -rf $(ZIPCACHEDIR)/$(IMG)/{.DS_Store,*.pxd,*.xcf}
	cd $(ZIPCACHEDIR) && zip -r ../$(PROJECT)-ppv.zip .

# Smooth Readers can also include ebooks. Anything in the ebooks/
# directory will get sucked into this.
sr: ppgen
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
# - Use the 'ppv' target for PPV.

# What to include in a zip file for PG direct upload:
# - a single zip file containing all files
# - do not include any .bin or Thumbs.db files
# - verify there are no restricted permissions on the files or directories

zip: ppgen
	rm -f $(ZIPDIR)/$(PROJECT).zip
	rm -rf $(ZIPCACHEDIR)
	mkdir -p $(ZIPCACHEDIR)/$(IMG)/
	cp $(TXT) $(HTML) $(ZIPCACHEDIR)
	cp -r $(IMG)/ $(ZIPCACHEDIR)/$(IMG)/
	rm -rf $(ZIPCACHEDIR)/$(IMG)/{.DS_Store,*.pxd,*.xcf}
	cd $(ZIPCACHEDIR) && zip -r ../$(PROJECT).zip .

zipclean:
	rm -rf $(ZIPDIR)

pyvenv:
	@if [ ! -d "$(UTILDIR)/venv" ]; \
	then \
		cd $(UTILDIR) && \
		python3 -m venv venv && \
		. venv/bin/activate && \
		pip install -r requirements.txt; \
	fi

ebooksdir:
	mkdir -p $(BOOKSDIR)

ebooks: ppgen ebooksdir pyvenv
	. $(UTILDIR)/venv/bin/activate && \
	$(UTILDIR)/venv/bin/ebookmaker --make=epub --max-depth=3 \
		--output-dir="$(BOOKSDIR)" --title="$(TITLE)" --author="$(AUTHOR)" \
		--input-mediatype="text/plain;charset=utf8" --ebook="`randpin5`" ./$(PROJECT).html

ebooksget: ebooksdir
ifndef cache
	@echo 'Missing param: "cache" not defined'
else
	curl -s --output-dir $(BOOKSDIR) -O $(PGLAF_URL)/cache/$(cache)/output.txt
	curl -s --output-dir $(BOOKSDIR) -O $(PGLAF_URL)/cache/$(cache)/$(book_id)-epub.epub
	curl -s --output-dir $(BOOKSDIR) -O $(PGLAF_URL)/cache/$(cache)/$(book_id)-images-epub.epub
	curl -s --output-dir $(BOOKSDIR) -O $(PGLAF_URL)/cache/$(cache)/$(book_id)-images-epub3.epub
	curl -s --output-dir $(BOOKSDIR) -O $(PGLAF_URL)/cache/$(cache)/$(book_id)-images-kindle.mobi
	curl -s --output-dir $(BOOKSDIR) -O $(PGLAF_URL)/cache/$(cache)/$(book_id)-kf8-kindle.mobi
	@ls -ltr $(BOOKSDIR)
endif

ebooksclean:
	rm -rf $(BOOKSDIR)

clean: zipclean ebooksclean
	rm -f guiguts.log
	rm -f $(PROJECT)*.zip
	rm -f $(HTML) $(HTML).bin
	rm -f $(TXT) $(TXT).bin
	rm -f $(LAT1TXT) $(LAT1TXT).bin
