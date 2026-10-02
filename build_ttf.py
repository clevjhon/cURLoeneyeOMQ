from fontTools.fontBuilder import FontBuilder

print("[*] Rebuilding OMQ.ttf with family name 'OMQ'...")
with open("OMQ.FNT", "rb") as f:
    data = f.read()

fb = FontBuilder(1024, isTTF=True)
fb.setupGlyphOrder(['.notdef'] + [f"uni{i:04X}" for i in range(256)])
fb.setupCharacterMap({i: f"uni{i:04X}" for i in range(256)})
fb.setupHorizontalMetrics({'.notdef': (500, 0), **{f"uni{i:04X}": (500, 0) for i in range(256)}})
fb.setupHorizontalHeader(ascent=800, descent=-200)

fb.setupNameTable({
    'familyName': 'OMQ',
    'styleName': 'Regular',
    'uniqueFontIdentifier': 'OMQ-Regular',
    'fullName': 'OMQ Regular',
    'psName': 'OMQ'
})

fb.setupOS2(sTypoAscender=800, sTypoDescender=-200, usWinAscent=800, usWinDescent=200)
fb.setupPost()
fb.save("OMQ.ttf")
print("[SUCCESS] OMQ.ttf updated!")
