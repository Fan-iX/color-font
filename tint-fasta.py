#!/usr/bin/env python3
from fontTools.ttLib import TTFont, newTable
from fontTools.ttLib.tables import otTables
from fontTools.ttLib.tables.C_P_A_L_ import Color
from fontTools.ttLib.tables._g_l_y_f import Glyph, GlyphComponent
from fontTools.feaLib.builder import addOpenTypeFeatures
import io


def font_set_color(font, palette, glyph_names):
    if "CPAL" not in font:
        font["CPAL"] = newTable("CPAL")
    cpal = font["CPAL"]
    cpal.version = 0
    cpal.palettes = [palette]
    cpal.numPaletteEntries = len(palette)

    if "COLR" not in font:
        font["COLR"] = newTable("COLR")
    colr = font["COLR"]
    colr.version = 0
    color_layers = {}

    for idx, names in enumerate(glyph_names):
        for name in names:
            layer = otTables.LayerRecord()
            layer.name, layer.colorID = name, idx
            color_layers[name] = [layer]
    colr.ColorLayers = color_layers

def font_add_glyph(font, glyph_names):
    glyf, hmtx = font["glyf"], font["hmtx"]
    gord, cmap = font.getGlyphOrder(), font.getBestCmap()
    gset = font.getGlyphSet()
    upm = font["head"].unitsPerEm

    def register_glyph(name, glyph_obj, width, lsb):
        glyf[name] = glyph_obj
        hmtx[name] = (width, lsb)
        if name not in gord:
            gord.append(name)

    def register_clone(name, base_glyph):
        comp_glyph = Glyph()
        comp_glyph.numberOfContours = -1
        comp = GlyphComponent()
        comp.glyphName, comp.x, comp.y = base_glyph, 0, 0
        comp.flags = 0x206
        comp_glyph.components = [comp]
        return register_glyph(name, comp_glyph, hmtx[base_glyph][0], 0)

    for gname in glyph_names:
        register_clone(f"{gname}.plain", gname)

    font.setGlyphOrder(gord)


def font_set_liga(font, plain_glyphs):
    cmap = font.getBestCmap()

    gt = cmap.get(ord(">"))

    feature = f"""
    @original = [{" ".join(plain_glyphs)}];
    @plain = [{" ".join(f"{g}.plain" for g in plain_glyphs)}];

    feature calt {{ 
        lookup PLAIN_START {{sub {gt} @original' by @plain; }} PLAIN_START;
        lookup PLAIN_CHAIN {{sub @plain @original' by @plain; }} PLAIN_CHAIN;
    }} calt;
    """
    with io.StringIO(feature) as fea:
        addOpenTypeFeatures(font, fea)


def font_set_name(font, font_name):
    name_table = font["name"]
    subfamily = next((r for r in name_table.names if r.nameID == 2), None).toUnicode()

    name_table.names = []
    name_table.setName(font_name, 1, 3, 1, 0x409)  # Font Family name
    name_table.setName(subfamily, 2, 3, 1, 0x409)  # Font Subfamily name
    name_table.setName(font_name, 4, 3, 1, 0x409)  # Font Full Name
    name_table.setName(font_name.replace(" ", ""), 6, 3, 1, 0x409)  # PostScript name


def read_palette(file):
    palette = []
    chars = []
    with open(file) as f:
        for line in f:
            color, *etc = line.rstrip("\t\r\n").split("\t")
            if not color.startswith("#"):
                raise ValueError("Color must be in hex format, starting with #")
            color = color[1:]
            r = int(color[4:6], 16)
            g = int(color[2:4], 16)
            b = int(color[0:2], 16)
            palette.append(Color(r, g, b, 0xFF))
            chars.append(etc)
    return palette, chars


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Create a FASTA color font.")
    parser.add_argument("input", help="Path to the input font file")
    parser.add_argument("output", help="Path to the output font file")
    parser.add_argument("--palette-map", help="Palette map file")
    parser.add_argument("--font-name", default="MyFont", help="Family name of the font")
    args = parser.parse_args()

    font = TTFont(args.input)

    cmap = font.getBestCmap()
    plain_glyphs = [cmap[i] for i in range(32, 127) if i in cmap]
    font_add_glyph(font, plain_glyphs)
    font_set_liga(font, plain_glyphs)

    palette, chars = read_palette(args.palette_map)
    palette_glyphs = [[cmap[ord(c)] for c in arr] for arr in chars]
    font_set_color(font, palette, palette_glyphs)

    font_set_name(font, args.font_name)

    font.save(args.output)
