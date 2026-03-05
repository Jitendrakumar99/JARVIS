"""
PDF Generator for Student Reports
Uses ReportLab for professional PDF generation
"""
import os
from datetime import datetime

# Try to import ReportLab
try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False
    print("Warning: reportlab not installed. PDF generation will be limited.")


def generate_student_pdf(student, upload_folder):
    """
    Generate a professional PDF report for a student
    
    Args:
        student: Student object
        upload_folder: Path to uploads folder
        
    Returns:
        Path to generated PDF file
    """
    if not REPORTLAB_AVAILABLE:
        raise ImportError("ReportLab is required for PDF generation. Install with: pip install reportlab")
    
    # Create temp folder for PDFs
    pdf_folder = os.path.join(upload_folder, 'pdfs')
    os.makedirs(pdf_folder, exist_ok=True)
    
    # Generate filename
    filename = f"{student.roll_no}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    pdf_path = os.path.join(pdf_folder, filename)
    
    # Create document
    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=A4,
        rightMargin=0.75*inch,
        leftMargin=0.75*inch,
        topMargin=0.75*inch,
        bottomMargin=0.75*inch
    )
    
    # Styles
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=20,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#1a365d')
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        spaceBefore=15,
        spaceAfter=10,
        textColor=colors.HexColor('#2d3748'),
        borderPadding=5
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=11,
        spaceAfter=8,
        leading=14
    )
    
    # Build content
    content = []
    
    # Header
    content.append(Paragraph("STUDENT PROFILE REPORT", title_style))
    content.append(Spacer(1, 10))
    
    # Photo (if exists)
    if student.image_path:
        image_full_path = os.path.join(upload_folder, student.image_path.replace('uploads/', ''))
        if os.path.exists(image_full_path):
            try:
                img = Image(image_full_path, width=1.5*inch, height=1.5*inch)
                content.append(img)
                content.append(Spacer(1, 10))
            except:
                pass
    
    # Personal Information Table
    content.append(Paragraph("Personal Information", heading_style))
    
    personal_data = [
        ['Name', student.name],
        ['Roll Number', student.roll_no],
        ['Department', student.department],
        ['Year', str(student.year)],
        ['Email', student.email or 'N/A'],
        ['Phone', student.phone or 'N/A'],
    ]
    
    personal_table = Table(personal_data, colWidths=[2*inch, 4*inch])
    personal_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e2e8f0')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#1a202c')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#cbd5e0')),
    ]))
    
    content.append(personal_table)
    content.append(Spacer(1, 20))
    
    # Skills
    content.append(Paragraph("Technical Skills", heading_style))
    if student.skills:
        skills_text = " • ".join(student.skills)
        content.append(Paragraph(skills_text, normal_style))
    else:
        content.append(Paragraph("No skills listed", normal_style))
    
    content.append(Spacer(1, 15))
    
    # Projects
    content.append(Paragraph("Projects", heading_style))
    if student.projects:
        for project in student.projects:
            content.append(Paragraph(f"• {project}", normal_style))
    else:
        content.append(Paragraph("No projects listed", normal_style))
    
    content.append(Spacer(1, 15))
    
    # Internships
    content.append(Paragraph("Internships & Experience", heading_style))
    if student.internships:
        for internship in student.internships:
            content.append(Paragraph(f"• {internship}", normal_style))
    else:
        content.append(Paragraph("No internships listed", normal_style))
    
    content.append(Spacer(1, 30))
    
    # Footer
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.grey,
        alignment=TA_CENTER
    )
    
    content.append(Paragraph(
        f"Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}",
        footer_style
    ))
    content.append(Paragraph(
        "Smart College Student Assistance Portal",
        footer_style
    ))
    
    # Build PDF
    doc.build(content)
    
    return pdf_path
