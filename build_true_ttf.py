import fontTools.fontBuilder
from fontTools.ttLib.tables import ttProgram
from fontTools.ttLib.tables._g_l_y_f import Glyph

print("[*] Parsing OMQ.FNT and adding font program bytecode...")

with open("OMQ.FNT", "rb") as f:
    raw_data = f.read()

glyf_table = {}
hmetrics = {'.notdef': (500, 0)}
glyph_order = ['.notdef']

g_notdef = Glyph()
g_notdef.coordinates = []
g_notdef.endPtsOfContours = []
g_notdef.flags = []
g_notdef.numberOfContours = 0
g_notdef.program = ttProgram.Program()
g_notdef.program.fromBytecode(b"")
glyf_table['.notdef'] = g_notdef

for i in range(256):
    char_bytes = raw_data[i*16 : (i+1)*16]
    glyph_name = f"uni{i:04X}"
    glyph_order.append(glyph_name)
    hmetrics[glyph_name] = (500, 0)
    
    g = Glyph()
    g.program = ttProgram.Program()
    g.program.fromBytecode(b"")
    
    contours = []
    for row_idx, row_byte in enumerate(char_bytes):
        for col_idx in range(8):
            if (row_byte & (1 << (7 - col_idx))):
                x = col_idx * 60
                y = (15 - row_idx) * 60
                w = 55
                h = 55
                pts = [(x, y), (x + w, y), (x + w, y + h), (x, y + h)]
                contours.append(pts)
    
    if contours:
        flat_pts = []
        end_points = []
        flags = []
        pt_idx = 0
        for contour in contours:
            for pt in contour:
                flat_pts.append(pt)
                flags.append(1)
            pt_idx += len(contour)
            end_points.append(pt_idx - 1)
        
        g.coordinates = fontTools.ttLib.tables._g_l_y_f.GlyphCoordinates(flat_pts)
        g.endPtsOfContours = end_points
        g.flags = bytes(flags)
        g.numberOfContours = len(contours)
    else:
        g.coordinates = []
        g.endPtsOfContours = []
        g.flags = []
        g.numberOfContours = 0
        
    glyf_table[glyph_name] = g

fb = fontTools.fontBuilder.FontBuilder(1024, isTTF=True)
fb.setupGlyphOrder(glyph_order)
fb.setupCharacterMap({i: f"uni{i:04X}" for i in range(256)})
fb.setupHorizontalMetrics(hmetrics)
fb.setupHorizontalHeader(ascent=1000, descent=-200)
fb.setupNameTable({
    'familyName': 'OMQ',
    'styleName': 'Regular',
    'uniqueFontIdentifier': 'OMQ-Regular',
    'fullName': 'OMQ Regular',
    'psName': 'OMQ'
})
fb.setupOS2(sTypoAscender=1000, sTypoDescender=-200, usWinAscent=1000, usWinDescent=200)
fb.setupPost()
fb.setupGlyf(glyf_table)

fb.save("OMQ.ttf")
print("[SUCCESS] Fully rendered OMQ.ttf generated successfully!")
