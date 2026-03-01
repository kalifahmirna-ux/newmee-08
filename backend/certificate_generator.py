"""
Certificate Generator untuk NEWME CLASS
Menghasilkan sertifikat PDF dengan desain sesuai template
"""
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm, mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from io import BytesIO
from datetime import datetime
import os
from personality_data import get_personality_data, determine_personality_code, PERSONALITY_DATA

# Colors
GOLD = colors.HexColor("#D4AF37")
DARK_GOLD = colors.HexColor("#B8860B")
BLACK = colors.HexColor("#1a1a1a")
WHITE = colors.white
GRAY = colors.HexColor("#666666")

# Element Colors
ELEMENT_COLORS = {
    "KAYU": colors.HexColor("#4CAF50"),
    "API": colors.HexColor("#F44336"),
    "TANAH": colors.HexColor("#FFC107"),
    "LOGAM": colors.HexColor("#9E9E9E"),
    "AIR": colors.HexColor("#2196F3")
}


class CertificateGenerator:
    def __init__(self):
        self.width, self.height = landscape(A4)
        self.margin = 1 * cm
        
    def generate_certificate(self, user_data: dict, analysis_data: dict) -> BytesIO:
        """Generate PDF certificate"""
        buffer = BytesIO()
        
        # Create canvas
        c = canvas.Canvas(buffer, pagesize=landscape(A4))
        
        # Get personality data
        personality_type = analysis_data.get("personalityType", "AMBIVERT")
        dominant_element = analysis_data.get("dominantElement", "KAYU")
        personality_code = determine_personality_code(personality_type, dominant_element)
        pdata = get_personality_data(personality_code)
        
        # Draw background
        self._draw_background(c)
        
        # Draw decorative elements
        self._draw_decorations(c)
        
        # Draw header
        self._draw_header(c, user_data)
        
        # Draw left column - Personality details
        self._draw_left_column(c, pdata, analysis_data)
        
        # Draw right column - Symbol and summary
        self._draw_right_column(c, pdata, analysis_data, user_data)
        
        # Draw footer with signature
        self._draw_footer(c)
        
        c.save()
        buffer.seek(0)
        return buffer
    
    def _draw_background(self, c):
        """Draw white background"""
        c.setFillColor(WHITE)
        c.rect(0, 0, self.width, self.height, fill=True, stroke=False)
    
    def _draw_decorations(self, c):
        """Draw gold decorative elements"""
        # Top left gold dots
        c.setFillColor(GOLD)
        for row in range(4):
            for col in range(12):
                x = 15 + col * 8
                y = self.height - 20 - row * 8
                c.circle(x, y, 2, fill=True)
        
        # Bottom left gold dots
        for row in range(4):
            for col in range(12):
                x = 15 + col * 8
                y = 50 + row * 8
                c.circle(x, y, 2, fill=True)
        
        # Top right gold dots
        for row in range(4):
            for col in range(8):
                x = self.width - 80 + col * 8
                y = self.height - 20 - row * 8
                c.circle(x, y, 2, fill=True)
        
        # Bottom right triangular decoration
        c.setFillColor(DARK_GOLD)
        path = c.beginPath()
        path.moveTo(self.width - 150, 0)
        path.lineTo(self.width, 0)
        path.lineTo(self.width, 150)
        path.close()
        c.drawPath(path, fill=True)
        
        # Inner triangle
        c.setFillColor(BLACK)
        path = c.beginPath()
        path.moveTo(self.width - 100, 0)
        path.lineTo(self.width, 0)
        path.lineTo(self.width, 100)
        path.close()
        c.drawPath(path, fill=True)
        
        # Left side gold stripe
        c.setFillColor(GOLD)
        c.rect(0, 100, 5, self.height - 200, fill=True)
        
        # Bottom gold stripe
        c.setFillColor(DARK_GOLD)
        path = c.beginPath()
        path.moveTo(0, 0)
        path.lineTo(200, 0)
        path.lineTo(250, 50)
        path.lineTo(50, 50)
        path.close()
        c.drawPath(path, fill=True)
    
    def _draw_header(self, c, user_data):
        """Draw certificate header"""
        # NEWME Logo placeholder (colorful circle)
        center_x = self.width / 2 - 50
        logo_y = self.height - 80
        
        # Draw 5-element colored circle
        c.setFillColor(colors.HexColor("#F44336"))  # Red
        c.wedge(center_x - 30, logo_y - 25, center_x + 30, logo_y + 25, 0, 72, fill=True)
        c.setFillColor(colors.HexColor("#FFC107"))  # Yellow
        c.wedge(center_x - 30, logo_y - 25, center_x + 30, logo_y + 25, 72, 144, fill=True)
        c.setFillColor(colors.HexColor("#4CAF50"))  # Green
        c.wedge(center_x - 30, logo_y - 25, center_x + 30, logo_y + 25, 144, 216, fill=True)
        c.setFillColor(colors.HexColor("#2196F3"))  # Blue
        c.wedge(center_x - 30, logo_y - 25, center_x + 30, logo_y + 25, 216, 288, fill=True)
        c.setFillColor(colors.HexColor("#9E9E9E"))  # Gray
        c.wedge(center_x - 30, logo_y - 25, center_x + 30, logo_y + 25, 288, 360, fill=True)
        
        # Title
        c.setFillColor(BLACK)
        c.setFont("Helvetica-Bold", 28)
        c.drawString(self.width / 2 + 30, self.height - 55, "SERTIFIKAT")
        
        c.setFont("Helvetica-Bold", 14)
        c.drawString(self.width / 2 + 30, self.height - 75, "ANALISA KEPRIBADIAN & JATIDIRI")
        
        # ID
        c.setFont("Helvetica", 11)
        cert_id = user_data.get("certificateId", f"NM-{datetime.now().strftime('%Y%m%d')}-001")
        c.drawString(self.width / 2 + 60, self.height - 100, f"ID : {cert_id}")
        
        # Name bar
        c.setFillColor(colors.HexColor("#E0E0E0"))
        c.roundRect(self.width / 2 + 30, self.height - 145, 230, 30, 5, fill=True)
        
        c.setFillColor(BLACK)
        c.setFont("Helvetica-Bold", 10)
        c.drawString(self.width / 2 + 50, self.height - 125, "Optimalkan versi terbaik_mu")
        
        # User name
        c.setFillColor(colors.HexColor("#E0E0E0"))
        c.roundRect(self.width / 2 + 30, self.height - 180, 230, 25, 3, fill=True)
        c.setFillColor(BLACK)
        c.setFont("Helvetica-Bold", 12)
        user_name = user_data.get("fullName", "Nama Peserta")
        c.drawCentredString(self.width / 2 + 145, self.height - 172, user_name[:30])
    
    def _draw_left_column(self, c, pdata, analysis_data):
        """Draw left column with personality details"""
        x_start = 20
        y_start = self.height - 100
        line_height = 12
        
        # Kepribadian section
        c.setFillColor(BLACK)
        c.setFont("Helvetica-Bold", 11)
        c.drawString(x_start, y_start, "Kepribadian :")
        
        y = y_start - 15
        c.setFont("Helvetica", 9)
        kepribadian_text = ", ".join(pdata.get("kepribadian", []))
        
        # Word wrap kepribadian
        max_width = 280
        words = kepribadian_text.split(", ")
        line = ""
        for word in words:
            test_line = f"{line}, {word}" if line else word
            if c.stringWidth(test_line, "Helvetica", 9) < max_width:
                line = test_line
            else:
                c.drawString(x_start, y, line)
                y -= line_height
                line = word
        if line:
            c.drawString(x_start, y, line)
            y -= line_height
        
        # +/- Karakter section
        y -= 10
        c.setFont("Helvetica-Bold", 11)
        c.drawString(x_start, y, "+/- Karakter :")
        y -= 15
        
        c.setFont("Helvetica", 8)
        karakter_text = " - ".join(pdata.get("karakter", []))
        
        # Word wrap karakter
        words = karakter_text.split(" - ")
        line = ""
        for word in words:
            test_line = f"{line} - {word}" if line else word
            if c.stringWidth(test_line, "Helvetica", 8) < max_width:
                line = test_line
            else:
                c.drawString(x_start, y, line)
                y -= line_height
                line = word
        if line:
            c.drawString(x_start, y, line)
            y -= line_height
        
        # Kekuatan Jatidiri section
        y -= 10
        c.setFont("Helvetica-Bold", 11)
        kj = pdata.get("kekuatanJatidiri", {})
        c.drawString(x_start, y, f"Kekuatan Jatidiri : {kj.get('tipe', 'Si KREATIF')}")
        y -= 15
        
        c.setFont("Helvetica", 9)
        kj_text = f"Kehidupan : {kj.get('kehidupan', '')} - Kesehatan : {kj.get('kesehatan', '')}"
        c.drawString(x_start, y, kj_text)
        y -= line_height
        
        kj_text2 = f"Kontribusi : {kj.get('kontribusi', '')} - Kekhasan : {kj.get('kekhasan', '')} - Kharisma :"
        c.drawString(x_start, y, kj_text2)
        y -= line_height
        c.drawString(x_start, y, kj.get('kharisma', ''))
        y -= line_height
        
        # Kompilasi Adaptasi section
        y -= 10
        c.setFont("Helvetica-Bold", 11)
        c.drawString(x_start, y, "Kompilasi Adaptasi :")
        y -= 15
        
        c.setFont("Helvetica", 7)
        ka = pdata.get("kompilasiAdaptasi", {})
        
        # Format kompilasi adaptasi
        ka_items = [
            f"Belajar : {ka.get('belajar', '')} - Bekerja : {ka.get('bekerja', '')} - Kalibrasi :",
            f"{ka.get('kalibrasi', '')} - Daya Raga : {ka.get('dayaRaga', '')} - Memimpin :",
            f"{ka.get('memimpin', '')} - Jalur Bisnis : {ka.get('jalurBisnis', '')} - Pendukung",
            f"karir : {ka.get('pendukungKarir', '')} - Keahlian : {ka.get('keahlian', '')} - Karya : {ka.get('karya', '')}",
            f" - Keunggulan : {ka.get('keunggulan', '')} - Kemistri : {ka.get('kemistri', '')} -",
            f"Keutamaan : {ka.get('keutamaan', '')} - Kelimpahan : {ka.get('kelimpahan', '')} - Magnet",
            f": {ka.get('magnet', '')} - Berbusana : {ka.get('berbusana', '')} - Kecepatan :",
            f"{ka.get('kecepatan', '')} - Kesukaan : {ka.get('kesukaan', '')} - Kebiasaan :",
            f"{ka.get('kebiasaan', '')} - Semesta Hidup : {ka.get('semestaHidup', '')} - Makanan :",
            f"{ka.get('makanan', '')} - Kehebatan : {ka.get('kehebatan', '')}."
        ]
        
        for item in ka_items:
            c.drawString(x_start, y, item)
            y -= 10
    
    def _draw_right_column(self, c, pdata, analysis_data, user_data):
        """Draw right column with symbol and summary"""
        x_start = self.width / 2 + 30
        y_start = self.height - 200
        
        # Personality Type
        c.setFillColor(BLACK)
        c.setFont("Helvetica", 11)
        c.drawString(x_start + 60, y_start, "Kepribadian :")
        
        personality_type = pdata.get("personalityType", "INTROVERT")
        c.setFont("Helvetica-Bold", 14)
        c.setFillColor(DARK_GOLD)
        c.drawString(x_start + 140, y_start, personality_type)
        
        # Symbol Jatidiri box
        y = y_start - 50
        code = pdata.get("code", "iK")
        
        # Draw symbol box
        c.setStrokeColor(BLACK)
        c.setFillColor(WHITE)
        c.roundRect(x_start, y - 30, 80, 60, 5, fill=True, stroke=True)
        
        # Draw code
        c.setFillColor(GOLD)
        c.setFont("Helvetica-Bold", 32)
        c.drawCentredString(x_start + 40, y - 10, code)
        
        # Simbol Jatidiri label
        c.setFillColor(BLACK)
        c.setFont("Helvetica-Bold", 10)
        c.drawString(x_start + 95, y + 15, "Simbol Jatidiri :")
        
        # Dominant elements
        element_scores = analysis_data.get("elementScores", {})
        dominant_element = pdata.get("dominantElement", "KAYU")
        
        # Sort elements by percentage
        sorted_elements = sorted(
            element_scores.items(), 
            key=lambda x: x[1].get("percentage", 0) if isinstance(x[1], dict) else 0, 
            reverse=True
        )[:3]
        
        y_dom = y + 5
        dominan_labels = ["Dominan I", "Dominan II", "Dominan III"]
        
        if sorted_elements:
            for i, (elem, data) in enumerate(sorted_elements):
                c.setFont("Helvetica", 9)
                c.setFillColor(BLACK)
                c.drawString(x_start + 110, y_dom, dominan_labels[i])
                
                elem_color = ELEMENT_COLORS.get(elem.upper(), GOLD)
                c.setFillColor(elem_color)
                c.setFont("Helvetica-Bold", 10)
                c.drawString(x_start + 165, y_dom, elem.upper())
                
                pct = data.get("percentage", 0) if isinstance(data, dict) else 0
                c.setFillColor(BLACK)
                c.setFont("Helvetica", 9)
                c.drawString(x_start + 210, y_dom, f". {pct}%")
                
                y_dom -= 15
        else:
            # Default if no element scores
            c.setFont("Helvetica", 9)
            c.drawString(x_start + 110, y_dom, f"Dominan I  {dominant_element}")
            c.drawString(x_start + 210, y_dom, ". %")
        
        # Ciri Khas section
        y = y - 80
        c.setFillColor(BLACK)
        c.setFont("Helvetica-Bold", 11)
        c.drawString(x_start, y, "Ciri khas :")
        y -= 15
        
        c.setFont("Helvetica", 9)
        ciri_khas = pdata.get("ciriKhas", [])
        ciri_text = " - ".join(ciri_khas)
        
        # Word wrap
        max_width = 230
        words = ciri_text.split(" - ")
        line = ""
        for word in words:
            test_line = f"{line} - {word}" if line else word
            if c.stringWidth(test_line, "Helvetica", 9) < max_width:
                line = test_line
            else:
                c.drawString(x_start, y, line)
                y -= 12
                line = word
        if line:
            c.drawString(x_start, y, line)
            y -= 12
        
        # Dibutuhkan pada profesi
        y -= 15
        c.setFont("Helvetica-Bold", 11)
        c.drawString(x_start, y, "Dibutuhkan pada profesi :")
        y -= 15
        
        c.setFont("Helvetica", 9)
        profesi = pdata.get("dibutuhkanPadaProfesi", "Yang memerlukan KREATIFITAS & SISTEM")
        c.drawString(x_start, y, profesi)
    
    def _draw_footer(self, c):
        """Draw footer with signature"""
        # Signature area
        sig_x = self.width / 2 + 80
        sig_y = 80
        
        # Signature line
        c.setStrokeColor(BLACK)
        c.line(sig_x, sig_y + 30, sig_x + 120, sig_y + 30)
        
        # Name and title
        c.setFillColor(BLACK)
        c.setFont("Helvetica-Bold", 11)
        c.drawCentredString(sig_x + 60, sig_y + 10, "- ABIE DIBYO -")
        
        c.setFont("Helvetica-Oblique", 10)
        c.setFillColor(DARK_GOLD)
        c.drawCentredString(sig_x + 60, sig_y - 5, "Chairman & B. Development")
        
        # Production by
        c.setFillColor(GRAY)
        c.setFont("Helvetica-Oblique", 8)
        c.drawString(self.width - 100, 20, "Production by")


def generate_certificate_pdf(user_data: dict, analysis_data: dict) -> BytesIO:
    """Public function to generate certificate PDF"""
    generator = CertificateGenerator()
    return generator.generate_certificate(user_data, analysis_data)
