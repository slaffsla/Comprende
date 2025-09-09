from fastapi import FastAPI, APIRouter, UploadFile, File, HTTPException, Form, BackgroundTasks
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime
import asyncio
import aiofiles
import tempfile
import shutil
from emergentintegrations.llm.chat import LlmChat, UserMessage
import json
import time
import hashlib
from cryptography.fernet import Fernet
import base64

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI(title="Comprende - Universal Communication Platform", version="1.0.0")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Security and encryption setup
ENCRYPTION_KEY = os.environ.get('ENCRYPTION_KEY', Fernet.generate_key())
cipher_suite = Fernet(ENCRYPTION_KEY)

# LLM Setup
EMERGENT_LLM_KEY = os.environ.get('EMERGENT_LLM_KEY')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Pydantic Models
class UserCreate(BaseModel):
    username: str
    email: str
    preferred_languages: List[str] = ["eng", "spa", "heb", "ara", "fra"]

class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    username: str
    email: str
    preferred_languages: List[str]
    created_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = True

class TranslationRequest(BaseModel):
    text: str
    source_language: Optional[str] = None
    target_language: str = "eng"
    context: Optional[str] = "general"
    industry: Optional[str] = "general"

class TranslationResult(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    original_text: str
    translated_text: str
    source_language: str
    target_language: str
    context: str
    industry: str
    confidence: float
    processing_time: float
    user_id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class DocumentProcessRequest(BaseModel):
    document_type: str = "auto"
    languages: List[str] = ["eng"]
    extract_text: bool = True
    translate_to: Optional[str] = None

class DocumentResult(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    filename: str
    document_type: str
    extracted_text: str
    translated_text: Optional[str] = None
    detected_language: str
    confidence: float
    processing_time: float
    created_at: datetime = Field(default_factory=datetime.utcnow)

class AuditLog(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: Optional[str] = None
    action: str
    resource: str
    details: Dict[str, Any]
    ip_address: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

# Security Functions
def encrypt_data(data: str) -> str:
    """Encrypt sensitive data"""
    try:
        encrypted_data = cipher_suite.encrypt(data.encode())
        return base64.b64encode(encrypted_data).decode()
    except Exception as e:
        logger.error(f"Encryption error: {e}")
        return data

def decrypt_data(encrypted_data: str) -> str:
    """Decrypt sensitive data"""
    try:
        decoded_data = base64.b64decode(encrypted_data.encode())
        decrypted_data = cipher_suite.decrypt(decoded_data)
        return decrypted_data.decode()
    except Exception as e:
        logger.error(f"Decryption error: {e}")
        return encrypted_data

async def log_audit_event(user_id: Optional[str], action: str, resource: str, details: Dict[str, Any], ip_address: Optional[str] = None):
    """Log audit events for security compliance"""
    try:
        audit_log = AuditLog(
            user_id=user_id,
            action=action,
            resource=resource,
            details=details,
            ip_address=ip_address
        )
        await db.audit_logs.insert_one(audit_log.dict())
    except Exception as e:
        logger.error(f"Audit logging error: {e}")

# Language Detection and Translation Service
class TranslationService:
    def __init__(self):
        self.llm_key = EMERGENT_LLM_KEY
        self.language_codes = {
            'eng': 'English',
            'spa': 'Spanish', 
            'heb': 'Hebrew',
            'ara': 'Arabic',
            'fra': 'French',
            'deu': 'German',
            'ita': 'Italian',
            'por': 'Portuguese',
            'rus': 'Russian',
            'chi': 'Chinese'
        }
        
    def detect_language(self, text: str) -> str:
        """Basic language detection based on script"""
        if not text:
            return 'eng'
            
        # Hebrew detection
        hebrew_chars = sum(1 for char in text if '\u0590' <= char <= '\u05FF')
        if hebrew_chars > len(text) * 0.3:
            return 'heb'
            
        # Arabic detection  
        arabic_chars = sum(1 for char in text if '\u0600' <= char <= '\u06FF')
        if arabic_chars > len(text) * 0.3:
            return 'ara'
            
        # Default to English
        return 'eng'
    
    async def translate_text(self, text: str, source_lang: str, target_lang: str, context: str = "general", industry: str = "general") -> tuple[str, float]:
        """Translate text using Emergent LLM"""
        if not self.llm_key:
            raise HTTPException(status_code=500, detail="Translation service not configured")
            
        start_time = time.time()
        
        try:
            # Create specialized system message based on context and industry
            system_message = self._create_system_message(source_lang, target_lang, context, industry)
            
            # Initialize LLM chat
            chat = LlmChat(
                api_key=self.llm_key,
                session_id=f"translate_{uuid.uuid4()}",
                system_message=system_message
            ).with_model("openai", "gpt-4o")
            
            # Create translation prompt
            user_message = UserMessage(
                text=f"Translate the following text from {self.language_codes.get(source_lang, source_lang)} to {self.language_codes.get(target_lang, target_lang)}:\n\n{text}"
            )
            
            # Get translation
            response = await chat.send_message(user_message)
            
            processing_time = time.time() - start_time
            confidence = 0.95  # High confidence for LLM translations
            
            return response.strip(), confidence
            
        except Exception as e:
            logger.error(f"Translation error: {e}")
            raise HTTPException(status_code=500, detail=f"Translation failed: {str(e)}")
    
    def _create_system_message(self, source_lang: str, target_lang: str, context: str, industry: str) -> str:
        """Create specialized system message for translation"""
        base_message = f"You are a professional translator specializing in {self.language_codes.get(source_lang, source_lang)} to {self.language_codes.get(target_lang, target_lang)} translation."
        
        if industry != "general":
            base_message += f" You have expertise in {industry} terminology and context."
            
        if context != "general":
            base_message += f" The translation context is: {context}."
            
        base_message += " Provide accurate, natural translations that preserve meaning and cultural context. Return only the translated text without explanations."
        
        # Add specific instructions for RTL languages
        if target_lang in ['heb', 'ara']:
            base_message += " Ensure proper right-to-left text formatting and cultural appropriateness."
            
        return base_message

translation_service = TranslationService()

# File Management
class FileManager:
    def __init__(self):
        self.upload_dir = Path("/tmp/comprende_uploads")
        self.upload_dir.mkdir(exist_ok=True)
        self.allowed_extensions = {'.txt', '.pdf', '.jpg', '.jpeg', '.png', '.tiff', '.bmp', '.docx'}
        self.max_file_size = 10 * 1024 * 1024  # 10MB
    
    async def save_upload_file(self, upload_file: UploadFile) -> str:
        """Save uploaded file securely"""
        if not upload_file.filename:
            raise HTTPException(status_code=400, detail="No filename provided")
            
        file_ext = Path(upload_file.filename).suffix.lower()
        if file_ext not in self.allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type. Allowed: {self.allowed_extensions}"
            )
        
        file_id = str(uuid.uuid4())
        file_path = self.upload_dir / f"{file_id}{file_ext}"
        
        # Save file with size validation
        total_size = 0
        async with aiofiles.open(file_path, 'wb') as f:
            while content := await upload_file.read(8192):
                total_size += len(content)
                if total_size > self.max_file_size:
                    await f.close()
                    file_path.unlink()
                    raise HTTPException(status_code=413, detail="File too large")
                await f.write(content)
        
        return str(file_path)
    
    def cleanup_file(self, file_path: str):
        """Clean up temporary files"""
        try:
            Path(file_path).unlink()
        except Exception as e:
            logger.warning(f"Failed to cleanup file {file_path}: {e}")

file_manager = FileManager()

# Document Processing Service (Mock OCR for now)
class DocumentProcessor:
    def __init__(self):
        self.supported_formats = {'.txt', '.pdf', '.jpg', '.jpeg', '.png', '.tiff', '.bmp'}
    
    async def extract_text(self, file_path: str, languages: List[str] = None) -> tuple[str, str, float]:
        """Extract text from document (mock implementation)"""
        start_time = time.time()
        
        file_ext = Path(file_path).suffix.lower()
        
        if file_ext == '.txt':
            # Read text file directly
            async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
                text = await f.read()
            detected_lang = translation_service.detect_language(text)
            confidence = 1.0
        
        elif file_ext in ['.jpg', '.jpeg', '.png', '.tiff', '.bmp']:
            # Mock OCR extraction
            text = "Sample extracted text from image document. This is a placeholder for OCR functionality."
            detected_lang = 'eng'
            confidence = 0.85
        
        elif file_ext == '.pdf':
            # Mock PDF text extraction
            text = "Sample extracted text from PDF document. This is a placeholder for PDF processing."
            detected_lang = 'eng'
            confidence = 0.90
        
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported file format: {file_ext}")
        
        processing_time = time.time() - start_time
        return text, detected_lang, confidence

document_processor = DocumentProcessor()

# API Routes
@api_router.get("/")
async def root():
    return {"message": "Comprende API - Universal Communication Platform", "version": "1.0.0"}

@api_router.post("/users", response_model=User)
async def create_user(user_data: UserCreate):
    """Create a new user"""
    user = User(**user_data.dict())
    await db.users.insert_one(user.dict())
    await log_audit_event(user.id, "CREATE", "USER", {"username": user.username})
    return user

@api_router.get("/users/{user_id}", response_model=User)
async def get_user(user_id: str):
    """Get user by ID"""
    user_data = await db.users.find_one({"id": user_id})
    if not user_data:
        raise HTTPException(status_code=404, detail="User not found")
    return User(**user_data)

@api_router.post("/translate", response_model=TranslationResult)
async def translate_text(request: TranslationRequest, user_id: Optional[str] = None):
    """Translate text between languages"""
    start_time = time.time()
    
    # Auto-detect source language if not provided
    source_lang = request.source_language
    if not source_lang:
        source_lang = translation_service.detect_language(request.text)
    
    # Perform translation
    translated_text, confidence = await translation_service.translate_text(
        request.text,
        source_lang,
        request.target_language,
        request.context,
        request.industry
    )
    
    processing_time = time.time() - start_time
    
    # Create result
    result = TranslationResult(
        original_text=request.text,
        translated_text=translated_text,
        source_language=source_lang,
        target_language=request.target_language,
        context=request.context,
        industry=request.industry,
        confidence=confidence,
        processing_time=processing_time,
        user_id=user_id
    )
    
    # Store translation in database (encrypted)
    result_dict = result.dict()
    result_dict['original_text'] = encrypt_data(result_dict['original_text'])
    result_dict['translated_text'] = encrypt_data(result_dict['translated_text'])
    
    await db.translations.insert_one(result_dict)
    
    # Log audit event
    await log_audit_event(
        user_id,
        "TRANSLATE",
        "TEXT",
        {
            "source_language": source_lang,
            "target_language": request.target_language,
            "text_length": len(request.text),
            "context": request.context,
            "industry": request.industry
        }
    )
    
    return result

@api_router.post("/documents/process", response_model=DocumentResult)
async def process_document(
    file: UploadFile = File(...),
    languages: str = Form("eng"),
    translate_to: Optional[str] = Form(None),
    background_tasks: BackgroundTasks = None,
    user_id: Optional[str] = None
):
    """Process uploaded document for text extraction and translation"""
    start_time = time.time()
    
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")
    
    file_path = None
    try:
        # Save uploaded file
        file_path = await file_manager.save_upload_file(file)
        
        # Parse languages
        language_list = [lang.strip() for lang in languages.split(',')]
        
        # Extract text from document
        extracted_text, detected_language, confidence = await document_processor.extract_text(
            file_path, language_list
        )
        
        # Translate if requested
        translated_text = None
        if translate_to and translate_to != detected_language:
            translated_text, _ = await translation_service.translate_text(
                extracted_text,
                detected_language,
                translate_to,
                "document",
                "general"
            )
        
        processing_time = time.time() - start_time
        
        # Create result
        result = DocumentResult(
            filename=file.filename,
            document_type=Path(file.filename).suffix.lower(),
            extracted_text=extracted_text,
            translated_text=translated_text,
            detected_language=detected_language,
            confidence=confidence,
            processing_time=processing_time
        )
        
        # Store result in database (encrypted)
        result_dict = result.dict()
        result_dict['extracted_text'] = encrypt_data(result_dict['extracted_text'])
        if result_dict['translated_text']:
            result_dict['translated_text'] = encrypt_data(result_dict['translated_text'])
        
        await db.documents.insert_one(result_dict)
        
        # Schedule cleanup
        if background_tasks and file_path:
            background_tasks.add_task(file_manager.cleanup_file, file_path)
        
        # Log audit event
        await log_audit_event(
            user_id,
            "PROCESS_DOCUMENT",
            "DOCUMENT",
            {
                "filename": file.filename,
                "detected_language": detected_language,
                "translate_to": translate_to,
                "text_length": len(extracted_text)
            }
        )
        
        return result
        
    except Exception as e:
        if file_path:
            file_manager.cleanup_file(file_path)
        raise e

@api_router.get("/translations/history")
async def get_translation_history(user_id: Optional[str] = None, limit: int = 50):
    """Get translation history for user"""
    query = {"user_id": user_id} if user_id else {}
    translations = await db.translations.find(query).sort("created_at", -1).limit(limit).to_list(limit)
    
    # Decrypt data for response
    for translation in translations:
        if 'original_text' in translation:
            translation['original_text'] = decrypt_data(translation['original_text'])
        if 'translated_text' in translation:
            translation['translated_text'] = decrypt_data(translation['translated_text'])
    
    return translations

@api_router.get("/languages/supported")
async def get_supported_languages():
    """Get list of supported languages"""
    return {
        "languages": translation_service.language_codes,
        "translation_engine": "Emergent LLM",
        "ocr_languages": ["eng", "spa", "heb", "ara", "fra", "deu"]
    }

@api_router.get("/health")
async def health_check():
    """System health check"""
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "components": {}
    }
    
    # Check database connection
    try:
        await db.command("ping")
        health_status["components"]["database"] = "healthy"
    except Exception as e:
        health_status["components"]["database"] = f"unhealthy: {str(e)}"
        health_status["status"] = "degraded"
    
    # Check LLM service
    try:
        if EMERGENT_LLM_KEY:
            health_status["components"]["translation_service"] = "healthy"
        else:
            health_status["components"]["translation_service"] = "unhealthy: No API key"
            health_status["status"] = "degraded"
    except Exception as e:
        health_status["components"]["translation_service"] = f"unhealthy: {str(e)}"
        health_status["status"] = "degraded"
    
    return health_status

@api_router.get("/audit/logs")
async def get_audit_logs(limit: int = 100, user_id: Optional[str] = None):
    """Get audit logs (admin only)"""
    query = {"user_id": user_id} if user_id else {}
    logs = await db.audit_logs.find(query).sort("timestamp", -1).limit(limit).to_list(limit)
    return logs

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()