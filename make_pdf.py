from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

def generate_pdf():
    pdf_filename = "summary.pdf"
    doc = SimpleDocTemplate(pdf_filename, pagesize=letter,
                            rightMargin=54, leftMargin=54,
                            topMargin=54, bottomMargin=54)
    story = []
    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontSize=20,
        leading=24,
        textColor=colors.HexColor('#1A237E'),
        spaceAfter=6
    )
    
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#555555'),
        spaceAfter=15
    )

    heading_style = ParagraphStyle(
        'SectionHeading',
        parent=styles['Heading2'],
        fontSize=14,
        leading=18,
        textColor=colors.HexColor('#283593'),
        spaceBefore=12,
        spaceAfter=6
    )

    body_style = ParagraphStyle(
        'BodyTextCustom',
        parent=styles['Normal'],
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#212121'),
        spaceAfter=6
    )

    # Content
    story.append(Paragraph("OENEYE Virtual Environment — Progress Summary", title_style))
    story.append(Paragraph("System: SIETEHR FOUNDATION (NCAGE: CNNN3) | Date: September 2026", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#283593'), spaceAfter=15))

    sections = [
        ("1. Virtual DOS Runtime (emu_dos.py)", 
         "Established a dual-drive virtual architecture featuring drive <b>C:</b> for the local workspace and drive <b>X:</b> for network archives and shared storage. Implemented core command handling including <b>DIR</b>, <b>CD</b>, <b>TYPE</b>, <b>LEDGER</b>, <b>OAI</b> (for OAI-PMH XML feeds), and <b>BACKUP</b>."),
        
        ("2. System Mapping (MAP Command)", 
         "Integrated a dedicated system map routine to display active workspace paths, telemetry locations, network shares, and your linked Zenodo repository identifier (<b>23026079</b>)."),
        
        ("3. Update Automation Pipeline", 
         "Orchestrated a unified script runner (<b>run_pipeline.py</b>) executing <b>update.py</b>, <b>update_channels.py</b>, and <b>update_emu.py</b> in sequence, directly callable from the virtual shell via the <b>UPDATE</b> command."),
        
        ("4. Automated Snapshots & Backups", 
         "Configured persistent state snapshotting on <b>EXIT</b>, which automatically bundles database records and indices into timestamped <b>.tar</b> archives within <b>X:\\ARCHIVE</b>."),
        
        ("5. AUTOEXEC.BAT Startup Routine", 
         "Added a non-destructive batch execution feature that safely reads an <b>AUTOEXEC.BAT</b> file upon boot to run startup diagnostic or mapping commands automatically.")
    ]

    for title, text in sections:
        story.append(Paragraph(title, heading_style))
        story.append(Paragraph(text, body_style))
        story.append(Spacer(1, 4))

    doc.build(story)
    print(f"[SUCCESS] Generated PDF summary: {pdf_filename}")

if __name__ == '__main__':
    generate_pdf()
