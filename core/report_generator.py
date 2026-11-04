import os
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle

class PDFReportGenerator:
    """Générateur de rapports PDF professionnels pour PC Check."""
    
    @staticmethod
    def generate_report(hardware_data, analysis_data):
        # Sauvegarde automatique sur le Bureau de l'utilisateur
        desktop = os.path.join(os.environ['USERPROFILE'], 'Desktop')
        date_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = os.path.join(desktop, f"PC_Check_Rapport_{date_str}.pdf")

        doc = SimpleDocTemplate(output_path, pagesize=A4, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
        styles = getSampleStyleSheet()
        elements = []

        # En-tête
        title_style = ParagraphStyle(
            'CustomTitle', parent=styles['Heading1'], fontSize=22, spaceAfter=20, textColor=colors.HexColor("#0F172A")
        )
        elements.append(Paragraph("Diagnostic Système — PC Check", title_style))
        elements.append(Paragraph(f"<b>Date de l'analyse :</b> {datetime.now().strftime('%d/%m/%Y à %H:%M')}", styles['Normal']))
        elements.append(Spacer(1, 20))

        # Section 1 : Matériel
        elements.append(Paragraph("Spécifications Matérielles", styles['Heading2']))
        
        cpu_name = hardware_data['cpu']['name']
        ram_total = f"{hardware_data['ram']['total_gb']} Go"
        
        table_data = [
            ["Composant", "Détails"],
            ["Système", f"Windows {hardware_data['os']['release']} ({hardware_data['os']['architecture']})"],
            ["Processeur", cpu_name],
            ["Mémoire RAM", f"{hardware_data['ram']['manufacturer'] or ''} {hardware_data['ram']['part_number'] or ''} — {ram_total}"]
        ]
        
        for gpu in hardware_data['gpus']:
            vram = f"{gpu['vram_gb']} Go" if gpu['vram_gb'] else "N/A"
            table_data.append(["Carte Graphique", f"{gpu['name']} (VRAM : {vram})"])

        if hardware_data['physical_disks']:
            disk = hardware_data['physical_disks'][0]
            table_data.append(["Stockage", f"{disk['model']} ({disk['size_gb']} Go)"])

        t = Table(table_data, colWidths=[130, 360])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#2563EB")),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor("#F8FAFC")),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor("#E2E8F0"))
        ]))
        elements.append(t)
        elements.append(Spacer(1, 30))

        # Section 2 : Diagnostic
        elements.append(Paragraph("Résultats du Diagnostic", styles['Heading2']))
        elements.append(Paragraph(f"État global du système : <b>{analysis_data['overall_status']}</b>", styles['Normal']))
        elements.append(Spacer(1, 15))

        for report in analysis_data['reports']:
            color = "#EF4444" if report['level'] == "CRITICAL" else ("#F59E0B" if report['level'] == "WARNING" else "#10B981")
            p_style = ParagraphStyle(
                'ReportItem', parent=styles['Normal'], textColor=colors.HexColor(color), fontName="Helvetica-Bold", spaceAfter=4
            )
            elements.append(Paragraph(f"[{report['level']}] {report['category']} : {report['title']}", p_style))
            elements.append(Paragraph(report['description'], styles['Normal']))
            elements.append(Paragraph(f"<i>Conseil : {report['recommendation']}</i>", styles['Normal']))
            elements.append(Spacer(1, 12))

        doc.build(elements)
        return output_path