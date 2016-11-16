#!/bin/bash
#
# TODO: the homebrew perl stuff exploded after I did an upgrade. Going to use
# perlbrew.pl instead. Using 5.24.0. I did NOT update the below instructions to
# match that, it still assumes homebrew perl.
#
# Process to install that way:
# \curl -L https://install.perlbrew.pl | bash
# perlbrew install perl-5.24.0
# perlbrew switch perl-5.24.0
# perlbrew install-cpanm
#
#apt: cpanminus
#
# cpanm Bundle::LWP             ubuntu:libwww-perl
# cpanm --force Tk              ubuntu:perl-tk
# cpanm Tk::CursorControl
# cpanm Tk::ToolBar
# cpanm Module::Build::Compat
# cpanm Image::Size
# cpanm Text::LevenshteinXS
#
# TODO: if later stuff requires a compiler, tell the user at the start to
# install xcode from the app store. Can that be started programmatically?
#
# TODO: if brew isn't installed, install it. Ask first. Make sure it won't
# destroy an existing /usr/local either.

# docker run:
# docker run --rm -it --name firefox -e DISPLAY=$ip:0 -v /tmp/.X11-unix:/tmp/.X11-unix
#   -v /Users/dan/dp:/dp jess/firefox

LOG="$(pwd)/homebrew.log"
GGHOME="$HOME/dp/guiguts"

export PATH="/usr/local/bin:$PATH"

function logit() {
    echo "==> $@" | tee -a $LOG
}

function perlinstall() {
    _force=""
    if [[ $1 = "--force" ]]; then
        _force="$1"
        shift
    fi

    _module="$1"
    _testpath="$2"

    if [[ -f $_testpath ]]; then
        logit "Perl $_module: already installed"
    else
        logit "Perl $_module: INSTALLING..."
        cpanm $_force $_module >> $LOG
    fi

    perl -M$_module -e 0
    if [[ $? -eq 0 ]]; then
        logit "Perl $_module: Loads OK"
    else
        logit "Error: can't load Perl module $_module"
        exit
    fi
}

function makedir() {
    if [[ -d "$1" ]]; then
        logit "Found $1/"
    else
        echo "$1/ does not exist."
        printf "Create it? [y/n] "
        read yn
        while [[ "$yn" != "y" && "$yn" != "n" ]]; do
            printf "Please answer 'y' or 'n': "
            read yn
        done
        if [[ "$yn" = "y" ]]; then
            logit "Creating $1"
            mkdir -p $1
        fi
    fi
}

rm -f $LOG
touch $LOG
logit "Logging to $LOG"

# Get up to date
logit "Updating homebrew index"
brew update >> $LOG

# install X11 (XQuartz)
if [[ -d /Applications/Utilities/XQuartz.app ]]; then
    logit "XQuartz: already installed"
else
    logit "XQuartz: INSTALLING..."
    brew cask install xquartz >> $LOG
fi

# Install homebrew perl
# 5.24.0 as of this writing
if [[ -f /usr/local/bin/perl ]]; then
    logit "Homebrew Perl: already installed"
else
    logit "Homebrew Perl: INSTALLING..."
    brew install perl >> $LOG
fi

eval `perl -V:version`
PERL_VERSION="$version"
eval `perl -V:archname`
PERL_ARCH="$archname"

PERL_LIBBASE="/usr/local/Cellar/perl/$PERL_VERSION/lib/site_perl/$PERL_VERSION"
PERL_ARCHBASE="$PERL_LIBBASE/$PERL_ARCH"

if [[ -f /usr/local/bin/cpanm ]]; then
    logit "cpanminus: already installed"
else
    logit "cpanminus: INSTALLING..."
    brew install cpanminus >> $LOG
fi

perlinstall Bundle::LWP "$PERL_LIBBASE/LWP.pm"
perlinstall --force Tk "$PERL_ARCHBASE/Tk.pm"
perlinstall Tk::CursorControl "$PERL_ARCHBASE/Tk/CursorControl.pm"
perlinstall Tk::ToolBar "$PERL_ARCHBASE/Tk/ToolBar.pm"
perlinstall Module::Build::Compat "$PERL_LIBBASE/Module/Build/Compat.pm"
perlinstall Image::Size "$PERL_LIBBASE/Image/Size.pm"
perlinstall Text::LevenshteinXS "$PERL_ARCHBASE/Text/LevenshteinXS.pm"

makedir "$HOME/dp"
makedir "$HOME/dp/pp"
makedir "$GGHOME"

## TODO: install guiguts. Can this be scripted? I didn't script it.
## Basically download it and unzip it in ~/dp or whatever..
## This may be perfect for a homebrew tap.

if [[ -f "$GGHOME/guiguts.pl" ]]; then
    logit "Found guiguts"
else
    logit "guiguts.pl not found"
    logit "Installing guiguts to $GGHOME"
    curl -o $GGHOME/guiguts-1.0.25.zip -L \
        "http://downloads.sourceforge.net/project/guiguts/guiguts/guiguts-1.0.25/guiguts-1.0.25.zip?r=https%3A%2F%2Fsourceforge.net%2Fprojects%2Fguiguts%2F&ts=1465012586&use_mirror=jaist"
    OLDCWD=$(pwd)
    cd $GGHOME
    unzip $OLDCWD/guiguts-1.0.25.zip
    cd $OLDCWD
fi

## TODO: replaced this... see guiguts/launchimage.{sh,scpt}
### but that doesn't really work right.

if [[ -f "$GGHOME/launchimage.sh" ]]; then
    logit "Found launchimage.sh"
else
    logit "Creating launchimage.sh"
    echo "#!/bin/sh" > $GGHOME/launchimage.sh
    # NOTE: open -g is supposed to not bring the app to fg, but
    #       seems like it doesn't honor that.
    echo "open -a Preview \"\$@\"" >> $GGHOME/launchimage.sh
    echo "sleep 0.25" >> $GGHOME/launchimage.sh
    echo "osascript -e 'tell app \"XQuartz\" to activate'" >> $GGHOME/launchimage.sh
    chmod 755 $GGHOME/launchimage.sh
fi

if [[ -f "/usr/local/bin/aspell" ]]; then
    logit "Found aspell"
else
    logit "aspell: INSTALL [en, es, fr, it, de]..."
    brew install \
        --with-lang-en \
        --with-lang-es \
        --with-lang-fr \
        --with-lang-it \
        --with-lang-de \
        aspell >> $LOG
fi

if [[ -f "/usr/local/bin/tidy" ]]; then
    logit "Found tidy"
else
    logit "tidy: INSTALL..."
    brew install tidy-html5 >> $LOG
fi

makedir $GGHOME/jeebies
if [[ -f "$GGHOME/jeebies/jeebies" ]]; then
    logit "Found jeebies"
else
    logit "jeebies: INSTALL..."
    OLDCWD=$(pwd)
    cd $GGHOME/jeebies
    curl -o jeebies.zip -L "http://pglaf.org/~jtinsley/gutcheck/jeebies.zip" >> $LOG 2>&1
    unzip jeebies.zip >> $LOG
    gcc -o jeebies jeebies.c >> $LOG 2>&1
    cd $OLDCWD
fi

## TODO: script adding dpcustommono2 font to X11?

## TODO: script setup of guiguts with file paths??

if [[ -f "$GGHOME/ppgen/ppgen.py" ]]; then
    logit "Found ppgen"
else
    logit "ppgen: INSTALL..."
    OLDCWD=$(pwd)
    cd $GGHOME
    git clone https://github.com/wf49670/ppgen.git >> $LOG
    cd $OLDCWD
fi

## TODO: script setup of epubmaker
##
## brew install groff
## pip install lxml
## pip install cssutils
## pip install Pillow
## pip install docutils
## pip install roman
## pip install epubmaker
##
## to test: epubmaker --help

logit "Done!"
