from fastapi import FastAPI, File, UploadFile, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import os
import cv2
import numpy as np
from PIL import Image
import io
import pandas as pd
import pickle
from typing import List, Dict, Any
import logging
from sqlalchemy.orm import Session

from furniture_detection import FurnitureDetector
from furniture_similarity import FurnitureSimilarity
from models import DetectionResponse, SimilarityResponse, FurnitureItem
from config import *
from database import get_db

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title=API_TITLE,
    description=API_DESCRIPTION,
    version=API_VERSION
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=CORS_METHODS,
    allow_headers=CORS_HEADERS,
)

# 전역 변수로 모델 인스턴스 저장
detector = None
similarity_model = None

@app.on_event("startup")
async def startup_event():
    """애플리케이션 시작 시 모델 로드"""
    global detector, similarity_model
    
    try:
        logger.info("Loading furniture detection model...")
        detector = FurnitureDetector()
        
        logger.info("Loading furniture similarity model...")
        similarity_model = FurnitureSimilarity()
        
        logger.info("All models loaded successfully!")
        
    except Exception as e:
        logger.error(f"Error loading models: {str(e)}")
        raise e

@app.get("/")
async def root():
    """API 상태 확인"""
    return {"message": "Furniture Recommendation API is running!", "status": "healthy"}

@app.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """헬스 체크 엔드포인트"""
    try:
        # 데이터베이스 연결 테스트
        from sqlalchemy import text
        db.execute(text("SELECT 1"))
        db_connected = True
    except Exception as e:
        logger.error(f"Database connection failed: {str(e)}")
        db_connected = False
    
    return {
        "status": "healthy",
        "detector_loaded": detector is not None,
        "similarity_model_loaded": similarity_model is not None,
        "database_connected": db_connected
    }

@app.post("/detect", response_model=DetectionResponse)
async def detect_furniture(file: UploadFile = File(...)):
    """
    이미지에서 가구 객체를 탐지하고 카테고리를 분류합니다.
    
    Args:
        file: 업로드된 이미지 파일
        
    Returns:
        DetectionResponse: 탐지된 가구 객체들의 정보
    """
    try:
        # 이미지 파일 검증
        if not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # 이미지 읽기
        contents = await file.read()
        image = Image.open(io.BytesIO(contents))
        image_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        
        # 가구 탐지 수행
        detections = detector.detect_furniture(image_cv)
        
        # 응답 생성
        response = DetectionResponse(
            success=True,
            message=f"Detected {len(detections)} furniture items",
            detections=detections,
            total_count=len(detections)
        )
        
        logger.info(f"Detection completed: {len(detections)} items found")
        return response
        
    except Exception as e:
        logger.error(f"Detection error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Detection failed: {str(e)}")

@app.post("/recommend", response_model=SimilarityResponse)
async def recommend_similar_furniture(
    file: UploadFile = File(...),
    category: str = None,
    top_k: int = 5,
    db: Session = Depends(get_db)
):
    """
    업로드된 가구 이미지와 유사한 스타일의 가구를 추천합니다.
    
    Args:
        file: 가구 이미지 파일
        category: 특정 카테고리로 제한 (선택사항)
        top_k: 추천할 상위 개수 (기본값: 5)
        
    Returns:
        SimilarityResponse: 추천된 가구 목록
    """
    try:
        # 이미지 파일 검증
        if not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # 이미지 읽기
        contents = await file.read()
        image = Image.open(io.BytesIO(contents))
        image_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        
        # 유사도 기반 추천 수행
        recommendations = similarity_model.find_similar_furniture(
            image_cv, 
            db, 
            category=category, 
            top_k=top_k
        )
        
        # 응답 생성
        response = SimilarityResponse(
            success=True,
            message=f"Found {len(recommendations)} similar furniture items",
            recommendations=recommendations,
            total_count=len(recommendations)
        )
        
        logger.info(f"Recommendation completed: {len(recommendations)} items found")
        return response
        
    except Exception as e:
        logger.error(f"Recommendation error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Recommendation failed: {str(e)}")

@app.get("/categories")
async def get_categories():
    """사용 가능한 가구 카테고리 목록을 반환합니다."""
    categories = ["bed", "chair", "dresser", "lamp", "sofa", "table"]
    return {"categories": categories}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
