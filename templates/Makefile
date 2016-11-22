export PATH := {{ kindlegen_dir }}:$(PATH)

PROJECT={{ project_name }}
TITLE={{ title }}
AUTHOR={{ author }}

HOST=dp.tangledhelix.com
DIR=sites/$(HOST)
WEBTARGET=$(HOST):$(DIR)/projects/$(PROJECT)

IMG=images
ZIPDIR=zipdir
ZIPTARG=$(ZIPDIR)/$(PROJECT)
BOOKSDIR=ebooks
ILLODIR=illustrations
README=README

IDX=index.html

TXT=$(PROJECT)-utf8.txt
HTML=$(PROJECT).html

default:
	@echo "make readme:    rebuild README.html file"
	@echo "make web:       upload to my DP preview site"
	@echo "make ebooks:    build epub and kindle files"
	@echo "make ebooksweb: upload ebook files to DP preview site"
	@echo "make sr:        create zip file to submit to SR"
	@echo "make ppv:       create zip file to submit to PPV"
	@echo "make clean:     remove Gimp/Pixelmator files, ebooks, zip archive"

readme: $(README).html

$(README).html: $(README).md
	grip --export --title="Project Notes: $(TITLE)" $(README).md

web: readme
	chmod 0755 $(IMG)/
	chmod 0644 $(IDX) $(TXT) $(HTML)
	find $(IMG) -type f -exec chmod 0644 {} ';'
	scp -q $(IDX) $(TXT) $(HTML) $(README).html $(WEBTARGET)
	rsync -a --delete $(IMG)/ $(WEBTARGET)/$(IMG)/

ebooksweb:
	chmod 0644 $(BOOKSDIR)/*.epub $(BOOKSDIR)/*.mobi
	scp -q $(BOOKSDIR)/$(PROJECT).epub $(BOOKSDIR)/$(PROJECT).mobi $(WEBTARGET)

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
	mkdir -p $(BOOKSDIR)

ebooks: ebooksclean booksdir
	epubmaker --make=epub --output-dir=$(BOOKSDIR) \
		--output-file=$(PROJECT).epub \
		--title="$(TITLE)" \
		--author="$(AUTHOR)" $(HTML)
	epubmaker --make=kindle --output-dir=$(BOOKSDIR) \
		--output-file=$(PROJECT).mobi \
		--title="$(TITLE)" \
		--author="$(AUTHOR)" $(HTML)
	mv "$(BOOKSDIR)/$(TITLE)-epub.epub" "$(BOOKSDIR)/$(PROJECT)-noimages.epub"
	mv "$(BOOKSDIR)/$(TITLE)-images-epub.epub" "$(BOOKSDIR)/$(PROJECT).epub"
	mv "$(BOOKSDIR)/$(TITLE)-kindle.mobi" "$(BOOKSDIR)/$(PROJECT)-noimages.mobi"
	mv "$(BOOKSDIR)/$(TITLE)-images-kindle.mobi" "$(BOOKSDIR)/$(PROJECT).mobi"
	ls -l $(BOOKSDIR)/*.epub $(BOOKSDIR)/*.mobi

illoclean:
	rm -fv $(ILLODIR)/*.xcf
	rm -fv $(ILLODIR)/*.pxm

clean: illoclean zipclean ebooksclean

