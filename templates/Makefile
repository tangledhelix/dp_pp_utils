
PROJECT={{ project_name }}
TITLE={{ title }}
AUTHOR={{ author }}

IMG=images
ZIPDIR=zipdir
ZIPTARG=$(ZIPDIR)/$(PROJECT)
BOOKSDIR=ebooks
ILLODIR=illustrations
UTILDIR=$(HOME)/dp/util

TXT=$(PROJECT)-utf8.txt
HTML=$(PROJECT).html

default:
	@echo "make ebooks:    build epub and kindle files"
	@echo "make sr:        create zip file to submit to SR"
	@echo "make ppv:       create zip file to submit to PPV"
	@echo "make ebookzip:  create zip file to upload to ebookmaker"
	@echo "make clean:     remove Gimp/Pixelmator files, ebooks, zip archive"

sr: zipclean zipdir
	cp $(TXT) $(ZIPTARG)
	cp smooth-reading.txt $(ZIPTARG)/README.txt
	cd $(ZIPDIR) && zip -r $(PROJECT)-sr.zip $(PROJECT)

ppv: zipclean zipdir
	cp $(TXT) $(TXT).bin $(HTML) $(HTML).bin $(ZIPTARG)
	mkdir -p $(ZIPTARG)/$(IMG)/
	cp -r $(IMG)/ $(ZIPTARG)/$(IMG)/
	rm -f $(ZIPTARG)/$(IMG)/.DS_Store
	cd $(ZIPDIR) && zip -r $(PROJECT).zip $(PROJECT)

zipdir:
	mkdir -p $(ZIPTARG)

zipclean:
	rm -rf $(ZIPDIR)

pyvenv:
	cd $(UTILDIR) && python3 -m venv venv && . venv/bin/activate && pip install -r requirements.txt

ebooksdir:
	mkdir -p $(BOOKSDIR)

ebooks: ebooksdir pyvenv
	. $(UTILDIR)/venv/bin/activate && $(UTILDIR)/venv/bin/ebookmaker --make=epub --max-depth=3 --output-dir="$(BOOKSDIR)" --title="$(TITLE)" --author="$(AUTHOR)" --input-mediatype="text/plain;charset=utf8" --ebook="10001" ./$(PROJECT).html

# /Applications/Kindle\ Previewer\ 3.app/Contents/lib/fc/bin/kindlegen ../$(PROJECT).html -o $(PROJECT).mobi
	mv $(PROJECT).mobi $(BOOKSDIR)

ebookzip:
	zip $(PROJECT).zip $(PROJECT).html images/*.{png,jpg}

ebooksclean:
	rm -f $(BOOKSDIR)

illoclean:
	rm -fv $(ILLODIR)/*.xcf
	rm -fv $(ILLODIR)/*.pxm

clean: illoclean zipclean ebooksclean
