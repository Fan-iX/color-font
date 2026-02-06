Scripts to play with fonts

## Requirements

- [fontTools](https://github.com/fonttools/fonttools), tested in v4.61.1

## tint.py - Create Colored Fonts

usage:

```bash
python3 tint.py <input.ttf> <output.ttf> --palette-map <color_map.tsv>
# e.g.
python3 tint.py /path/to/SourceFont.ttf build/Font.ttf --palette-map rainbow.map
```

The color map should be a arbitrary-column tsv file, with first column being hex color codes, and the rest columns being characters to be colored with the corresponding color.

e.g. `rainbow.map`:

```
#F8766D	A	a
#EE8043	B	b
#E18A00	C	c
#D19300	D	d
...
```

Multiple characters in one column will be combined into ligatures.

## scriptify.py - Add simple TeX style super/subscript

usage:

```bash
python3 scriptify.py <input.ttf> <output.ttf> --unicodes="U+xxxx-xxxx"
# e.g.
python3 scriptify.py /path/to/SourceFont.ttf build/Font.ttf --unicodes="U+0020-007E" # build super/subscript for ASCII chars
```

To use the super/subscript glyphs, type `_{char}` for subscript, and `^{char}` for superscript.

e.g. `H_2SO_4^{2+}` will render as H₂SO₄²⁺

### utils

To subset glyphs from a font: (requires `fonttools`)

```
pyftsubset SourceFont.ttf --unicodes="U+0000-007F" --output-file=build/SubsetASCII.ttf
```

To adjust luminance of a palette: (requires `colorspacious`)

```
python3 remap-palette.py light-theme.map --l-from 0 0.7 --l-to 0.3 1 > dark-theme.map
```
