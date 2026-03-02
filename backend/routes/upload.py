from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from typing import List, Optional
from database import get_db
from datetime import datetime
from bson import ObjectId
import uuid
from pathlib import Path

router = APIRouter(prefix="/api/upload", tags=["upload"])
db = get_db()

# Base upload directory
BASE_UPLOAD_DIR = Path("/app/frontend/public/uploads")

# Allowed file types
ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp', 'gif'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

def get_upload_dir(category: str) -> Path:
    """Get or create upload directory for category"""
    upload_dir = BASE_UPLOAD_DIR / category
    upload_dir.mkdir(parents=True, exist_ok=True)
    return upload_dir

def validate_file(file: UploadFile, max_size: int = MAX_FILE_SIZE) -> str:
    """Validate file type and return extension"""
    if not file.filename:
        raise HTTPException(status_code=400, detail="Nama file tidak boleh kosong")
    
    file_extension = file.filename.rsplit('.', 1)[-1].lower() if '.' in file.filename else ''
    
    if file_extension not in ALLOWED_IMAGE_EXTENSIONS:
        raise HTTPException(
            status_code=400, 
            detail=f"Tipe file tidak diizinkan. Format yang diterima: {', '.join(ALLOWED_IMAGE_EXTENSIONS)}"
        )
    
    return file_extension

@router.post("/single", response_model=dict)
async def upload_single_file(
    file: UploadFile = File(...),
    category: str = Form("general")
):
    """
    Upload single file
    Categories: general, banners, articles, payments, certificates, profiles
    """
    try:
        file_extension = validate_file(file)
        
        upload_dir = get_upload_dir(category)
        unique_filename = f"{uuid.uuid4()}.{file_extension}"
        file_path = upload_dir / unique_filename
        
        contents = await file.read()
        
        # Check file size
        if len(contents) > MAX_FILE_SIZE:
            raise HTTPException(status_code=400, detail="Ukuran file maksimal 10MB")
        
        with open(file_path, 'wb') as f:
            f.write(contents)
        
        file_url = f"/uploads/{category}/{unique_filename}"
        
        # Log upload to database
        await db.uploads.insert_one({
            "filename": unique_filename,
            "originalName": file.filename,
            "url": file_url,
            "category": category,
            "size": len(contents),
            "mimeType": file.content_type,
            "uploadedAt": datetime.utcnow()
        })
        
        return {
            "success": True,
            "url": file_url,
            "filename": unique_filename,
            "message": "File berhasil diupload"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@router.post("/image", response_model=dict)
async def upload_image(file: UploadFile = File(...)):
    """
    Simple image upload endpoint - returns URL directly
    """
    try:
        file_extension = validate_file(file)
        
        upload_dir = get_upload_dir("images")
        unique_filename = f"{uuid.uuid4()}.{file_extension}"
        file_path = upload_dir / unique_filename
        
        contents = await file.read()
        
        # Check file size
        if len(contents) > MAX_FILE_SIZE:
            raise HTTPException(status_code=400, detail="Ukuran file maksimal 10MB")
        
        with open(file_path, 'wb') as f:
            f.write(contents)
        
        file_url = f"/uploads/images/{unique_filename}"
        
        # Log upload to database
        await db.uploads.insert_one({
            "filename": unique_filename,
            "originalName": file.filename,
            "url": file_url,
            "category": "images",
            "size": len(contents),
            "mimeType": file.content_type,
            "uploadedAt": datetime.utcnow()
        })
        
        return {
            "success": True,
            "url": file_url,
            "filename": unique_filename
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@router.post("/multiple", response_model=dict)
async def upload_multiple_files(
    files: List[UploadFile] = File(...),
    category: str = Form("general")
):
    """
    Upload multiple files at once (max 10 files)
    Categories: general, banners, articles, payments, certificates, profiles
    """
    try:
        if len(files) > 10:
            raise HTTPException(status_code=400, detail="Maksimal 10 file dalam satu upload")
        
        upload_dir = get_upload_dir(category)
        uploaded_files = []
        failed_files = []
        
        for file in files:
            try:
                file_extension = validate_file(file)
                unique_filename = f"{uuid.uuid4()}.{file_extension}"
                file_path = upload_dir / unique_filename
                
                contents = await file.read()
                
                if len(contents) > MAX_FILE_SIZE:
                    failed_files.append({
                        "filename": file.filename,
                        "error": "Ukuran file melebihi 10MB"
                    })
                    continue
                
                with open(file_path, 'wb') as f:
                    f.write(contents)
                
                file_url = f"/uploads/{category}/{unique_filename}"
                
                # Log to database
                await db.uploads.insert_one({
                    "filename": unique_filename,
                    "originalName": file.filename,
                    "url": file_url,
                    "category": category,
                    "size": len(contents),
                    "mimeType": file.content_type,
                    "uploadedAt": datetime.utcnow()
                })
                
                uploaded_files.append({
                    "originalName": file.filename,
                    "url": file_url,
                    "filename": unique_filename
                })
                
            except HTTPException as he:
                failed_files.append({
                    "filename": file.filename,
                    "error": he.detail
                })
            except Exception as e:
                failed_files.append({
                    "filename": file.filename,
                    "error": str(e)
                })
        
        return {
            "success": True,
            "uploaded": uploaded_files,
            "failed": failed_files,
            "message": f"{len(uploaded_files)} file berhasil diupload, {len(failed_files)} gagal"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@router.delete("/{category}/{filename}", response_model=dict)
async def delete_uploaded_file(category: str, filename: str):
    """Delete uploaded file"""
    try:
        upload_dir = get_upload_dir(category)
        file_path = upload_dir / filename
        
        if file_path.exists():
            file_path.unlink()
            
            # Remove from database
            await db.uploads.delete_one({
                "filename": filename,
                "category": category
            })
            
            return {"success": True, "message": "File berhasil dihapus"}
        else:
            raise HTTPException(status_code=404, detail="File tidak ditemukan")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@router.get("/list", response_model=dict)
async def list_uploads(
    category: Optional[str] = None,
    skip: int = 0,
    limit: int = 50
):
    """List uploaded files"""
    try:
        query = {}
        if category:
            query["category"] = category
        
        cursor = db.uploads.find(query).skip(skip).limit(limit).sort("uploadedAt", -1)
        uploads = await cursor.to_list(length=limit)
        
        for upload in uploads:
            upload["_id"] = str(upload["_id"])
        
        total = await db.uploads.count_documents(query)
        
        return {
            "uploads": uploads,
            "total": total,
            "skip": skip,
            "limit": limit
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
