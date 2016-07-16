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

IDX=index.html
ORIG=projectID{{ project_id }}.txt

TXT=$(PROJECT)-utf8.txt
HTML=$(PROJECT).html

default:
	@echo "make web:    upload to my DP preview site"
	@echo "make zip:    create zip file to submit to PPV"
	@echo "make epub:   build epub files"
	@echo "make kindle: build kindle files"
	@echo "make ebooks: build both epub and kindle files"

web:
	chmod 0755 $(IMG)/
	chmod 0644 $(IDX) $(TXT) $(HTML) $(IMG)/*
	scp -q $(ORIG) $(IDX) $(TXT) $(HTML) $(WEBTARGET)
	rsync -a --delete $(IMG)/ $(WEBTARGET)/$(IMG)/

zip:
	rm -rf $(ZIPDIR) $(PROJECT).zip
	mkdir -p $(ZIPTARG)
	cp $(TXT) $(ZIPTARG)/$(PROJECT)-utf8.txt
	cp $(TXT).bin $(ZIPTARG)/$(PROJECT)-utf8.txt.bin
	cp $(HTML) $(ZIPTARG)/$(PROJECT).html
	cp $(HTML).bin $(ZIPTARG)/$(PROJECT).html.bin
	mkdir -p $(ZIPTARG)/$(IMG)/
	cp -r $(IMG)/ $(ZIPTARG)/$(IMG)/
	rm -f $(ZIPTARG)/$(IMG)/.DS_Store
	cd $(ZIPDIR) && zip -r $(PROJECT).zip $(PROJECT)

booksdir:
	mkdir -p $(BOOKSDIR)

epub: booksdir
	rm -f $(BOOKSDIR)/*.epub
	epubmaker --make=epub --output-dir=$(BOOKSDIR) \
		--output-file=$(PROJECT).epub \
		--title="$(TITLE)" \
		--author="$(AUTHOR)" $(HTML)
	ls -l $(BOOKSDIR)/*.epub

kindle: booksdir
	rm -f $(BOOKSDIR)/*.mobi
	epubmaker --make=kindle --output-dir=$(BOOKSDIR) \
		--output-file=$(PROJECT).mobi \
		--title="$(TITLE)" \
		--author="$(AUTHOR)" $(HTML)
	ls -l $(BOOKSDIR)/*.mobi

ebooks: epub kindle

