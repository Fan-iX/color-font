#!/usr/bin/env python3
from fontTools.ttLib import TTFont
from fontTools.ttLib.tables._g_l_y_f import Glyph, GlyphComponent
from fontTools.feaLib.builder import addOpenTypeFeatures
from fontTools.pens.recordingPen import RecordingPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.ttGlyphPen import TTGlyphPen
import io


def build_chem_font(font):
    glyf, hmtx = font["glyf"], font["hmtx"]
    gord, cmap = font.getGlyphOrder(), font.getBestCmap()
    gset = font.getGlyphSet()
    upm = font["head"].unitsPerEm
    
    def register_glyph(name, glyph_obj, width, lsb):
        glyf[name] = glyph_obj
        hmtx[name] = (width, lsb)
        if name not in gord:
            gord.append(name)

    empty_glyph = Glyph()
    empty_glyph.numberOfContours = 0
    register_glyph("hide.glyph", empty_glyph, 0, 0)

    def build_derivative(src, scale=1, xoff=0, yoff=0):
        rec = RecordingPen()
        gset[src].draw(rec)
        tt_pen = TTGlyphPen(gset)
        t_pen = TransformPen(tt_pen, (scale, 0, 0, scale, xoff, yoff))
        rec.replay(t_pen)
        return tt_pen.glyph()

    caret, lowline = cmap.get(ord("^")), cmap.get(ord("_"))
    nums = [cmap[ord(c)] for c in "0123456789"]
    pm = [cmap[ord(c)] for c in "+-"]

    for g in nums + pm:
        gl = build_derivative(g, 0.6, 0, int(upm * 0.35))
        register_glyph(f"{g}.sup", gl, int(hmtx[g][0] * 0.6), 0)

    for g in nums:
        gl = build_derivative(g, 0.6, 0, int(upm * -0.1))
        register_glyph(f"{g}.sub", gl, int(hmtx[g][0] * 0.6), 0)
    font.setGlyphOrder(gord)

    feature = f"""
    @supprefix = [{caret} {" ".join([c+ ".sup" for c in nums])}];
    @subprefix = [{lowline} {" ".join([c+ ".sub" for c in nums])}];
 
    @supchar0 = [{" ".join(nums + pm)}];
    @subchar0 = [{" ".join(nums)}];
    @supchar = [{" ".join([c+ ".sup" for c in nums + pm])}];
    @subchar = [{" ".join([c+ ".sub" for c in nums])}];

    feature calt {{
        lookup SUB_CHAIN {{ sub @subprefix @subchar0' by @subchar; }} SUB_CHAIN;
        lookup SUP_CHAIN {{ sub @supprefix @supchar0' by @supchar; }} SUP_CHAIN;
 
        lookup HIDE_CARET {{ sub {caret}' @supchar by hide.glyph; }} HIDE_CARET;
        lookup HIDE_LOWLINE {{ sub {lowline}' @subchar by hide.glyph; }} HIDE_LOWLINE;
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


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Create chemical symbols font.")
    parser.add_argument("input", help="Path to input file (TTF font)")
    parser.add_argument("output", help="Path to output file")
    parser.add_argument("--font-name", default="MyFont", help="Family name of the font")
    args = parser.parse_args()

    font = TTFont(args.input)
    build_chem_font(font)
    font_set_name(font, args.font_name)
    font.save(args.output)
