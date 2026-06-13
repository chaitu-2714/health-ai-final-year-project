import os
import logging
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

logger = logging.getLogger("MedicalApp.PDFExport")

class PDFExportService:
    """Generates professional PDF reports from medical analysis results using ReportLab."""

    @staticmethod
    def export_report_to_pdf(output_path: str, patient_name: str, email: str, report_date: str, parameters: list, ai_summary: str) -> bool:
        """
        Creates a stylized, production-grade PDF medical analysis report.
        """
        try:
            logger.info(f"Generating PDF report to: {output_path}")
            
            # Setup document
            doc = SimpleDocTemplate(
                output_path,
                pagesize=letter,
                rightMargin=54,
                leftMargin=54,
                topMargin=54,
                bottomMargin=54
            )
            
            story = []
            styles = getSampleStyleSheet()

            # Custom styles
            title_style = ParagraphStyle(
                'DocTitle',
                parent=styles['Normal'],
                fontName='Helvetica-Bold',
                fontSize=22,
                leading=26,
                textColor=colors.HexColor("#0D5C75")  # Dark teal
            )
            
            section_style = ParagraphStyle(
                'SectionHeader',
                parent=styles['Normal'],
                fontName='Helvetica-Bold',
                fontSize=14,
                leading=18,
                textColor=colors.HexColor("#0D5C75"),
                spaceAfter=8,
                spaceBefore=15
            )
            
            body_style = ParagraphStyle(
                'BodyTextCustom',
                parent=styles['Normal'],
                fontName='Helvetica',
                fontSize=10,
                leading=14,
                textColor=colors.HexColor("#333333")
            )
            
            bold_label = ParagraphStyle(
                'BoldLabel',
                parent=styles['Normal'],
                fontName='Helvetica-Bold',
                fontSize=10,
                leading=14,
                textColor=colors.HexColor("#111111")
            )
            
            summary_style = ParagraphStyle(
                'SummaryStyle',
                parent=styles['Normal'],
                fontName='Helvetica',
                fontSize=10.5,
                leading=15,
                textColor=colors.HexColor("#222222")
            )

            # 1. Header
            story.append(Paragraph("AURA HEALTHCARE SYSTEMS", title_style))
            story.append(Paragraph("Clinical Parameter Analysis Report - Confidential", ParagraphStyle('Sub', parent=body_style, fontSize=11, textColor=colors.HexColor("#666666"))))
            story.append(Spacer(1, 10))

            # Horizontal line
            line_table = Table([[""]], colWidths=[504])
            line_table.setStyle(TableStyle([
                ('LINEABOVE', (0,0), (-1,-1), 1.5, colors.HexColor("#0D5C75")),
                ('BOTTOMPADDING', (0,0), (-1,-1), 0),
                ('TOPPADDING', (0,0), (-1,-1), 0),
            ]))
            story.append(line_table)
            story.append(Spacer(1, 15))

            # 2. Patient / Report Metadata Table
            meta_data = [
                [Paragraph("Patient Name:", bold_label), Paragraph(patient_name, body_style),
                 Paragraph("Report Date:", bold_label), Paragraph(report_date, body_style)],
                [Paragraph("Email Address:", bold_label), Paragraph(email, body_style),
                 Paragraph("Export Date:", bold_label), Paragraph(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), body_style)]
            ]
            meta_table = Table(meta_data, colWidths=[90, 162, 80, 172])
            meta_table.setStyle(TableStyle([
                ('ALIGN', (0,0), (-1,-1), 'LEFT'),
                ('VALIGN', (0,0), (-1,-1), 'TOP'),
                ('BOTTOMPADDING', (0,0), (-1,-1), 4),
                ('TOPPADDING', (0,0), (-1,-1), 4),
            ]))
            story.append(meta_table)
            story.append(Spacer(1, 20))

            # 3. Parameters Table
            story.append(Paragraph("Extracted Lab Parameters", section_style))
            
            # Table headers
            table_data = [[
                Paragraph("<b>Parameter</b>", bold_label),
                Paragraph("<b>Observed Value</b>", bold_label),
                Paragraph("<b>Unit</b>", bold_label),
                Paragraph("<b>Status</b>", bold_label),
                Paragraph("<b>Reference Range</b>", bold_label)
            ]]

            # Styles for cells
            cell_style = ParagraphStyle('Cell', parent=body_style, fontSize=9.5)
            
            status_colors = {
                "Normal": colors.HexColor("#2ECC71"),  # Light Green
                "Low": colors.HexColor("#F1C40F"),     # Yellow
                "High": colors.HexColor("#E67E22"),    # Orange
                "Critical": colors.HexColor("#E74C3C")  # Red
            }

            for p in parameters:
                name = p.get("parameter_name", "N/A")
                val = str(p.get("value", "N/A"))
                unit = p.get("unit", "")
                status = p.get("classification", "Normal")
                ref_range = p.get("reference_range", "N/A")
                
                # Check status text color
                status_color = status_colors.get(status, colors.black)
                status_p = Paragraph(f"<font color='{status_color.hexval()}'><b>{status}</b></font>", cell_style)

                table_data.append([
                    Paragraph(name, cell_style),
                    Paragraph(val, cell_style),
                    Paragraph(unit, cell_style),
                    status_p,
                    Paragraph(ref_range, cell_style)
                ])

            param_table = Table(table_data, colWidths=[134, 90, 80, 80, 120])
            param_table.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#F2F6F8")),
                ('ALIGN', (0,0), (-1,-1), 'LEFT'),
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#DDDDDD")),
                ('TOPPADDING', (0,0), (-1,-1), 6),
                ('BOTTOMPADDING', (0,0), (-1,-1), 6),
                ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#FAFBFB")])
            ]))
            story.append(param_table)
            story.append(Spacer(1, 20))

            # 4. AI-Generated Summary Block (Keep together to avoid page break mid-summary)
            summary_elements = [
                Paragraph("AI-Generated Clinical Summary", section_style),
                Spacer(1, 4)
            ]
            
            # Wrap summary in a nice border box
            summary_box_data = [[Paragraph(ai_summary, summary_style)]]
            summary_box_table = Table(summary_box_data, colWidths=[504])
            summary_box_table.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F5F9FA")),
                ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#D1E2E6")),
                ('TOPPADDING', (0,0), (-1,-1), 12),
                ('BOTTOMPADDING', (0,0), (-1,-1), 12),
                ('LEFTPADDING', (0,0), (-1,-1), 12),
                ('RIGHTPADDING', (0,0), (-1,-1), 12),
            ]))
            summary_elements.append(summary_box_table)
            story.append(KeepTogether(summary_elements))
            
            story.append(Spacer(1, 30))

            # 5. Footer / Disclaimer
            disclaimer_style = ParagraphStyle(
                'Disclaimer',
                parent=styles['Normal'],
                fontName='Helvetica-Oblique',
                fontSize=8,
                leading=11,
                textColor=colors.HexColor("#777777"),
                alignment=1  # Centered
            )
            story.append(Paragraph(
                "Disclaimer: This report is automatically generated using optical character recognition (OCR) and artificial intelligence. "
                "The analysis and classifications provided are for informational and educational purposes only. They do not constitute formal medical diagnosis "
                "or professional advice. Always verify results with a medical professional and consult your physician regarding health issues.",
                disclaimer_style
            ))

            # Build document
            doc.build(story)
            logger.info("PDF report exported successfully.")
            return True
            
        except Exception as e:
            logger.error(f"Error exporting PDF report: {e}")
            return False
