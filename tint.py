#!/usr/bin/env python3
from fontTools.ttLib import TTFont, newTable
from fontTools.ttLib.tables import otTables
from fontTools.ttLib.tables.C_P_A_L_ import Color

def make_color_font(input_path, output_path, palette_map, font_name=None):
    font = TTFont(input_path)
    glyph_order = font.getGlyphOrder()
    hmtx = font['hmtx']
    cmap = font.getBestCmap()

    if 'CPAL' not in font:
        font['CPAL'] = newTable('CPAL')
    cpal = font['CPAL']
    cpal.version = 0
    cpal.palettes = [list(palette_map.values())]
    cpal.numPaletteEntries = len(palette_map)

    if 'COLR' not in font:
        font['COLR'] = newTable('COLR')
    colr = font['COLR']
    colr.version = 0
    color_layers = {}
    for idx, chars in enumerate(palette_map.keys()):
        for char in set(chars.lower()+chars.upper()):
            if (name := cmap.get(ord(char))) in glyph_order:
                layer = otTables.LayerRecord()
                layer.name, layer.colorID = name, idx
                color_layers[name] = [layer]
    colr.ColorLayers = color_layers

    if font_name is not None:
        name_ids = {
            1: font_name,
            4: font_name,
            6: font_name.replace(" ", "")
        }

        for record in font['name'].names:
            if (name := name_ids.get(record.nameID)) is not None:
                record.string = name.encode(record.getEncoding())

    font.save(output_path)

def read_palette_map(file):
    palette_map = {}
    with open(file) as f:
        for line in f:
            text, color = line.rstrip().split("\t")
            if not color.startswith("#"):
                raise ValueError("Color must be in hex format, starting with #")
            color = color[1:]
            r = int(color[4:6], 16)
            g = int(color[2:4], 16)
            b = int(color[0:2], 16)
            palette_map[text] = Color(r, g, b, 0xFF)
    return palette_map

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Create a color font based on an existing font.")
    parser.add_argument("input", help="Path to the input font file")
    parser.add_argument("output", help="Path to the output font file")
    parser.add_argument("--palette-map", default="nucl", help="Palette map to use")
    parser.add_argument("--font-name", default=None, help="Family name of the font")
    args = parser.parse_args()
    palette_map = read_palette_map(args.palette_map)
    make_color_font(args.input, args.output, palette_map, args.font_name)
