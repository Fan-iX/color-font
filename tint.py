#!/usr/bin/env python3
import io
from fontTools.ttLib import TTFont, newTable
from fontTools.ttLib.tables import otTables
from fontTools.ttLib.tables.C_P_A_L_ import Color
from fontTools.ttLib.tables._g_l_y_f import Glyph, GlyphComponent
from fontTools.feaLib.builder import addOpenTypeFeatures


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


def font_add_glyph(font, ligas):
    glyf, hmtx = font["glyf"], font["hmtx"]
    gord, cmap = font.getGlyphOrder(), font.getBestCmap()

    def register_glyph(name, glyph_obj, width, lsb):
        glyf[name] = glyph_obj
        hmtx[name] = (width, lsb)
        if name not in gord:
            gord.append(name)

    missing_glyphs = set(c for chars in ligas for c in chars if ord(c) not in cmap)
    if missing_glyphs:
        raise ValueError(f"Characters not found in font: {', '.join(missing_glyphs)}")
    for c in set(c for chars in ligas for c in chars[1:]):
        gname = cmap[ord(c)]
        if f"{gname}.hide" not in gord:
            glyph = Glyph()
            glyph.numberOfContours = 0
            register_glyph(f"{gname}.hide", glyph, hmtx[gname][0], 0)
    for liga in ligas:
        name = f"liga.{liga}"
        gname0 = cmap[ord(liga[0])]
        gl = Glyph()
        gl.numberOfContours = -1
        components = []
        x = 0

        for gname in (cmap[ord(c)] for c in liga):
            comp = GlyphComponent()
            comp.glyphName = gname
            comp.x, comp.y = x, 0
            comp.flags = 0x206  # ROUND_XY_TO_GRID
            components.append(comp)
            x += hmtx[comp.glyphName][0]

        gl.components = components
        register_glyph(name, gl, *hmtx[gname0])
    font.setGlyphOrder(gord)


def font_set_liga(font, ligas):
    glyf = font["glyf"]

    rules = {}
    for liga in ligas:
        name = f"liga.{liga}"
        gnames = [comp.glyphName for comp in glyf[name].components]

        rules[liga] = [f"sub {gnames[0]}' {' '.join(gnames[1:])} by {name};"]
        for i in range(1, len(gnames)):
            lookbehind = [name] + [f"{gname}.hide" for gname in gnames[1:i]]
            rules[liga].append(
                f"sub {' '.join(lookbehind)} {gnames[i]}' by {gnames[i]}.hide;"
            )

    rules = [rule for k in sorted(rules, key=len, reverse=True) for rule in rules[k]]
    feature = "feature calt {\n" + "\n".join(rules) + "\n} calt;"
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

    parser = argparse.ArgumentParser(description="Create a color font with ligatures.")
    parser.add_argument("input", help="Path to the input font file")
    parser.add_argument("output", help="Path to the output font file")
    parser.add_argument("--palette-map", help="Palette map file")
    parser.add_argument("--font-name", default="MyFont", help="Family name of the font")
    args = parser.parse_args()

    font = TTFont(args.input)

    cmap = font.getBestCmap()
    palette, chars = read_palette(args.palette_map)
    ligas = [c for arr in chars for c in arr if len(c) > 1]
    font_add_glyph(font, ligas)
    font_set_liga(font, ligas)

    palette_glyphs = [
        [cmap[ord(c)] if len(c) == 1 else f"liga.{c}" for c in arr] for arr in chars
    ]
    font_set_color(font, palette, palette_glyphs)

    font_set_name(font, args.font_name)

    font.save(args.output)
