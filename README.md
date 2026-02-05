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

### useful fontTools commands

To subset glyphs from a font:

```
pyftsubset SourceFont.ttf --unicodes="U+0000-007F" --output-file=build/SubsetASCII.ttf
```
