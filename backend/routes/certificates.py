from fastapi import APIRouter, HTTPException, UploadFile, File, Depends, Form
from fastapi.responses import StreamingResponse
from typing import List, Optional
from database import get_db
from datetime import datetime
from bson import ObjectId
from routes.admin import verify_token
import uuid
from pathlib import Path
from io import BytesIO

# PDF Generation imports
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.lib.units import inch, cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.pdfgen import canvas

router = APIRouter(prefix="/api/certificates", tags=["certificates"])
db = get_db()

# Upload directory
UPLOAD_DIR = Path("/app/frontend/public/uploads/certificates")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

@router.get("/template", response_model=dict)
async def get_certificate_template():
    """
    Get certificate template settings
    """
    try:
        template = await db.certificate_templates.find_one()
        if not template:
            # Create default template
            default_template = {
                "backgroundUrl": "",
                "logoUrl": "",
                "signatureUrl": "",
                "signerName": "Director NEWME CLASS",
                "signerTitle": "Direktur",
                "titleText": "SERTIFIKAT",
                "subtitleText": "Diberikan kepada",
                "completionText": "Telah berhasil menyelesaikan",
                "dateFormat": "DD MMMM YYYY",
                "textColor": "#000000",
                "accentColor": "#FFD700",
                "createdAt": datetime.utcnow()
            }
            result = await db.certificate_templates.insert_one(default_template)
            template = await db.certificate_templates.find_one({"_id": result.inserted_id})
        
        template["_id"] = str(template["_id"])
        return template
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@router.put("/template", response_model=dict)
async def update_certificate_template(
    signerName: Optional[str] = Form(None),
    signerTitle: Optional[str] = Form(None),
    titleText: Optional[str] = Form(None),
    subtitleText: Optional[str] = Form(None),
    completionText: Optional[str] = Form(None),
    textColor: Optional[str] = Form(None),
    accentColor: Optional[str] = Form(None),
    token_data: dict = Depends(verify_token)
):
    """
    Update certificate template (admin only)
    """
    try:
        update_data = {}
        
        if signerName is not None:
            update_data["signerName"] = signerName
        if signerTitle is not None:
            update_data["signerTitle"] = signerTitle
        if titleText is not None:
            update_data["titleText"] = titleText
        if subtitleText is not None:
            update_data["subtitleText"] = subtitleText
        if completionText is not None:
            update_data["completionText"] = completionText
        if textColor is not None:
            update_data["textColor"] = textColor
        if accentColor is not None:
            update_data["accentColor"] = accentColor
        
        update_data["updatedAt"] = datetime.utcnow()
        update_data["updatedBy"] = token_data["sub"]
        
        template = await db.certificate_templates.find_one()
        if template:
            await db.certificate_templates.update_one(
                {"_id": template["_id"]},
                {"$set": update_data}
            )
        else:
            update_data["createdAt"] = datetime.utcnow()
            await db.certificate_templates.insert_one(update_data)
        
        return {"success": True, "message": "Template updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@router.post("/template/upload/{asset_type}", response_model=dict)
async def upload_certificate_asset(
    asset_type: str,
    file: UploadFile = File(...),
    token_data: dict = Depends(verify_token)
):
    """
    Upload certificate assets (background, logo, signature)
    """
    try:
        allowed_types = ['background', 'logo', 'signature']
        if asset_type not in allowed_types:
            raise HTTPException(status_code=400, detail="Invalid asset type")
        
        allowed_extensions = {'png', 'jpg', 'jpeg', 'webp'}
        file_extension = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
        
        if file_extension not in allowed_extensions:
            raise HTTPException(status_code=400, detail="File type not allowed")
        
        unique_filename = f"cert_{asset_type}_{uuid.uuid4()}.{file_extension}"
        file_path = UPLOAD_DIR / unique_filename
        
        contents = await file.read()
        with open(file_path, 'wb') as f:
            f.write(contents)
        
        file_url = f"/uploads/certificates/{unique_filename}"
        
        # Update template
        field_map = {
            'background': 'backgroundUrl',
            'logo': 'logoUrl',
            'signature': 'signatureUrl'
        }
        
        template = await db.certificate_templates.find_one()
        if template:
            await db.certificate_templates.update_one(
                {"_id": template["_id"]},
                {"$set": {field_map[asset_type]: file_url, "updatedAt": datetime.utcnow()}}
            )
        
        return {"success": True, "url": file_url, "message": f"{asset_type} uploaded successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@router.get("/issued", response_model=List[dict])
async def get_issued_certificates(
    skip: int = 0,
    limit: int = 50,
    token_data: dict = Depends(verify_token)
):
    """
    Get all issued certificates (admin only)
    """
    try:
        cursor = db.issued_certificates.find().skip(skip).limit(limit).sort("issuedAt", -1)
        certificates = await cursor.to_list(length=limit)
        
        for cert in certificates:
            cert["_id"] = str(cert["_id"])
        
        return certificates
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@router.post("/issue", response_model=dict)
async def issue_certificate(
    userId: str = Form(...),
    courseName: str = Form(...),
    completionDate: Optional[str] = Form(None),
    token_data: dict = Depends(verify_token)
):
    """
    Issue certificate to user (admin only)
    """
    try:
        # Get user info
        user = await db.registrations.find_one({"_id": ObjectId(userId)})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        certificate_data = {
            "userId": userId,
            "userName": user.get("name"),
            "userEmail": user.get("email"),
            "courseName": courseName,
            "certificateNumber": f"NEWME-{datetime.utcnow().strftime('%Y%m%d')}-{uuid.uuid4().hex[:8].upper()}",
            "issuedAt": datetime.utcnow(),
            "completionDate": completionDate or datetime.utcnow().strftime("%Y-%m-%d"),
            "issuedBy": token_data["sub"]
        }
        
        result = await db.issued_certificates.insert_one(certificate_data)
        
        return {
            "success": True,
            "certificateId": str(result.inserted_id),
            "certificateNumber": certificate_data["certificateNumber"],
            "message": "Certificate issued successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@router.get("/verify/{certificate_number}", response_model=dict)
async def verify_certificate(certificate_number: str):
    """
    Verify certificate by number (public)
    """
    try:
        certificate = await db.issued_certificates.find_one({"certificateNumber": certificate_number})
        
        if not certificate:
            return {
                "valid": False,
                "message": "Certificate not found"
            }
        
        return {
            "valid": True,
            "userName": certificate.get("userName"),
            "courseName": certificate.get("courseName"),
            "issuedAt": certificate.get("issuedAt").isoformat() if certificate.get("issuedAt") else None,
            "completionDate": certificate.get("completionDate"),
            "certificateNumber": certificate_number
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


def generate_certificate_pdf(certificate: dict, template: dict) -> BytesIO:
    """
    Generate PDF certificate
    """
    buffer = BytesIO()
    
    # Create landscape A4 PDF
    page_width, page_height = landscape(A4)
    c = canvas.Canvas(buffer, pagesize=landscape(A4))
    
    # Colors from template
    accent_color_hex = template.get("accentColor", "#FFD700")
    text_color_hex = template.get("textColor", "#000000")
    
    # Convert hex to RGB
    def hex_to_rgb(hex_color):
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) / 255.0 for i in (0, 2, 4))
    
    accent_rgb = hex_to_rgb(accent_color_hex)
    text_rgb = hex_to_rgb(text_color_hex)
    
    # Background
    background_url = template.get("backgroundUrl")
    if background_url:
        try:
            bg_path = Path(f"/app/frontend/public{background_url}")
            if bg_path.exists():
                c.drawImage(str(bg_path), 0, 0, width=page_width, height=page_height)
        except:
            pass
    else:
        # Default elegant background
        c.setFillColorRGB(0.98, 0.98, 0.95)
        c.rect(0, 0, page_width, page_height, fill=1)
        
        # Border
        c.setStrokeColorRGB(*accent_rgb)
        c.setLineWidth(3)
        c.rect(30, 30, page_width - 60, page_height - 60, stroke=1, fill=0)
        
        # Inner border
        c.setLineWidth(1)
        c.rect(40, 40, page_width - 80, page_height - 80, stroke=1, fill=0)
    
    # Logo
    logo_url = template.get("logoUrl")
    if logo_url:
        try:
            logo_path = Path(f"/app/frontend/public{logo_url}")
            if logo_path.exists():
                c.drawImage(str(logo_path), page_width/2 - 40, page_height - 120, width=80, height=80, preserveAspectRatio=True)
        except:
            pass
    
    # Title
    title_text = template.get("titleText", "SERTIFIKAT")
    c.setFillColorRGB(*accent_rgb)
    c.setFont("Helvetica-Bold", 48)
    c.drawCentredString(page_width/2, page_height - 160, title_text)
    
    # Subtitle
    subtitle_text = template.get("subtitleText", "Diberikan kepada")
    c.setFillColorRGB(*text_rgb)
    c.setFont("Helvetica", 18)
    c.drawCentredString(page_width/2, page_height - 200, subtitle_text)
    
    # Recipient Name
    recipient_name = certificate.get("userName", "")
    c.setFillColorRGB(*text_rgb)
    c.setFont("Helvetica-Bold", 36)
    c.drawCentredString(page_width/2, page_height - 260, recipient_name)
    
    # Decorative line under name
    c.setStrokeColorRGB(*accent_rgb)
    c.setLineWidth(2)
    name_width = c.stringWidth(recipient_name, "Helvetica-Bold", 36)
    c.line(page_width/2 - name_width/2 - 20, page_height - 275, 
           page_width/2 + name_width/2 + 20, page_height - 275)
    
    # Completion text
    completion_text = template.get("completionText", "Telah berhasil menyelesaikan")
    c.setFillColorRGB(*text_rgb)
    c.setFont("Helvetica", 16)
    c.drawCentredString(page_width/2, page_height - 310, completion_text)
    
    # Course name
    course_name = certificate.get("courseName", "")
    c.setFont("Helvetica-Bold", 24)
    c.drawCentredString(page_width/2, page_height - 350, course_name)
    
    # Date
    completion_date = certificate.get("completionDate", "")
    if completion_date:
        c.setFont("Helvetica", 14)
        c.drawCentredString(page_width/2, page_height - 390, f"Pada tanggal: {completion_date}")
    
    # Certificate number
    cert_number = certificate.get("certificateNumber", "")
    c.setFont("Helvetica", 12)
    c.setFillColorRGB(0.5, 0.5, 0.5)
    c.drawCentredString(page_width/2, 80, f"No. Sertifikat: {cert_number}")
    
    # Signature section
    signer_name = template.get("signerName", "Director NEWME CLASS")
    signer_title = template.get("signerTitle", "Direktur")
    
    # Signature image
    signature_url = template.get("signatureUrl")
    if signature_url:
        try:
            sig_path = Path(f"/app/frontend/public{signature_url}")
            if sig_path.exists():
                c.drawImage(str(sig_path), page_width/2 - 50, 120, width=100, height=50, preserveAspectRatio=True)
        except:
            pass
    
    # Signature line
    c.setStrokeColorRGB(*text_rgb)
    c.setLineWidth(1)
    c.line(page_width/2 - 80, 115, page_width/2 + 80, 115)
    
    # Signer info
    c.setFillColorRGB(*text_rgb)
    c.setFont("Helvetica-Bold", 14)
    c.drawCentredString(page_width/2, 95, signer_name)
    c.setFont("Helvetica", 12)
    c.drawCentredString(page_width/2, 75, signer_title)
    
    c.save()
    buffer.seek(0)
    return buffer


def generate_ai_certificate_pdf(user: dict, ai_analysis: dict, template: dict) -> BytesIO:
    """
    Generate PDF certificate sesuai template NEWME CLASS
    Template: IMG-20260205-WA0012.jpg
    """
    buffer = BytesIO()
    
    page_width, page_height = landscape(A4)
    c = canvas.Canvas(buffer, pagesize=landscape(A4))
    
    # Colors matching template exactly
    gold_rgb = (0.85, 0.65, 0.13)  # Gold/Yellow accent
    black_rgb = (0.1, 0.1, 0.1)
    white_rgb = (1, 1, 1)
    cream_rgb = (0.99, 0.98, 0.95)  # Very light cream/white background
    blue_rgb = (0.2, 0.5, 0.7)  # NEW ME logo blue
    
    def draw_wrapped_text(c, text, x, y, max_width, font_name, font_size, line_height=None):
        """Helper to draw wrapped text"""
        if line_height is None:
            line_height = font_size + 2
        c.setFont(font_name, font_size)
        words = str(text).split()
        lines = []
        current_line = ""
        for word in words:
            test_line = current_line + " " + word if current_line else word
            if c.stringWidth(test_line, font_name, font_size) < max_width:
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = word
        if current_line:
            lines.append(current_line)
        
        for line in lines:
            c.drawString(x, y, line)
            y -= line_height
        return y
    
    # ========== PAGE 1: Main Certificate ==========
    
    # White/cream background
    c.setFillColorRGB(*cream_rgb)
    c.rect(0, 0, page_width, page_height, fill=1)
    
    # ===== TOP LEFT: Black diagonal with yellow dots =====
    path = c.beginPath()
    path.moveTo(0, page_height)
    path.lineTo(180, page_height)
    path.lineTo(0, page_height - 120)
    path.close()
    c.setFillColorRGB(*black_rgb)
    c.drawPath(path, fill=1, stroke=0)
    
    # Yellow dots pattern in black area
    c.setFillColorRGB(*gold_rgb)
    for row in range(8):
        for col in range(12):
            dot_x = 60 + col * 10
            dot_y = page_height - 15 - row * 10
            # Only draw dots that are within the black triangle area
            if dot_x < (180 - row * 15):
                c.circle(dot_x, dot_y, 2, fill=1)
    
    # ===== TOP CENTER: Two oval logos =====
    # Oval 1: Logo WARNA elemen (left oval)
    oval1_x, oval1_y = 230, page_height - 55
    c.setStrokeColorRGB(*black_rgb)
    c.setLineWidth(2)
    c.ellipse(oval1_x - 50, oval1_y - 30, oval1_x + 50, oval1_y + 30, stroke=1, fill=0)
    c.setFillColorRGB(*black_rgb)
    c.setFont("Helvetica", 10)
    c.drawCentredString(oval1_x, oval1_y + 8, "Logo")
    c.drawCentredString(oval1_x, oval1_y - 5, "WARNA")
    c.drawCentredString(oval1_x, oval1_y - 18, "elemen")
    
    # Oval 2: Logo NEWME (right oval)
    oval2_x, oval2_y = 350, page_height - 55
    c.ellipse(oval2_x - 45, oval2_y - 30, oval2_x + 45, oval2_y + 30, stroke=1, fill=0)
    c.drawCentredString(oval2_x, oval2_y + 5, "Logo")
    c.drawCentredString(oval2_x, oval2_y - 10, "NEWME")
    
    # Get analysis data
    personality_type = ai_analysis.get("personalityType", "AMBIVERT")
    dominant_element = ai_analysis.get("dominantElement", "AIR")
    dominant_type = ai_analysis.get("dominantType", "SI ADAPTIF")
    result_category = ai_analysis.get("resultCategory", "aAi")
    element_scores = ai_analysis.get("elementScores", {})
    recipient_name = user.get("fullName", "Pengguna")
    
    # Get dominant percentage
    dominant_pct = 0
    dominant_label = dominant_type
    if dominant_element in element_scores:
        dominant_pct = element_scores[dominant_element].get("percentage", 0)
        dominant_label = element_scores[dominant_element].get("label", dominant_type)
    
    # ===== TOP RIGHT: Title section =====
    c.setFillColorRGB(*black_rgb)
    c.setFont("Helvetica-Bold", 32)
    c.drawRightString(page_width - 40, page_height - 45, "SERTIFIKAT")
    c.setFont("Helvetica", 12)
    c.drawRightString(page_width - 40, page_height - 65, "ANALISA KEPRIBADIAN & JATIDIRI")
    
    # ID field
    cert_id = f"NM-{datetime.utcnow().strftime('%Y%m%d')}-{str(user.get('_id', ''))[-6:].upper()}"
    c.setFont("Helvetica", 10)
    c.drawRightString(page_width - 40, page_height - 90, f"ID {cert_id}")
    
    # Dotted line under ID
    c.setStrokeColorRGB(0.5, 0.5, 0.5)
    c.setDash(2, 2)
    c.line(page_width - 200, page_height - 95, page_width - 40, page_height - 95)
    c.setDash()
    
    # Tagline
    c.setFillColorRGB(*gold_rgb)
    c.setFont("Helvetica-Oblique", 11)
    c.drawRightString(page_width - 40, page_height - 115, "Optimalkan versi terbaik_mu")
    
    # ========== Two Column Layout ==========
    col1_x = 50  # Left column
    col2_x = page_width / 2 + 30  # Right column
    y_start = page_height - 160
    
    # ===== LEFT COLUMN =====
    # Kepribadian section
    c.setFillColorRGB(*black_rgb)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(col1_x, y_start, "Kepribadian :")
    
    kepribadian_desc = ai_analysis.get("kepribadian", [
        "Extra Responsif", "bahasa IMAGINASI", "kurang investigatif",
        "extra pasif", "lebih sensitif", "mudah tersinggung"
    ])
    y = y_start - 15
    c.setFont("Helvetica", 8)
    kepribadian_text = ", ".join(kepribadian_desc[:6])
    y = draw_wrapped_text(c, kepribadian_text, col1_x, y, 280, "Helvetica", 8, 11)
    
    # +/- Karakter section
    y -= 15
    c.setFont("Helvetica-Bold", 10)
    c.drawString(col1_x, y, "+/- Karakter :")
    y -= 13
    c.setFont("Helvetica", 7)
    karakter = ai_analysis.get("karakter", [
        "Pemerhati", "suka beda", "imaginatif", "suka hal baru",
        "percaya diri", "romantis", "perfectionis", "penuntut idealisme"
    ])
    karakter_text = " - ".join(karakter[:10])
    y = draw_wrapped_text(c, karakter_text, col1_x, y, 280, "Helvetica", 7, 10)
    
    # Kekuatan Jatidiri section
    y -= 15
    c.setFont("Helvetica-Bold", 10)
    c.drawString(col1_x, y, f"Kekuatan Jatidiri : {dominant_label}")
    
    kekuatan = ai_analysis.get("kekuatanJatidiri", {})
    y -= 15
    c.setFont("Helvetica", 8)
    jatidiri_items = [
        f"Kehidupan : {kekuatan.get('kehidupan', 'KAYA GAGASAN')}",
        f"Kesehatan : {kekuatan.get('kesehatan', 'PENCERNAAN')}",
        f"Kontribusi : {kekuatan.get('kontribusi', 'KREATIFITAS')}",
        f"Kekhasan : {kekuatan.get('kekhasan', 'BERBEDA')}",
        f"Kharisma : {kekuatan.get('kharisma', 'INSPIRATIF')}"
    ]
    for item in jatidiri_items:
        c.drawString(col1_x, y, item)
        y -= 11
    
    # Kompilasi Adaptasi section
    y -= 10
    c.setFont("Helvetica-Bold", 10)
    c.drawString(col1_x, y, "Kompilasi Adaptasi :")
    y -= 13
    c.setFont("Helvetica", 7)
    
    kompilasi = ai_analysis.get("kompilasiAdaptasi", [
        "Belajar: Mengimajinasikan", "Bekerja: Bebas", "Kalibrasi: Variasi",
        "Daya Raga: Tidur/nonton", "Memimpin: Organisasi Cipta", "Jalur Bisnis: Owner",
        "Pendukung karir: Komunikator", "Keahlian: Negosiator", "Karya: Inovatif",
        "Keunggulan: Menggambarkan", "Keutamaan: Kesempurnaan", "Tanggung jawab: Magnet"
    ])
    
    for i, item in enumerate(kompilasi[:12]):
        c.drawString(col1_x, y, f"• {item}")
        y -= 9
    
    # ===== RIGHT COLUMN =====
    # Big Symbol Display (like eK, iA, etc)
    symbol_code = result_category if result_category else f"{personality_type[0].lower()}{dominant_element[0].upper()}"
    
    # Draw big parentheses with symbol
    c.setFillColorRGB(*gold_rgb)
    c.setFont("Helvetica-Bold", 72)
    c.drawCentredString(col2_x + 100, y_start - 50, f"({symbol_code})")
    
    # Kepribadian type
    c.setFillColorRGB(*black_rgb)
    c.setFont("Helvetica", 10)
    c.drawString(col2_x + 20, y_start - 100, "Kepribadian :")
    c.setFillColorRGB(*gold_rgb)
    c.setFont("Helvetica-Bold", 18)
    c.drawString(col2_x + 20, y_start - 120, personality_type)
    
    # Simbol Jatidiri section
    y = y_start - 150
    c.setFillColorRGB(*black_rgb)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(col2_x + 20, y, "Simbol Jatidiri :")
    
    # Show dominant elements with percentages
    y -= 18
    c.setFont("Helvetica", 9)
    
    # Sort elements by percentage
    sorted_elements = sorted(element_scores.items(), key=lambda x: x[1].get('percentage', 0), reverse=True)
    
    for i, (elem, data) in enumerate(sorted_elements[:3]):
        pct = data.get('percentage', 0)
        label = data.get('label', '')
        c.setFont("Helvetica-Bold", 10)
        c.drawString(col2_x + 20, y, f"Dominan {['I', 'II', 'III'][i]}")
        c.setFillColorRGB(*gold_rgb)
        c.drawString(col2_x + 80, y, elem)
        c.setFillColorRGB(*black_rgb)
        c.setFont("Helvetica", 9)
        c.drawString(col2_x + 130, y, f"{pct:.2f} %")
        y -= 18
    
    # Ciri khas section
    y -= 10
    c.setFont("Helvetica-Bold", 10)
    c.drawString(col2_x + 20, y, "Ciri khas :")
    y -= 15
    c.setFont("Helvetica", 8)
    ciri_khas = ai_analysis.get("ciriKhas", [
        "Menarik", "Tampil Beda", "Charming",
        "Berat Badan cenderung stabil", "Bicara nambah wawasan"
    ])
    for ciri in ciri_khas[:5]:
        c.drawString(col2_x + 20, y, f"• {ciri}")
        y -= 11
    
    # Dibutuhkan pada profesi
    y -= 10
    c.setFont("Helvetica-Bold", 10)
    c.drawString(col2_x + 20, y, "Dibutuhkan pada profesi :")
    y -= 13
    c.setFont("Helvetica", 8)
    profesi_text = f"Yang memerlukan {kekuatan.get('kontribusi', 'KREATIFITAS')} & SISTEM"
    c.drawString(col2_x + 20, y, profesi_text)
    
    # ===== FOOTER =====
    # NEW ME logo small (bottom left)
    c.setFillColorRGB(*black_rgb)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, 70, "NEW ME")
    c.setFont("Helvetica", 7)
    c.drawString(50, 58, "Jatidiri di sini")
    
    # Signature section
    c.setFont("Helvetica", 10)
    c.drawString(150, 70, "_________________")
    c.setFont("Helvetica-Bold", 10)
    c.drawString(150, 55, "- ABIE DIBYO -")
    c.setFont("Helvetica", 8)
    c.drawString(150, 43, "Chairman & B. Development")
    
    # Production info (bottom right)
    c.setFont("Helvetica", 7)
    c.drawRightString(page_width - 60, 45, "Production by")
    c.setFont("Helvetica-Bold", 9)
    c.drawRightString(page_width - 60, 32, "S L")
    
    # Note
    c.setFillColorRGB(0.5, 0.5, 0.5)
    c.setFont("Helvetica-Oblique", 6)
    c.drawString(50, 25, "Catt: Point positif only, negatif by private.")
    
    # ========== PAGE 2: Detailed Analysis ==========
    c.showPage()
    
    # Background
    c.setFillColorRGB(1, 1, 0.97)
    c.rect(0, 0, page_width, page_height, fill=1)
    
    # Header bars
    c.setFillColorRGB(*gold_rgb)
    c.rect(0, page_height - 20, page_width, 20, fill=1)
    c.rect(0, 0, page_width, 20, fill=1)
    
    # Border
    c.setStrokeColorRGB(*gold_rgb)
    c.setLineWidth(1)
    c.rect(15, 25, page_width - 30, page_height - 50, stroke=1, fill=0)
    
    # Title
    c.setFillColorRGB(*black_rgb)
    c.setFont("Helvetica-Bold", 20)
    c.drawCentredString(page_width/2, page_height - 50, "LAPORAN ANALISIS AI")
    c.setFont("Helvetica", 11)
    c.drawCentredString(page_width/2, page_height - 68, f"Untuk: {recipient_name}")
    
    # Two column layout
    col_width = (page_width - 100) / 2
    col1_x = 50
    col2_x = page_width/2 + 20
    y_start = page_height - 100
    
    # Left Column
    c.setFillColorRGB(*gold_rgb)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(col1_x, y_start, "KEKUATAN ANDA")
    
    y = y_start - 20
    c.setFillColorRGB(*black_rgb)
    c.setFont("Helvetica", 9)
    for strength in ai_analysis.get("strengths", [])[:6]:
        c.drawString(col1_x + 10, y, f"• {strength[:55]}")
        y -= 14
    
    y -= 15
    c.setFillColorRGB(*gold_rgb)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(col1_x, y, "AREA PENGEMBANGAN")
    y -= 20
    c.setFillColorRGB(*black_rgb)
    c.setFont("Helvetica", 9)
    for area in ai_analysis.get("areasToImprove", [])[:5]:
        c.drawString(col1_x + 10, y, f"• {area[:55]}")
        y -= 14
    
    # Right Column
    y = y_start
    c.setFillColorRGB(*gold_rgb)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(col2_x, y, "REKOMENDASI KARIR")
    y -= 20
    c.setFillColorRGB(*black_rgb)
    c.setFont("Helvetica", 9)
    for career in ai_analysis.get("careerRecommendations", [])[:7]:
        c.drawString(col2_x + 10, y, f"• {career[:45]}")
        y -= 14
    
    y -= 15
    c.setFillColorRGB(*gold_rgb)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(col2_x, y, "TIPS PENGEMBANGAN")
    y -= 20
    c.setFillColorRGB(*black_rgb)
    c.setFont("Helvetica", 9)
    for i, tip in enumerate(ai_analysis.get("tips", [])[:6], 1):
        c.drawString(col2_x + 10, y, f"{i}. {tip[:50]}")
        y -= 14
    
    # Summary box at bottom
    summary = ai_analysis.get("summary", "")
    if summary:
        y = 120
        c.setFillColorRGB(0.95, 0.95, 0.90)
        c.rect(50, 50, page_width - 100, 70, fill=1)
        c.setStrokeColorRGB(*gold_rgb)
        c.rect(50, 50, page_width - 100, 70, stroke=1, fill=0)
        
        c.setFillColorRGB(*black_rgb)
        c.setFont("Helvetica-Bold", 10)
        c.drawString(60, 105, "RINGKASAN:")
        c.setFont("Helvetica", 9)
        draw_wrapped_text(c, summary, 60, 90, page_width - 130, "Helvetica", 9, 12)
    
    # Footer
    c.setFillColorRGB(0.5, 0.5, 0.5)
    c.setFont("Helvetica", 7)
    c.drawCentredString(page_width/2, 35, "Sertifikat ini dihasilkan berdasarkan analisis AI dari jawaban test kepribadian Anda.")
    c.drawCentredString(page_width/2, 25, f"© NEWME CLASS - Jatidirimu di Sini | Diterbitkan: {datetime.utcnow().strftime('%d %B %Y')}")
    
    c.save()
    buffer.seek(0)
    return buffer


@router.get("/download/{certificate_number}")
async def download_certificate(certificate_number: str):
    """
    Download certificate as PDF (public)
    """
    try:
        certificate = await db.issued_certificates.find_one({"certificateNumber": certificate_number})
        
        if not certificate:
            raise HTTPException(status_code=404, detail="Certificate not found")
        
        # Get template
        template = await db.certificate_templates.find_one()
        if not template:
            template = {
                "titleText": "SERTIFIKAT",
                "subtitleText": "Diberikan kepada",
                "completionText": "Telah berhasil menyelesaikan",
                "signerName": "Director NEWME CLASS",
                "signerTitle": "Direktur",
                "textColor": "#000000",
                "accentColor": "#FFD700"
            }
        
        # Generate PDF
        pdf_buffer = generate_certificate_pdf(certificate, template)
        
        return StreamingResponse(
            pdf_buffer,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=certificate_{certificate_number}.pdf"
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


from routes.auth import get_current_user

@router.get("/download-ai-certificate")
async def download_ai_certificate(current_user: dict = Depends(get_current_user)):
    """
    Download AI analysis certificate - ONLY for PAID test users
    """
    try:
        user_id = str(current_user["_id"])
        
        # Check if user has paid for test from payments collection
        payment = await db.payments.find_one({
            "userId": user_id,
            "status": "approved",
            "type": {"$in": ["test", "paid_test", "premium_test"]}
        })
        
        # Also check user's paymentStatus field
        user_paid = current_user.get("paymentStatus") == "approved" or current_user.get("paidTestStatus") == "completed"
        
        if not payment and not user_paid:
            raise HTTPException(
                status_code=403, 
                detail="Sertifikat hanya tersedia untuk pengguna yang telah membayar test. Silakan upgrade ke Test Premium."
            )
        
        # Get latest AI analysis
        ai_analysis_doc = await db.ai_analyses.find_one(
            {"userId": user_id},
            sort=[("createdAt", -1)]
        )
        
        if not ai_analysis_doc:
            raise HTTPException(
                status_code=404,
                detail="Belum ada hasil analisis AI. Silakan selesaikan test terlebih dahulu."
            )
        
        ai_analysis = ai_analysis_doc.get("aiAnalysis", {})
        if not ai_analysis:
            ai_analysis = {
                "personalityType": ai_analysis_doc.get("personalityType", ""),
                "summary": ai_analysis_doc.get("summary", ""),
                "strengths": ai_analysis_doc.get("strengths", []),
                "areasToImprove": ai_analysis_doc.get("areasToImprove", []),
                "careerRecommendations": ai_analysis_doc.get("careerRecommendations", []),
                "tips": ai_analysis_doc.get("tips", [])
            }
        
        # Get certificate template
        template = await db.certificate_templates.find_one()
        if not template:
            template = {
                "signerName": "Director NEWME CLASS",
                "textColor": "#000000",
                "accentColor": "#FFD700"
            }
        
        # Generate PDF
        pdf_buffer = generate_ai_certificate_pdf(current_user, ai_analysis, template)
        
        filename = f"sertifikat_ai_{current_user.get('fullName', 'user').replace(' ', '_')}_{datetime.utcnow().strftime('%Y%m%d')}.pdf"
        
        return StreamingResponse(
            pdf_buffer,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@router.get("/check-eligibility")
async def check_certificate_eligibility(current_user: dict = Depends(get_current_user)):
    """
    Check if user is eligible to download AI certificate
    """
    try:
        user_id = str(current_user["_id"])
        
        # Check payment from payments collection
        payment = await db.payments.find_one({
            "userId": user_id,
            "status": "approved",
            "type": {"$in": ["test", "paid_test", "premium_test"]}
        })
        
        # Also check user's paymentStatus field
        user_paid = current_user.get("paymentStatus") == "approved" or current_user.get("paidTestStatus") == "completed"
        
        has_paid = payment is not None or user_paid
        
        # Check AI analysis
        ai_analysis = await db.ai_analyses.find_one({"userId": user_id})
        has_analysis = ai_analysis is not None
        
        # Check free test usage
        free_test = await db.test_results.find_one({
            "userId": user_id,
            "testType": "free"
        })
        has_used_free_test = free_test is not None
        
        return {
            "hasPaid": has_paid,
            "hasAnalysis": has_analysis,
            "hasUsedFreeTest": has_used_free_test,
            "canDownloadCertificate": has_paid and has_analysis,
            "message": "Eligible to download certificate" if (has_paid and has_analysis) else "Upgrade ke Test Premium untuk download sertifikat"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@router.get("/generate-newme/{user_id}")
async def generate_newme_certificate(user_id: str):
    """
    Generate NEWME CLASS personality certificate PDF for user
    """
    try:
        from certificate_generator import generate_certificate_pdf
        
        # Get user info
        user = None
        if ObjectId.is_valid(user_id):
            user = await db.users.find_one({"_id": ObjectId(user_id)})
        
        if not user:
            raise HTTPException(status_code=404, detail="User tidak ditemukan")
        
        # Check if user has paid
        if user.get("paymentStatus") != "approved":
            raise HTTPException(status_code=403, detail="Silakan selesaikan pembayaran untuk download sertifikat")
        
        # Get AI analysis result
        ai_analysis = await db.ai_analyses.find_one({
            "userId": user_id,
            "testType": "paid"
        }, sort=[("createdAt", -1)])
        
        if not ai_analysis:
            raise HTTPException(status_code=404, detail="Hasil analisis tidak ditemukan. Silakan selesaikan test premium.")
        
        # Prepare user data for certificate
        user_data = {
            "fullName": user.get("fullName", "Peserta"),
            "email": user.get("email", ""),
            "certificateId": f"NM-{datetime.utcnow().strftime('%Y%m%d')}-{user_id[-6:].upper()}"
        }
        
        # Prepare analysis data
        analysis_data = ai_analysis.get("aiAnalysis", {})
        
        # Generate PDF
        pdf_buffer = generate_certificate_pdf(user_data, analysis_data)
        
        # Record certificate issuance
        cert_record = {
            "userId": user_id,
            "userName": user.get("fullName"),
            "userEmail": user.get("email"),
            "certificateId": user_data["certificateId"],
            "certificateType": "personality",
            "personalityCode": analysis_data.get("resultCategory", ""),
            "dominantElement": analysis_data.get("dominantElement", ""),
            "personalityType": analysis_data.get("personalityType", ""),
            "generatedAt": datetime.utcnow()
        }
        
        await db.issued_certificates.insert_one(cert_record)
        
        # Return PDF as download
        return StreamingResponse(
            pdf_buffer,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=Sertifikat_NEWME_{user.get('fullName', 'Peserta').replace(' ', '_')}.pdf"
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating certificate: {str(e)}")


@router.get("/preview-newme/{user_id}")
async def preview_newme_certificate(user_id: str):
    """
    Preview NEWME CLASS personality certificate (inline display, not download)
    """
    try:
        from certificate_generator import generate_certificate_pdf
        
        # Get user info
        user = None
        if ObjectId.is_valid(user_id):
            user = await db.users.find_one({"_id": ObjectId(user_id)})
        
        if not user:
            raise HTTPException(status_code=404, detail="User tidak ditemukan")
        
        # Get AI analysis result
        ai_analysis = await db.ai_analyses.find_one({
            "userId": user_id,
            "testType": "paid"
        }, sort=[("createdAt", -1)])
        
        if not ai_analysis:
            # Try to get analysis from lastAnalysis field
            if user.get("lastAnalysis"):
                analysis_data = user.get("lastAnalysis")
            else:
                raise HTTPException(status_code=404, detail="Hasil analisis tidak ditemukan")
        else:
            analysis_data = ai_analysis.get("aiAnalysis", {})
        
        # Prepare user data for certificate
        user_data = {
            "fullName": user.get("fullName", "Peserta"),
            "email": user.get("email", ""),
            "certificateId": f"NM-{datetime.utcnow().strftime('%Y%m%d')}-{user_id[-6:].upper()}"
        }
        
        # Generate PDF
        pdf_buffer = generate_certificate_pdf(user_data, analysis_data)
        
        # Return PDF for inline viewing
        return StreamingResponse(
            pdf_buffer,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"inline; filename=Sertifikat_Preview.pdf"
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating preview: {str(e)}")
