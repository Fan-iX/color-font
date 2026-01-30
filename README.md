A recipe to create [colored fonts](https://fonts.google.com/knowledge/introducing_type/introducing_color_fonts) from an existing font

## Requirements

- [fontTools](https://github.com/fonttools/fonttools) v4.61.1

## Usage

First, prepare a two-column tsv with characters and corresponding colors. The first column may contain multiple characters.

e.g. `rainbow.map`:

```
Aa	#F8766D
Bb	#EE8043
Cc	#E18A00
Dd	#D19300
...
```

then run

```
./tint.py source_font.ttf out_font.ttf --palette-map rainbow.map
```

<hr>

Or, using the provided `Makefile`:

```
make PALETTE_MAP=rainbow.map TEMPLATE_FONT=your_font.ttf
```

output will be created at `build/Font.ttf`. You can preview it in `preview.html` with a supporting browser (e.g. Chrome).

#### `make` options

```
PALETTE_MAP    color mapping file
TEMPLATE_FONT  source font file
# metadata
FONT_NAME      family name of the font [ optional ]
# output
BUILD_DIR      working directory [ default: build/ ]
```
