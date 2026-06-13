import os
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
import fitz  # PyMuPDF

def build_pdf(filename: str, patient_name: str, date: str, params: list):
    doc = SimpleDocTemplate(filename, pagesize=letter, leftMargin=54, rightMargin=54, topMargin=54, bottomMargin=54)
    story = []
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'Title', fontName='Helvetica-Bold', fontSize=20, leading=24, textColor=colors.HexColor('#0284C7'), spaceAfter=15
    )
    section_style = ParagraphStyle(
        'Section', fontName='Helvetica-Bold', fontSize=12, leading=16, textColor=colors.HexColor('#334155'), spaceAfter=8, spaceBefore=10
    )
    body_style = ParagraphStyle(
        'Body', fontName='Helvetica', fontSize=10, leading=14, textColor=colors.HexColor('#1E293B')
    )
    bold_style = ParagraphStyle(
        'Bold', fontName='Helvetica-Bold', fontSize=10, leading=14, textColor=colors.HexColor('#0F172A')
    )

    # Header
    story.append(Paragraph("METROPOLITAN CLINICAL LABS", title_style))
    story.append(Paragraph("Patient Laboratory Analysis Report", ParagraphStyle('Sub', parent=body_style, fontSize=11, textColor=colors.HexColor('#64748B'))))
    story.append(Spacer(1, 10))

    # Divider line
    divider = Table([[""]], colWidths=[504])
    divider.setStyle(TableStyle([
        ('LINEABOVE', (0,0), (-1,-1), 1.5, colors.HexColor('#0EA5E9')),
        ('BOTTOMPADDING', (0,0), (-1,-1), 0),
        ('TOPPADDING', (0,0), (-1,-1), 0),
    ]))
    story.append(divider)
    story.append(Spacer(1, 12))

    # Metadata
    meta_data = [
        [Paragraph("Patient Name:", bold_style), Paragraph(patient_name, body_style),
         Paragraph("Date of Test:", bold_style), Paragraph(date, body_style)],
        [Paragraph("Physician:", bold_style), Paragraph("Dr. Sarah Jenkins", body_style),
         Paragraph("Report Status:", bold_style), Paragraph("Final", body_style)]
    ]
    meta_table = Table(meta_data, colWidths=[90, 162, 90, 162])
    meta_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('TOPPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 15))

    # Values Table
    story.append(Paragraph("Hematology & General Chemistry Results", section_style))
    
    table_data = [[
        Paragraph("<b>Test Name</b>", bold_style),
        Paragraph("<b>Value</b>", bold_style),
        Paragraph("<b>Unit</b>", bold_style),
        Paragraph("<b>Reference Range</b>", bold_style)
    ]]

    for name, val, unit, ref in params:
        table_data.append([
            Paragraph(name, body_style),
            Paragraph(str(val), body_style),
            Paragraph(unit, body_style),
            Paragraph(ref, body_style)
        ])

    val_table = Table(table_data, colWidths=[180, 90, 90, 144])
    val_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#F1F5F9')),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(val_table)
    story.append(Spacer(1, 40))

    # Footer Disclaimer
    disclaimer = Paragraph(
        "Notice: This clinical document is intended solely for diagnostic review. Medical ranges represent standard normal intervals.",
        ParagraphStyle('Disc', parent=body_style, fontSize=8, textColor=colors.HexColor('#64748B'), alignment=1)
    )
    story.append(disclaimer)

    doc.build(story)

def main():
    samples_dir = os.path.dirname(os.path.abspath(__file__))
    os.makedirs(samples_dir, exist_ok=True)

    # 1. Generate Normal CBC PDF
    cbc_normal_path = os.path.join(samples_dir, "cbc_normal.pdf")
    build_pdf(
        cbc_normal_path,
        "Alice Smith",
        "2026-06-01",
        [
            ("Hemoglobin", 14.2, "g/dL", "12.0 - 17.5"),
            ("RBC", 4.8, "million/mcL", "4.2 - 5.9"),
            ("WBC", 6.5, "x10^3/uL", "4.5 - 11.0"),
            ("Platelets", 250, "x10^3/uL", "150 - 450"),
            ("Blood Sugar", 85, "mg/dL", "70 - 100"),
            ("Cholesterol", 180, "mg/dL", "< 200"),
            ("Vitamin D3", 45.0, "ng/mL", "30.0 - 100.0"),
            ("Vitamin B12", 620.0, "pg/mL", "200.0 - 900.0"),
            ("Thyroid TSH", 1.85, "uIU/mL", "0.40 - 4.50")
        ]
    )
    print(f"Generated: {cbc_normal_path}")

    # 2. Generate Abnormal CBC PDF
    cbc_abnormal_path = os.path.join(samples_dir, "cbc_abnormal.pdf")
    build_pdf(
        cbc_abnormal_path,
        "Bob Jones",
        "2026-06-05",
        [
            ("Hemoglobin", 10.5, "g/dL", "12.0 - 17.5"),
            ("RBC", 3.8, "million/mcL", "4.2 - 5.9"),
            ("WBC", 12.8, "x10^3/uL", "4.5 - 11.0"),
            ("Platelets", 130, "x10^3/uL", "150 - 450"),
            ("Blood Sugar", 140, "mg/dL", "70 - 100"),
            ("Cholesterol", 245, "mg/dL", "< 200"),
            ("Vitamin D3", 22.0, "ng/mL", "30.0 - 100.0"),
            ("Vitamin B12", 150.0, "pg/mL", "200.0 - 900.0"),
            ("Thyroid TSH", 5.20, "uIU/mL", "0.40 - 4.50")
        ]
    )
    print(f"Generated: {cbc_abnormal_path}")

    # 3. Generate Metabolic Panel PDF
    metabolic_path = os.path.join(samples_dir, "metabolic_panel.pdf")
    build_pdf(
        metabolic_path,
        "Charlie Brown",
        "2026-06-10",
        [
            ("Hemoglobin", 15.0, "g/dL", "12.0 - 17.5"),
            ("RBC", 5.1, "million/mcL", "4.2 - 5.9"),
            ("WBC", 7.2, "x10^3/uL", "4.5 - 11.0"),
            ("Platelets", 320, "x10^3/uL", "150 - 450"),
            ("Blood Sugar", 210, "mg/dL", "70 - 100"),
            ("Cholesterol", 190, "mg/dL", "< 200"),
            ("Blood Pressure", "150/95", "mmHg", "Systolic <120 / Diastolic <80"),
            ("Vitamin D3", 38.0, "ng/mL", "30.0 - 100.0"),
            ("Vitamin B12", 480.0, "pg/mL", "200.0 - 900.0"),
            ("Thyroid TSH", 0.32, "uIU/mL", "0.40 - 4.50")
        ]
    )
    print(f"Generated: {metabolic_path}")

    # 4. Render Abnormal PDF as Image PNG to simulate a scanned report image
    png_path = os.path.join(samples_dir, "cbc_abnormal.png")
    try:
        doc = fitz.open(cbc_abnormal_path)
        page = doc[0]
        pix = page.get_pixmap(dpi=150)
        pix.save(png_path)
        doc.close()
        print(f"Rendered image: {png_path}")
    except Exception as e:
        print(f"Failed to render image: {e}")

if __name__ == "__main__":
    main()
