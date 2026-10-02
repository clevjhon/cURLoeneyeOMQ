import fitz  # PyMuPDF

# Open the harvested PDF document
doc = fitz.open("dnb_publication.pdf")
page = doc.load_page(0)  # First page

# Set high-resolution matrix zoom (300 DPI)
zoom = 4.16
mat = fitz.Matrix(zoom, zoom)
pix = page.get_pixmap(matrix=mat)

# Save enhanced output
pix.save("dnb_enhanced_highres.png")
print("High-resolution rendering saved as dnb_enhanced_highres.png 🖼️✨")
