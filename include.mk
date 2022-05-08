
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

default:
	@echo "make ppgen:     output text & html files from ppgen source"
	@echo "make zip:       create zip file for pptools / ppwb"
	@echo "make ppv:       create zip file to submit to PPV"
	@echo "make pg:        create zip file to upload to PG"
	@echo "make ebooks:    create epub files"
	@echo "make ebookzip:  create zip file to upload to ebookmaker"
	@echo "make clean:     remove Gimp/Pixelmator files, ebooks, zip archive"

# Per PPV, the zip should have files at the root, not contain
# a directory which then contains the files. -April 2022
ppv:
	rm -rf $(ZIPCACHEDIR)
	mkdir -p $(ZIPCACHEDIR)
	cp $(TXT) $(TXT).bin $(HTML) $(HTML).bin $(ZIPCACHEDIR)
	mkdir -p $(ZIPCACHEDIR)/$(IMG)/
	cp -r $(IMG)/ $(ZIPCACHEDIR)/$(IMG)/
	rm -f $(ZIPCACHEDIR)/$(IMG)/.DS_Store
	rm -rf $(ZIPCACHEDIR)/$(IMG)/*.pxd
	cd $(ZIPCACHEDIR) && zip -r ../$(PROJECT)-ppv.zip .

# What to include in a zip file for PG direct upload:
# - a single zip file containing all files
# - do not include any .bin or Thumbs.db files
# - verify there are no restricted permissions on the files or directories
pg:
	rm -rf $(ZIPCACHEDIR)
	mkdir -p $(ZIPCACHEDIR)
	cp $(TXT) $(HTML) $(ZIPCACHEDIR)
	mkdir -p $(ZIPCACHEDIR)/$(IMG)/
	cp -r $(IMG)/ $(ZIPCACHEDIR)/$(IMG)/
	rm -f $(ZIPCACHEDIR)/$(IMG)/.DS_Store
	rm -rf $(ZIPCACHEDIR)/$(IMG)/*.pxd
	cd $(ZIPCACHEDIR) && zip -r ../$(PROJECT)-upload.zip .

zip:
	rm -rf $(ZIPCACHEDIR)
	mkdir -p $(ZIPCACHEDIR)
	cp $(HTML) $(ZIPCACHEDIR)
	mkdir -p $(ZIPCACHEDIR)/$(IMG)/
	cp -r $(IMG)/ $(ZIPCACHEDIR)/$(IMG)/
	rm -f $(ZIPCACHEDIR)/$(IMG)/.DS_Store
	rm -rf $(ZIPCACHEDIR)/$(IMG)/*.pxd
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

ebooks: ebooksdir pyvenv
	. $(UTILDIR)/venv/bin/activate && \
	$(UTILDIR)/venv/bin/ebookmaker --make=epub --max-depth=3 \
		--output-dir="$(BOOKSDIR)" --title="$(TITLE)" --author="$(AUTHOR)" \
		--input-mediatype="text/plain;charset=utf8" --ebook="`randpin5`" ./$(PROJECT).html

# /Applications/Kindle\ Previewer\ 3.app/Contents/lib/fc/bin/kindlegen ../$(PROJECT).html -o $(PROJECT).mobi
#mv $(PROJECT).mobi $(BOOKSDIR)

ebookzip:
	zip $(PROJECT).zip $(PROJECT).html images/*.{png,jpg}

ebooksclean:
	rm -rf $(BOOKSDIR)

illoclean:
	rm -fv $(ILLODIR)/*.xcf
	rm -fv $(ILLODIR)/*.pxm

clean: zipclean ebooksclean

ppgen:
	. $(UTILDIR)/venv/bin/activate && python3 $(PPGEN) -l -d a -std -i $(PPGEN_SRC)

