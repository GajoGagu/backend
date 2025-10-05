"""
가구 데이터베이스 생성 스크립트
기존 IKEA 데이터를 furniture 데이터베이스로 변환합니다.
"""

import pandas as pd
import numpy as np
import os
import sys
import pickle
from pathlib import Path
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_furniture_database():
    """기존 IKEA 데이터를 furniture 데이터베이스로 변환합니다."""
    
    # 기존 IKEA 데이터 경로
    ikea_data_path = "example/ObjectDetectionProject-IKEAFurnituresRecommender/ikea/ikea-data"
    ikea_csv_path = os.path.join(ikea_data_path, "ikea_final_model0.csv")
    
    try:
        # IKEA 데이터 로드
        logger.info("Loading IKEA data...")
        ikea_df = pd.read_pickle(ikea_csv_path)
        
        logger.info(f"Loaded {len(ikea_df)} furniture items")
        logger.info(f"Columns: {ikea_df.columns.tolist()}")
        
        # 데이터 정리 및 변환
        furniture_df = ikea_df.copy()
        
        # 컬럼명 정리
        if 'Unnamed: 0' in furniture_df.columns:
            furniture_df = furniture_df.drop('Unnamed: 0', axis=1)
        
        # 카테고리명 정리 (소문자로 변환)
        if 'item_cat' in furniture_df.columns:
            furniture_df['item_cat'] = furniture_df['item_cat'].str.lower()
        
        # 가격 데이터 정리
        if 'item_price' in furniture_df.columns:
            # 가격을 숫자로 변환 (문자열에서 숫자만 추출)
            furniture_df['item_price'] = pd.to_numeric(
                furniture_df['item_price'].astype(str).str.extract(r'(\d+\.?\d*)')[0], 
                errors='coerce'
            )
            furniture_df['item_price'] = furniture_df['item_price'].fillna(0.0)
        
        # URL 정리
        if 'item_url' in furniture_df.columns:
            furniture_df['item_url'] = furniture_df['item_url'].fillna('')
        if 'prod_url' in furniture_df.columns:
            furniture_df['prod_url'] = furniture_df['prod_url'].fillna('')
        
        # 제품명 정리
        if 'item_name' in furniture_df.columns:
            furniture_df['item_name'] = furniture_df['item_name'].fillna('Unknown Product')
        
        # 벡터 데이터 확인
        if 'vector' in furniture_df.columns:
            # 벡터가 None인 행 제거
            furniture_df = furniture_df.dropna(subset=['vector'])
            logger.info(f"After removing rows without vectors: {len(furniture_df)} items")
        else:
            logger.warning("No vector column found in the data")
            # 더미 벡터 생성 (실제 사용 시에는 실제 특성 벡터로 교체 필요)
            furniture_df['vector'] = [np.random.rand(256) for _ in range(len(furniture_df))]
        
        # 데이터 저장
        output_path = "furniture_data/furniture_database.pkl"
        furniture_df.to_pickle(output_path)
        
        logger.info(f"Furniture database saved to {output_path}")
        logger.info(f"Final database contains {len(furniture_df)} items")
        
        # 카테고리별 통계
        if 'item_cat' in furniture_df.columns:
            category_stats = furniture_df['item_cat'].value_counts()
            logger.info("Category distribution:")
            for category, count in category_stats.items():
                logger.info(f"  {category}: {count} items")
        
        # 샘플 데이터 출력
        logger.info("\nSample data:")
        logger.info(furniture_df.head())
        
        return furniture_df
        
    except Exception as e:
        logger.error(f"Error creating furniture database: {str(e)}")
        raise e

def create_sample_database():
    """샘플 가구 데이터베이스를 생성합니다 (테스트용)."""
    
    logger.info("Creating sample furniture database...")
    
    # 샘플 데이터 생성
    sample_data = []
    categories = ['bed', 'chair', 'dresser', 'lamp', 'sofa', 'table']
    
    for i in range(100):  # 100개 샘플 아이템
        category = categories[i % len(categories)]
        
        item = {
            'item_name': f'Sample {category.title()} {i+1}',
            'item_cat': category,
            'item_price': np.random.uniform(50, 500),
            'item_url': f'https://example.com/images/{category}_{i+1}.jpg',
            'prod_url': f'https://example.com/products/{category}_{i+1}',
            'vector': np.random.rand(256)  # 256차원 랜덤 벡터
        }
        sample_data.append(item)
    
    # DataFrame 생성
    furniture_df = pd.DataFrame(sample_data)
    
    # 데이터 저장
    output_path = "furniture_data/furniture_database.pkl"
    furniture_df.to_pickle(output_path)
    
    logger.info(f"Sample furniture database saved to {output_path}")
    logger.info(f"Created {len(furniture_df)} sample items")
    
    return furniture_df

if __name__ == "__main__":
    try:
        # 기존 IKEA 데이터가 있으면 사용, 없으면 샘플 데이터 생성
        ikea_csv_path = "example/ObjectDetectionProject-IKEAFurnituresRecommender/ikea/ikea-data/ikea_final_model0.csv"
        
        if os.path.exists(ikea_csv_path):
            logger.info("Found IKEA data, creating database from existing data...")
            create_furniture_database()
        else:
            logger.info("IKEA data not found, creating sample database...")
            create_sample_database()
            
    except Exception as e:
        logger.error(f"Failed to create database: {str(e)}")
        sys.exit(1)
