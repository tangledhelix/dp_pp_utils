# not addressed yet

## first pass
- check spaces around hyphens
- check spaces before punct `. ! ? ; : ,`
- check spaces around quotes `' "`
- check spaces around `( ) { } [ ]`
- check spaces within abbreviations `A.M. P.M.` etc
- check multiple consecutive spaces outside no-wrap blocks
- check improper thought breaks
- check ellipses
- check for 3 dashes (not 2 or 4)
- check for spaces around em or long dashes
- check adjacent letters & numbers to find `6O` or `I5`
- search `\n\n\n` to find chapter & section spacing to check them

## other
- how to tag lang like `<i lang="foo">` ?
- Avoid use of `px` in CSS; use `em` or `%`
- Avoid using `<br>` and `&nbsp;` to indent or separate text. Use CSS margins and padding.
- is it covered to use h1 for heading and ONCE ONLY
- h2 chapter; h3 section; does guiguts do this on its own?
- page break before each new chapter, and `<div class="chapter">` at chapter break for e-readers. See [Easy Epub][].
- is possible to include Greek in a `<span>` with `title` attribute to help reader to know how it's pronounced (via transliteration).

[easy epub]: https://www.pgdp.net/wiki/DP_Official_Documentation:PP_and_PPV/Easy_Epub/Headings

## toward end of process
- transcriber's notes
- and links from TN back to correction locations 

TN note from wiki

```
- Apparent typographical errors have been changed
- Italics denoted by underscores (or preferred method)
- Bold denoted by equals signs (or preferred method)
- Small capitals changed to all capitals (or preferred method)
- Illustrations have been positioned near the relevant text
- The page scans of the original publication were poor so
    1. guesses for some words had to be made
    2. illustrations have been processed to the best ability of the transcribers
```

page on quote marks:
https://www.pgdp.net/wiki/Quotation_Mark_and_Apostrophe_Entities
