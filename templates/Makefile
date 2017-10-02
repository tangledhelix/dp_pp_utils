export PATH := {{ kindlegen_dir }}:$(PATH)

PROJECT={{ project_name }}
TITLE={{ title }}
AUTHOR={{ author }}

IMG=images
ZIPDIR=zipdir
ZIPTARG=$(ZIPDIR)/$(PROJECT)
BOOKSDIR=ebooks
ILLODIR=illustrations

TXT=$(PROJECT)-utf8.txt
HTML=$(PROJECT).html

default:
	@echo "make ebooks:    build epub and kindle files"
	@echo "make sr:        create zip file to submit to SR"
	@echo "make ppv:       create zip file to submit to PPV"
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

ebooksclean:
	rm -rf $(BOOKSDIR)

booksdir:
	mkdir -p $(BOOKSDIR)/out

ebooks: ebooksclean booksdir
	epubmaker --make=epub --output-dir=$(BOOKSDIR) \
		--output-file=$(PROJECT).epub \
		--title="$(TITLE)" \
		--author="$(AUTHOR)" $(HTML)
	epubmaker --make=kindle --output-dir=$(BOOKSDIR) \
		--output-file=$(PROJECT).mobi \
		--title="$(TITLE)" \
		--author="$(AUTHOR)" $(HTML)
	mv $(BOOKSDIR)/*-images-epub.epub $(BOOKSDIR)/out/$(PROJECT).epub
	mv $(BOOKSDIR)/*-epub.epub $(BOOKSDIR)/out/$(PROJECT)-noimages.epub
	mv $(BOOKSDIR)/*-images-kindle.mobi $(BOOKSDIR)/out/$(PROJECT).mobi
	mv $(BOOKSDIR)/*-kindle.mobi $(BOOKSDIR)/out/$(PROJECT)-noimages.mobi
	mv $(BOOKSDIR)/out/* $(BOOKSDIR)
	ls -l $(BOOKSDIR)/*.epub $(BOOKSDIR)/*.mobi

illoclean:
	rm -fv $(ILLODIR)/*.xcf
	rm -fv $(ILLODIR)/*.pxm

clean: illoclean zipclean ebooksclean
