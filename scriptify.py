#!/usr/bin/env python3
from fontTools.ttLib import TTFont
from fontTools.ttLib.tables._g_l_y_f import Glyph, GlyphComponent
from fontTools.feaLib.builder import addOpenTypeFeatures
from fontTools.pens.recordingPen import RecordingPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.ttGlyphPen import TTGlyphPen
import io


def font_add_script(font, chars):
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
    register_glyph("lbrace.supstart", empty_glyph, 0, 0)
    register_glyph("lbrace.substart", empty_glyph, 0, 0)

    def build_derivative(src, scale=1, xoff=0, yoff=0):
        rec = RecordingPen()
        gset[src].draw(rec)
        tt_pen = TTGlyphPen(gset)
        t_pen = TransformPen(tt_pen, (scale, 0, 0, scale, xoff, yoff))
        rec.replay(t_pen)
        return tt_pen.glyph()

    def register_script(name, base_glyph, scale, yoff):
        gl = build_derivative(base_glyph, scale, 0, int(upm * yoff))
        return register_glyph(name, gl, int(hmtx[base_glyph][0] * scale), 0)

    def register_clone(name, base_glyph):
        comp_glyph = Glyph()
        comp_glyph.numberOfContours = -1
        comp = GlyphComponent()
        comp.glyphName, comp.x, comp.y = base_glyph, 0, 0
        comp.flags = 0x206
        comp_glyph.components = [comp]
        return register_glyph(name, comp_glyph, hmtx[base_glyph][0], 0)

    for g in (cmap[ord(c)] for c in chars if c not in "{}"):
        register_script(f"{g}.supc", g, 0.6, +0.35)
        register_clone(f"{g}.sup1", f"{g}.supc")
        register_script(f"{g}.subc", g, 0.6, -0.1)
        register_clone(f"{g}.sub1", f"{g}.subc")
    font.setGlyphOrder(gord)


def font_set_liga(font, chars):
    cmap = font.getBestCmap()

    caret, lowline = cmap.get(ord("^")), cmap.get(ord("_"))
    lbrace, rbrace = cmap.get(ord("{")), cmap.get(ord("}"))

    chars = [cmap[ord(c)] for c in chars if c not in "{}"]

    feature = f"""
    @orichar = [{" ".join(chars)}];
    @supchar = [{" ".join([c+ ".supc" for c in chars])}];
    @subchar = [{" ".join([c+ ".subc" for c in chars])}];
    @sup1char = [{" ".join([c+ ".sup1" for c in chars])}];
    @sub1char = [{" ".join([c+ ".sub1" for c in chars])}];

    @supprefix = [lbrace.supstart @supchar];
    @subprefix = [lbrace.substart @subchar];
    @suphidesuffix = [lbrace.supstart @sup1char];
    @subhidesuffix = [lbrace.substart @sub1char];

    feature ccmp {{
        lookup SUP_CHAR {{ sub {caret} @orichar' by @sup1char; }} SUP_CHAR;
        lookup SUP_CHAIN_START {{ sub {caret} {lbrace}' by lbrace.supstart; }} SUP_CHAIN_START;
        lookup SUP_CHAIN {{ sub @supprefix @orichar' by @supchar; }} SUP_CHAIN;
        lookup SUP_END {{ sub @supchar {rbrace}' by hide.glyph; }} SUP_END;
        lookup HIDE_CARET {{ sub {caret}' @suphidesuffix by hide.glyph; }} HIDE_CARET;

        lookup SUB_CHAR {{ sub {lowline} @orichar' by @sub1char; }} SUB_CHAR;
        lookup SUB_CHAIN_START {{ sub {lowline} {lbrace}' by lbrace.substart; }} SUB_CHAIN_START;
        lookup SUB_CHAIN {{ sub @subprefix @orichar' by @subchar; }} SUB_CHAIN;
        lookup SUB_END {{ sub @subchar {rbrace}' by hide.glyph; }} SUB_END;
        lookup HIDE_LOWLINE {{ sub {lowline}' @subhidesuffix by hide.glyph; }} HIDE_LOWLINE;
    }} ccmp;
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


def parse_unicode_list(s):
    if s == "*":
        return None
    res = set()
    for part in s.split(","):
        part = part.strip().lstrip("Uu+")
        if "-" in part:
            start, end = part.split("-", 1)
            res.update(range(int(start, 16), int(end, 16) + 1))
        else:
            res.add(int(part, 16))
    return [chr(i) for i in sorted(res)]


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Create super/subscript font.")
    parser.add_argument("input", help="Path to the input font file")
    parser.add_argument("output", help="Path to the output font file")
    parser.add_argument("--unicodes", help="""
Specify comma-separated list of Unicode codepoints or
ranges as hex numbers, optionally prefixed with 'U+', 'u', etc.
use '*' to use all Unicode characters mapped in the font.
""", default="*")
    parser.add_argument("--font-name", default="MyFont", help="Family name of the font")
    args = parser.parse_args()

    font = TTFont(args.input)

    cmap = font.getBestCmap()
    script_chars = parse_unicode_list(args.unicodes)
    if script_chars is None:
        script_chars = [chr(i) for i in cmap.keys()]
    script_chars = [c for c in script_chars if ord(c) in cmap]
    font_add_script(font, script_chars)
    font_set_liga(font, script_chars)

    font_set_name(font, args.font_name)

    font.save(args.output)
