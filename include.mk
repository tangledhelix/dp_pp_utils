
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

PGLAF_URL=https://ebookmaker.pglaf.org

default:
	@echo "make ppgen:     output text & html files from ppgen source"
	@echo "make ppgend:    run ppgen in debug/verbose mode"
	@echo "make zip:       create zipfile (PPtools, PPwb, DU, ebookmaker)"
	@echo "make ppv:       create zip file to submit to PPV"
	@echo "make ebooks:    create epub files (no .mobi)"
	@echo "make ebooksget: fetch ebooks from PGLAF epubmaker"
	@echo "       you must specify the cache ID and ebook ID"
	@echo "       ex: make cache=20220507205607 id=22349 ebooksget"
	@echo "make clean:     remove built ebooks, zip archives"

# Basic build command
# -i <file> : specify input file
ppgen:
	$(UTILDIR)/venv/bin/python3 $(PPGEN) -i $(PPGEN_SRC)

# More verbose build command
# -std : output to stdout (for debugging)
# -d <level> : debug level  ('a' is all)
# -l : display Latin-1, diacritic, and Greek conversion logs
ppgend:
	$(UTILDIR)/venv/bin/python3 $(PPGEN) -l -d a -std -i $(PPGEN_SRC)

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
ifndef id
	@echo 'Missing param: "id" not defined'
else ifndef cache
	@echo 'Missing param: "cache" not defined'
else
	curl -s --output-dir $(BOOKSDIR) -O $(PGLAF_URL)/cache/$(cache)/$(id)-images-epub.epub
	curl -s --output-dir $(BOOKSDIR) -O $(PGLAF_URL)/cache/$(cache)/$(id)-images-kindle.mobi
	@ls -l $(BOOKSDIR)/$(id)-images*
endif

ebooksclean:
	rm -rf $(BOOKSDIR)

clean: zipclean ebooksclean

