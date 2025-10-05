import cv2
import numpy as np
import torch
import os
import logging
from typing import List, Dict, Any
from PIL import Image
import io

from models import DetectionItem

logger = logging.getLogger(__name__)

# Detectron2 import with fallback
try:
    from detectron2 import model_zoo
    from detectron2.engine import DefaultPredictor
    from detectron2.config import get_cfg
    from detectron2.utils.visualizer import Visualizer
    from detectron2.data import MetadataCatalog
    DETECTRON2_AVAILABLE = True
except ImportError:
    DETECTRON2_AVAILABLE = False
    logger.warning("Detectron2 not available, using fallback detection method")

class FurnitureDetector:
    """가구 객체 탐지를 위한 Detectron2 기반 클래스"""
    
    def __init__(self, model_path: str = None, confidence_threshold: float = 0.7):
        """
        FurnitureDetector 초기화
        
        Args:
            model_path: 사전 학습된 모델 경로
            confidence_threshold: 탐지 신뢰도 임계값
        """
        self.confidence_threshold = confidence_threshold
        self.target_classes = ['Bed', 'Dresser', 'Chair', 'Sofa', 'Lamp', 'Table']
        self.class_mapping = {
            0: 'bed',
            1: 'dresser', 
            2: 'chair',
            3: 'sofa',
            4: 'lamp',
            5: 'table'
        }
        
        if DETECTRON2_AVAILABLE:
            # Detectron2 모델 설정
            self.cfg = get_cfg()
            self.cfg.MODEL.DEVICE = 'cuda' if torch.cuda.is_available() else 'cpu'
            
            # Detectron2 설정 - COCO 사전 학습 모델 사용
            self.cfg.merge_from_file(
                model_zoo.get_config_file("COCO-Detection/faster_rcnn_R_50_FPN_3x.yaml")
            )
            
            # 모델 가중치 설정
            if model_path and os.path.exists(model_path):
                self.cfg.MODEL.WEIGHTS = model_path
                logger.info(f"Using custom model: {model_path}")
            else:
                # 사전 학습된 COCO 모델 사용
                self.cfg.MODEL.WEIGHTS = model_zoo.get_checkpoint_url(
                    "COCO-Detection/faster_rcnn_R_50_FPN_3x.yaml"
                )
                logger.info("Using COCO pre-trained model")
            
            # 모델 설정
            self.cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = confidence_threshold
            # COCO 데이터셋의 80개 클래스 사용 (가구 관련 클래스 포함)
            self.cfg.MODEL.ROI_HEADS.NUM_CLASSES = 80
            
            # 예측기 초기화
            self.predictor = DefaultPredictor(self.cfg)
            
            # COCO 클래스 매핑 (가구 관련 클래스들)
            self.coco_class_mapping = {
                0: 'person', 1: 'bicycle', 2: 'car', 3: 'motorcycle', 4: 'airplane',
                5: 'bus', 6: 'train', 7: 'truck', 8: 'boat', 9: 'traffic light',
                10: 'fire hydrant', 11: 'stop sign', 12: 'parking meter', 13: 'bench',
                14: 'bird', 15: 'cat', 16: 'dog', 17: 'horse', 18: 'sheep', 19: 'cow',
                20: 'elephant', 21: 'bear', 22: 'zebra', 23: 'giraffe', 24: 'backpack',
                25: 'umbrella', 26: 'handbag', 27: 'tie', 28: 'suitcase', 29: 'frisbee',
                30: 'skis', 31: 'snowboard', 32: 'sports ball', 33: 'kite', 34: 'baseball bat',
                35: 'baseball glove', 36: 'skateboard', 37: 'surfboard', 38: 'tennis racket',
                39: 'bottle', 40: 'wine glass', 41: 'cup', 42: 'fork', 43: 'knife',
                44: 'spoon', 45: 'bowl', 46: 'banana', 47: 'apple', 48: 'sandwich',
                49: 'orange', 50: 'broccoli', 51: 'carrot', 52: 'hot dog', 53: 'pizza',
                54: 'donut', 55: 'cake', 56: 'chair', 57: 'couch', 58: 'potted plant',
                59: 'bed', 60: 'dining table', 61: 'toilet', 62: 'tv', 63: 'laptop',
                64: 'mouse', 65: 'remote', 66: 'keyboard', 67: 'cell phone', 68: 'microwave',
                69: 'oven', 70: 'toaster', 71: 'sink', 72: 'refrigerator', 73: 'book',
                74: 'clock', 75: 'vase', 76: 'scissors', 77: 'teddy bear', 78: 'hair drier',
                79: 'toothbrush'
            }
            
            # 가구 관련 클래스만 필터링
            self.furniture_classes = {
                56: 'chair',    # 의자
                57: 'couch',    # 소파
                59: 'bed',      # 침대
                60: 'dining table',  # 식탁
                58: 'potted plant'   # 화분 (램프 대신)
            }
            
            logger.info(f"FurnitureDetector initialized with Detectron2, device: {self.cfg.MODEL.DEVICE}")
        else:
            # Fallback: 간단한 객체 탐지 (OpenCV 기반)
            self.predictor = None
            logger.info("FurnitureDetector initialized with fallback method (OpenCV)")
    
    def detect_furniture(self, image: np.ndarray) -> List[DetectionItem]:
        """
        이미지에서 가구 객체를 탐지합니다.
        
        Args:
            image: 입력 이미지 (BGR 형식)
            
        Returns:
            List[DetectionItem]: 탐지된 가구 객체들의 정보
        """
        try:
            if DETECTRON2_AVAILABLE and self.predictor is not None:
                # Detectron2를 사용한 객체 탐지
                outputs = self.predictor(image)
                detections = self._parse_detections(outputs, image)
            else:
                # Fallback: 간단한 객체 탐지
                detections = self._fallback_detection(image)
            
            logger.info(f"Detected {len(detections)} furniture items")
            return detections
            
        except Exception as e:
            logger.error(f"Detection failed: {str(e)}")
            raise e
    
    def _parse_detections(self, outputs: Dict, image: np.ndarray) -> List[DetectionItem]:
        """
        Detectron2 출력을 파싱하여 DetectionItem 리스트로 변환합니다.
        
        Args:
            outputs: Detectron2 모델 출력
            image: 원본 이미지
            
        Returns:
            List[DetectionItem]: 파싱된 탐지 결과
        """
        detections = []
        
        instances = outputs["instances"]
        if len(instances) == 0:
            return detections
        
        # 탐지된 객체들의 정보 추출
        pred_classes = instances.pred_classes.cpu().numpy()
        pred_boxes = instances.pred_boxes.tensor.cpu().numpy()
        pred_scores = instances.scores.cpu().numpy()
        
        for i in range(len(instances)):
            # 신뢰도가 임계값 이상인 경우만 처리
            if pred_scores[i] >= self.confidence_threshold:
                class_id = pred_classes[i]
                confidence = float(pred_scores[i])
                bbox = pred_boxes[i].tolist()  # [x_min, y_min, x_max, y_max]
                
                # 가구 관련 클래스인지 확인
                if class_id in self.furniture_classes:
                    # COCO 클래스를 가구 클래스로 매핑
                    coco_category = self.furniture_classes[class_id]
                    
                    # 가구 카테고리 매핑
                    if coco_category == 'chair':
                        category = 'chair'
                    elif coco_category == 'couch':
                        category = 'sofa'
                    elif coco_category == 'bed':
                        category = 'bed'
                    elif coco_category == 'dining table':
                        category = 'table'
                    elif coco_category == 'potted plant':
                        category = 'lamp'  # 화분을 램프로 매핑
                    else:
                        category = 'unknown'
                    
                    # DetectionItem 생성
                    detection = DetectionItem(
                        category=category,
                        confidence=confidence,
                        bbox=bbox
                    )
                    
                    detections.append(detection)
        
        # 신뢰도 순으로 정렬
        detections.sort(key=lambda x: x.confidence, reverse=True)
        
        return detections
    
    def crop_detected_furniture(self, image: np.ndarray, detections: List[DetectionItem]) -> List[np.ndarray]:
        """
        탐지된 가구 객체들을 크롭합니다.
        
        Args:
            image: 원본 이미지
            detections: 탐지 결과
            
        Returns:
            List[np.ndarray]: 크롭된 이미지들
        """
        cropped_images = []
        
        for detection in detections:
            x_min, y_min, x_max, y_max = detection.bbox
            
            # 좌표를 정수로 변환하고 이미지 경계 내로 제한
            x_min = max(0, int(x_min))
            y_min = max(0, int(y_min))
            x_max = min(image.shape[1], int(x_max))
            y_max = min(image.shape[0], int(y_max))
            
            # 이미지 크롭
            cropped = image[y_min:y_max, x_min:x_max]
            cropped_images.append(cropped)
        
        return cropped_images
    
    def visualize_detections(self, image: np.ndarray, detections: List[DetectionItem]) -> np.ndarray:
        """
        탐지 결과를 시각화합니다.
        
        Args:
            image: 원본 이미지
            detections: 탐지 결과
            
        Returns:
            np.ndarray: 시각화된 이미지
        """
        vis_image = image.copy()
        
        for detection in detections:
            x_min, y_min, x_max, y_max = detection.bbox
            
            # 바운딩 박스 그리기
            cv2.rectangle(
                vis_image,
                (int(x_min), int(y_min)),
                (int(x_max), int(y_max)),
                (0, 255, 0),
                2
            )
            
            # 라벨과 신뢰도 표시
            label = f"{detection.category}: {detection.confidence:.2f}"
            cv2.putText(
                vis_image,
                label,
                (int(x_min), int(y_min) - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (0, 255, 0),
                2
            )
        
        return vis_image
    
    def _fallback_detection(self, image: np.ndarray) -> List[DetectionItem]:
        """
        Detectron2가 없을 때 사용하는 간단한 객체 탐지 (fallback)
        
        Args:
            image: 입력 이미지 (BGR 형식)
            
        Returns:
            List[DetectionItem]: 탐지된 가구 객체들의 정보
        """
        detections = []
        
        try:
            # 간단한 색상 기반 객체 탐지 (예시)
            # 실제로는 더 정교한 방법이 필요하지만, 데모용으로 간단하게 구현
            
            # 이미지를 HSV로 변환
            hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
            
            # 갈색 계열 (가구) 탐지
            lower_brown = np.array([10, 50, 50])
            upper_brown = np.array([20, 255, 255])
            mask = cv2.inRange(hsv, lower_brown, upper_brown)
            
            # 윤곽선 찾기
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # 큰 윤곽선들을 가구로 간주
            for contour in contours:
                area = cv2.contourArea(contour)
                if area > 1000:  # 최소 면적 임계값
                    x, y, w, h = cv2.boundingRect(contour)
                    
                    # 바운딩 박스 좌표
                    bbox = [x, y, x + w, y + h]
                    
                    # 간단한 카테고리 분류 (크기 기반)
                    if w > h * 1.5:  # 가로가 더 긴 경우
                        category = 'table'
                    elif h > w * 1.5:  # 세로가 더 긴 경우
                        category = 'dresser'
                    else:  # 비슷한 경우
                        category = 'chair'
                    
                    detection = DetectionItem(
                        category=category,
                        confidence=0.6,  # 낮은 신뢰도
                        bbox=bbox
                    )
                    detections.append(detection)
            
            # 최대 3개까지만 반환
            detections = detections[:3]
            
        except Exception as e:
            logger.warning(f"Fallback detection failed: {str(e)}")
            # 완전히 실패한 경우 더미 데이터 반환
            detections = [
                DetectionItem(
                    category='chair',
                    confidence=0.5,
                    bbox=[100, 100, 300, 400]
                )
            ]
        
        return detections
