import cv2
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Model
from tensorflow.keras.applications import VGG16
import pandas as pd
import logging
from typing import List, Dict, Any, Optional
import os
import pickle
from scipy.spatial.distance import cosine
from sqlalchemy.orm import Session

from models import FurnitureItem

logger = logging.getLogger(__name__)

class FurnitureSimilarity:
    """가구 유사도 검색을 위한 VGG16 기반 클래스"""
    
    def __init__(self, model_path: str = None, input_size: tuple = (224, 224)):
        """
        FurnitureSimilarity 초기화
        
        Args:
            model_path: 사전 학습된 모델 경로
            input_size: 입력 이미지 크기
        """
        self.input_size = input_size
        self.feature_extractor = None
        
        # 모델 로드
        self._load_model(model_path)
        
        logger.info("FurnitureSimilarity initialized successfully")
    
    def _load_model(self, model_path: str = None):
        """
        유사도 검색 모델을 로드합니다.
        
        Args:
            model_path: 모델 파일 경로
        """
        try:
            if model_path and os.path.exists(model_path):
                # 사전 학습된 모델 로드
                model = tf.keras.models.load_model(model_path)
                # 특성 추출 레이어 선택 (예: dense_4)
                self.feature_extractor = Model(
                    model.input, 
                    model.get_layer('dense_4').output
                )
                logger.info(f"Loaded custom model from {model_path}")
            else:
                # VGG16 기반 모델 생성 (fallback)
                self._create_vgg16_model()
                logger.warning("Custom model not found, using VGG16 pre-trained model")
                
        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")
            # VGG16 기반 모델 생성 (fallback)
            self._create_vgg16_model()
    
    def _create_vgg16_model(self):
        """VGG16 기반 특성 추출 모델을 생성합니다."""
        try:
            # VGG16 모델 로드 (사전 학습된 가중치 사용)
            base_model = VGG16(
                weights='imagenet',
                include_top=False,
                input_shape=(*self.input_size, 3)
            )
            
            # 특성 추출을 위한 모델 구성
            x = base_model.output
            x = tf.keras.layers.GlobalAveragePooling2D()(x)
            x = tf.keras.layers.Dense(512, activation='relu')(x)
            x = tf.keras.layers.Dropout(0.5)(x)
            features = tf.keras.layers.Dense(256, activation='relu')(x)
            
            self.feature_extractor = Model(inputs=base_model.input, outputs=features)
            
            logger.info("Created VGG16-based feature extractor")
            
        except Exception as e:
            logger.error(f"Error creating VGG16 model: {str(e)}")
            raise e
    
    def extract_features(self, image: np.ndarray) -> np.ndarray:
        """
        이미지에서 특성 벡터를 추출합니다.
        
        Args:
            image: 입력 이미지 (BGR 형식)
            
        Returns:
            np.ndarray: 추출된 특성 벡터
        """
        try:
            # 이미지 전처리
            processed_image = self._preprocess_image(image)
            
            # 특성 추출
            features = self.feature_extractor.predict(processed_image, verbose=0)
            
            # 정규화
            features = features / np.linalg.norm(features)
            
            return features.flatten()
            
        except Exception as e:
            logger.error(f"Feature extraction failed: {str(e)}")
            raise e
    
    def _preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """
        이미지를 모델 입력 형식으로 전처리합니다.
        
        Args:
            image: 입력 이미지 (BGR 형식)
            
        Returns:
            np.ndarray: 전처리된 이미지
        """
        # BGR을 RGB로 변환
        if len(image.shape) == 3 and image.shape[2] == 3:
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # 이미지 크기 조정
        image = cv2.resize(image, self.input_size)
        
        # 정규화 (0-1 범위)
        image = image.astype(np.float32) / 255.0
        
        # 배치 차원 추가
        image = np.expand_dims(image, axis=0)
        
        return image
    
    def find_similar_furniture(
        self, 
        query_image: np.ndarray, 
        db: Session,
        category: str = None,
        top_k: int = 5
    ) -> List[FurnitureItem]:
        """
        쿼리 이미지와 유사한 가구를 찾습니다.
        
        Args:
            query_image: 쿼리 이미지
            db: SQLAlchemy 데이터베이스 세션
            category: 특정 카테고리로 제한 (선택사항)
            top_k: 반환할 상위 개수
            
        Returns:
            List[FurnitureItem]: 유사한 가구 목록
        """
        try:
            # 쿼리 이미지에서 특성 추출
            query_features = self.extract_features(query_image)
            
            # PostgreSQL에서 제품 데이터 가져오기
            from sqlalchemy import text
            
            # 기본 쿼리
            query = """
                SELECT p.id, p.title, p.price_amount, p.images, c.name as category_name
                FROM products p
                LEFT JOIN categories c ON p.category_id = c.id
                WHERE p.stock > 0
            """
            
            # 카테고리 필터링
            if category:
                query += " AND LOWER(c.name) = LOWER(:category)"
            
            query += " LIMIT 1000"  # 성능을 위해 제한
            
            # 쿼리 실행
            if category:
                result = db.execute(text(query), {"category": category})
            else:
                result = db.execute(text(query))
            
            products = result.fetchall()
            
            if len(products) == 0:
                logger.warning(f"No products found for category: {category}")
                return []
            
            # 유사도 계산 (현재는 더미 구현 - 실제로는 이미지 특성 벡터 비교 필요)
            similarities = []
            for product in products:
                try:
                    # 실제 구현에서는 제품 이미지에서 특성 벡터를 추출하고 비교해야 함
                    # 현재는 더미 유사도 점수 사용
                    similarity = np.random.random()  # 더미 점수
                    
                    similarities.append({
                        'product': product,
                        'similarity': similarity
                    })
                except Exception as e:
                    logger.warning(f"Error calculating similarity for product {product.id}: {str(e)}")
                    continue
            
            # 유사도 순으로 정렬
            similarities.sort(key=lambda x: x['similarity'], reverse=True)
            
            # 상위 k개 선택
            top_similarities = similarities[:top_k]
            
            # FurnitureItem 객체로 변환
            recommendations = []
            for item in top_similarities:
                product = item['product']
                
                # 이미지 URL 추출 (JSON 배열에서 첫 번째 이미지)
                image_url = ""
                if product.images and len(product.images) > 0:
                    image_url = product.images[0] if isinstance(product.images, list) else str(product.images)
                
                furniture_item = FurnitureItem(
                    id=str(product.id),
                    name=str(product.title),
                    category=str(product.category_name or 'unknown'),
                    price=float(product.price_amount or 0.0),
                    image_url=image_url,
                    product_url=f"/products/{product.id}",  # API 엔드포인트
                    similarity_score=float(item['similarity']),
                    style_features=query_features.tolist()
                )
                recommendations.append(furniture_item)
            
            logger.info(f"Found {len(recommendations)} similar furniture items")
            return recommendations
            
        except Exception as e:
            logger.error(f"Similarity search failed: {str(e)}")
            raise e
    
    def calculate_similarity_matrix(self, images: List[np.ndarray]) -> np.ndarray:
        """
        여러 이미지 간의 유사도 행렬을 계산합니다.
        
        Args:
            images: 이미지 리스트
            
        Returns:
            np.ndarray: 유사도 행렬
        """
        try:
            n_images = len(images)
            similarity_matrix = np.zeros((n_images, n_images))
            
            # 각 이미지의 특성 추출
            features = []
            for image in images:
                feature = self.extract_features(image)
                features.append(feature)
            
            # 유사도 행렬 계산
            for i in range(n_images):
                for j in range(n_images):
                    if i == j:
                        similarity_matrix[i][j] = 1.0
                    else:
                        similarity = 1 - cosine(features[i], features[j])
                        similarity_matrix[i][j] = similarity
            
            return similarity_matrix
            
        except Exception as e:
            logger.error(f"Similarity matrix calculation failed: {str(e)}")
            raise e
