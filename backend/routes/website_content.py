from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer
from typing import List, Optional
from pydantic import BaseModel
from database import get_db
from datetime import datetime
from bson import ObjectId

router = APIRouter(prefix="/api/website-content", tags=["website-content"])
security = HTTPBearer()

db = get_db()

# Models
class SlideContent(BaseModel):
    title: str
    subtitle: str
    description: str
    badge: str
    imageUrl: str
    ctaText: str
    ctaLink: str
    order: int = 0
    isActive: bool = True

class ProductContent(BaseModel):
    title: str
    subtitle: str
    imageUrl: str
    link: str
    badge: str = ""
    order: int = 0
    isActive: bool = True

class TestimonialContent(BaseModel):
    name: str
    organization: str
    role: str
    imageUrl: str
    text: str
    rating: int = 5
    order: int = 0
    isActive: bool = True

class ActivityContent(BaseModel):
    title: str
    imageUrl: str
    link: str
    order: int = 0
    isActive: bool = True

class SectionImage(BaseModel):
    sectionName: str  # about, services-corporate, services-individual, etc
    imageUrl: str
    altText: str = ""

# Hero Slides CRUD
@router.get("/hero-slides")
async def get_hero_slides():
    try:
        slides = await db.hero_slides.find({"isActive": True}).sort("order", 1).to_list(100)
        for slide in slides:
            slide["_id"] = str(slide["_id"])
        return slides
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/hero-slides")
async def create_hero_slide(slide: SlideContent):
    try:
        slide_dict = slide.dict()
        slide_dict["createdAt"] = datetime.utcnow()
        result = await db.hero_slides.insert_one(slide_dict)
        return {"id": str(result.inserted_id), "message": "Slide created successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/hero-slides/{slide_id}")
async def update_hero_slide(slide_id: str, slide: SlideContent):
    try:
        result = await db.hero_slides.update_one(
            {"_id": ObjectId(slide_id)},
            {"$set": slide.dict()}
        )
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Slide not found")
        return {"message": "Slide updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/hero-slides/{slide_id}")
async def delete_hero_slide(slide_id: str):
    try:
        result = await db.hero_slides.delete_one({"_id": ObjectId(slide_id)})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Slide not found")
        return {"message": "Slide deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Products CRUD
@router.get("/products")
async def get_products():
    try:
        products = await db.website_products.find({"isActive": True}).sort("order", 1).to_list(100)
        for product in products:
            product["_id"] = str(product["_id"])
        return products
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/products")
async def create_product(product: ProductContent):
    try:
        product_dict = product.dict()
        product_dict["createdAt"] = datetime.utcnow()
        result = await db.website_products.insert_one(product_dict)
        return {"id": str(result.inserted_id), "message": "Product created successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/products/{product_id}")
async def update_product(product_id: str, product: ProductContent):
    try:
        result = await db.website_products.update_one(
            {"_id": ObjectId(product_id)},
            {"$set": product.dict()}
        )
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Product not found")
        return {"message": "Product updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/products/{product_id}")
async def delete_product(product_id: str):
    try:
        result = await db.website_products.delete_one({"_id": ObjectId(product_id)})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Product not found")
        return {"message": "Product deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Testimonials CRUD
@router.get("/testimonials")
async def get_testimonials():
    try:
        testimonials = await db.website_testimonials.find({"isActive": True}).sort("order", 1).to_list(100)
        for t in testimonials:
            t["_id"] = str(t["_id"])
        return testimonials
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/testimonials")
async def create_testimonial(testimonial: TestimonialContent):
    try:
        t_dict = testimonial.dict()
        t_dict["createdAt"] = datetime.utcnow()
        result = await db.website_testimonials.insert_one(t_dict)
        return {"id": str(result.inserted_id), "message": "Testimonial created successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/testimonials/{testimonial_id}")
async def update_testimonial(testimonial_id: str, testimonial: TestimonialContent):
    try:
        result = await db.website_testimonials.update_one(
            {"_id": ObjectId(testimonial_id)},
            {"$set": testimonial.dict()}
        )
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Testimonial not found")
        return {"message": "Testimonial updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/testimonials/{testimonial_id}")
async def delete_testimonial(testimonial_id: str):
    try:
        result = await db.website_testimonials.delete_one({"_id": ObjectId(testimonial_id)})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Testimonial not found")
        return {"message": "Testimonial deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Activities CRUD
@router.get("/activities")
async def get_activities():
    try:
        activities = await db.website_activities.find({"isActive": True}).sort("order", 1).to_list(100)
        for a in activities:
            a["_id"] = str(a["_id"])
        return activities
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/activities")
async def create_activity(activity: ActivityContent):
    try:
        a_dict = activity.dict()
        a_dict["createdAt"] = datetime.utcnow()
        result = await db.website_activities.insert_one(a_dict)
        return {"id": str(result.inserted_id), "message": "Activity created successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/activities/{activity_id}")
async def update_activity(activity_id: str, activity: ActivityContent):
    try:
        result = await db.website_activities.update_one(
            {"_id": ObjectId(activity_id)},
            {"$set": activity.dict()}
        )
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Activity not found")
        return {"message": "Activity updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/activities/{activity_id}")
async def delete_activity(activity_id: str):
    try:
        result = await db.website_activities.delete_one({"_id": ObjectId(activity_id)})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Activity not found")
        return {"message": "Activity deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Section Images CRUD (for about, services, etc)
@router.get("/section-images")
async def get_section_images():
    try:
        images = await db.section_images.find({}).to_list(100)
        for img in images:
            img["_id"] = str(img["_id"])
        return images
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/section-images/{section_name}")
async def get_section_image(section_name: str):
    try:
        image = await db.section_images.find_one({"sectionName": section_name})
        if image:
            image["_id"] = str(image["_id"])
        return image
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/section-images")
async def create_or_update_section_image(image: SectionImage):
    try:
        result = await db.section_images.update_one(
            {"sectionName": image.sectionName},
            {"$set": image.dict(), "$setOnInsert": {"createdAt": datetime.utcnow()}},
            upsert=True
        )
        return {"message": "Section image saved successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Seed default data
@router.post("/seed-defaults")
async def seed_default_content():
    try:
        # Check if already seeded
        existing_slides = await db.hero_slides.count_documents({})
        if existing_slides > 0:
            return {"message": "Data already exists", "seeded": False}
        
        # Default hero slides
        default_slides = [
            {
                "title": "COMPANY PROFILE",
                "subtitle": "NEWMECLASS",
                "description": "Kami, perusahaan edukasi peduli minat bakat, yang berinovasi dengan tambahan strategi membangun jejaring komunitas.",
                "badge": "Kelas Peduli Talenta",
                "imageUrl": "https://images.unsplash.com/photo-1522202176988-66273c2fd55f?w=800&q=80",
                "ctaText": "www.newmeclass.com",
                "ctaLink": "/",
                "order": 0,
                "isActive": True,
                "createdAt": datetime.utcnow()
            },
            {
                "title": "SIAPA KAMI?",
                "subtitle": "PT. MITRA SEMESTA EDUCLASS",
                "description": "NEWMECLASS adalah sebuah brand dan produk dari PT. MITRA SEMESTA EDUCLASS, yang bergerak dengan produk Edukasi dan Komunitas.",
                "badge": "B to B & B to C",
                "imageUrl": "https://images.unsplash.com/photo-1551434678-e076c223a692?w=800&q=80",
                "ctaText": "Pelajari Lebih Lanjut",
                "ctaLink": "/company-profile",
                "order": 1,
                "isActive": True,
                "createdAt": datetime.utcnow()
            },
            {
                "title": "PRODUK USAHA",
                "subtitle": "NIB: 2805240064989",
                "description": "Berbagai produk dan layanan edukasi untuk pengembangan potensi diri dan bakat alami Anda.",
                "badge": "Terdaftar Resmi",
                "imageUrl": "https://images.unsplash.com/photo-1552664730-d307ca884978?w=800&q=80",
                "ctaText": "Lihat Produk",
                "ctaLink": "/shop",
                "order": 2,
                "isActive": True,
                "createdAt": datetime.utcnow()
            },
            {
                "title": "VISI & MISI",
                "subtitle": "NEWME CLASS",
                "description": "Menjadi bagian dari kemajuan bangsa lewat peran EDUKASI JATIDIRI di berbagai lembaga dan organisasi.",
                "badge": "PT. MITRA SEMESTA EDUCLASS",
                "imageUrl": "https://images.unsplash.com/photo-1523240795612-9a054b0db644?w=800&q=80",
                "ctaText": "Lihat Visi Misi",
                "ctaLink": "/company-profile",
                "order": 3,
                "isActive": True,
                "createdAt": datetime.utcnow()
            }
        ]
        await db.hero_slides.insert_many(default_slides)
        
        # Default products
        default_products = [
            {"title": "NEWME TEST", "subtitle": "Tes Kepribadian 5 Element", "imageUrl": "https://images.unsplash.com/photo-1434030216411-0b793f4b4173?w=400&q=80", "link": "/newme-test", "badge": "Popular", "order": 0, "isActive": True, "createdAt": datetime.utcnow()},
            {"title": "KELAS GALI BAKAT", "subtitle": "Program Pengembangan Potensi", "imageUrl": "https://images.unsplash.com/photo-1524178232363-1fb2b075b655?w=400&q=80", "link": "/kelas-gali-bakat", "badge": "B to B", "order": 1, "isActive": True, "createdAt": datetime.utcnow()},
            {"title": "NEWME CLINIC", "subtitle": "Konseling Individual", "imageUrl": "https://images.unsplash.com/photo-1573497620053-ea5300f94f21?w=400&q=80", "link": "/services/clinic", "badge": "B to C", "order": 2, "isActive": True, "createdAt": datetime.utcnow()},
            {"title": "NEWME CLASS", "subtitle": "Pelatihan & Workshop", "imageUrl": "https://images.unsplash.com/photo-1552664730-d307ca884978?w=400&q=80", "link": "/services/class", "badge": "B to B", "order": 3, "isActive": True, "createdAt": datetime.utcnow()},
            {"title": "MERCHANDISE", "subtitle": "Produk Komunitas NMC", "imageUrl": "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=400&q=80", "link": "/shop", "badge": "New", "order": 4, "isActive": True, "createdAt": datetime.utcnow()},
            {"title": "Digital Apps", "subtitle": "Aplikasi Tes Online", "imageUrl": "https://images.unsplash.com/photo-1551650975-87deedd944c3?w=400&q=80", "link": "/user-test", "badge": "Digital", "order": 5, "isActive": True, "createdAt": datetime.utcnow()}
        ]
        await db.website_products.insert_many(default_products)
        
        # Default testimonials
        default_testimonials = [
            {"name": "Siti Rahma", "organization": "Yayasan Al Karim", "role": "Kepala Sekolah", "imageUrl": "https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=200&q=80", "text": "Program event KELAS GALI BAKAT yang telah terealisir di sekolah kami, NYATA telah memberi ANTUSIAS yang tinggi dari murid-murid kami.", "rating": 5, "order": 0, "isActive": True, "createdAt": datetime.utcnow()},
            {"name": "Asmi Kamal", "organization": "Peserta Program", "role": "Mahasiswa", "imageUrl": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=200&q=80", "text": "Setelah diobservasi oleh NEWMECLASS, semakin mengerti tentang 'siapa diri ini', memastikan langkah apa yang bisa saya pilih dalam pengembangan.", "rating": 5, "order": 1, "isActive": True, "createdAt": datetime.utcnow()},
            {"name": "Dr. Ahmad Fauzi", "organization": "Universitas Negeri Medan", "role": "Dosen Psikologi", "imageUrl": "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=200&q=80", "text": "Metode 5 Element yang digunakan NEWMECLASS sangat komprehensif dan berbasis riset. Saya merekomendasikan program ini.", "rating": 5, "order": 2, "isActive": True, "createdAt": datetime.utcnow()},
            {"name": "Rina Susanti", "organization": "PT. Global Mandiri", "role": "HR Manager", "imageUrl": "https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=200&q=80", "text": "Kami telah bermitra dengan NEWMECLASS untuk program pengembangan karyawan. Hasilnya sangat positif.", "rating": 5, "order": 3, "isActive": True, "createdAt": datetime.utcnow()}
        ]
        await db.website_testimonials.insert_many(default_testimonials)
        
        # Default activities
        default_activities = [
            {"title": "Outbound Training", "imageUrl": "https://images.unsplash.com/photo-1529156069898-49953e39b3ac?w=400&q=80", "link": "/services/class", "order": 0, "isActive": True, "createdAt": datetime.utcnow()},
            {"title": "Coaching / Upscale Talent", "imageUrl": "https://images.unsplash.com/photo-1552664730-d307ca884978?w=400&q=80", "link": "/services/clinic", "order": 1, "isActive": True, "createdAt": datetime.utcnow()},
            {"title": "Edukasi Bisnis", "imageUrl": "https://images.unsplash.com/photo-1542744173-8e7e53415bb0?w=400&q=80", "link": "/kelas-gali-bakat", "order": 2, "isActive": True, "createdAt": datetime.utcnow()},
            {"title": "Kontes Brand Ambassador", "imageUrl": "https://images.unsplash.com/photo-1475721027785-f74eccf877e2?w=400&q=80", "link": "/shop", "order": 3, "isActive": True, "createdAt": datetime.utcnow()}
        ]
        await db.website_activities.insert_many(default_activities)
        
        # Default section images
        default_section_images = [
            {"sectionName": "about-main", "imageUrl": "https://images.unsplash.com/photo-1552664730-d307ca884978?w=600&q=80", "altText": "Team Working", "createdAt": datetime.utcnow()},
            {"sectionName": "services-corporate", "imageUrl": "https://images.unsplash.com/photo-1524178232363-1fb2b075b655?w=600&q=80", "altText": "Corporate Training", "createdAt": datetime.utcnow()},
            {"sectionName": "services-individual", "imageUrl": "https://images.unsplash.com/photo-1573497620053-ea5300f94f21?w=600&q=80", "altText": "Individual Counseling", "createdAt": datetime.utcnow()},
            {"sectionName": "promo-main", "imageUrl": "https://images.unsplash.com/photo-1598162942982-5cb74331817c?w=600&q=80", "altText": "Growth Mindset", "createdAt": datetime.utcnow()}
        ]
        await db.section_images.insert_many(default_section_images)
        
        return {"message": "Default content seeded successfully", "seeded": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
