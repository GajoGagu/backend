from fastapi import APIRouter
from typing import List
from pydantic import BaseModel


class Ad(BaseModel):
    id: str
    image_url: str
    target_url: str
    title: str
    description: str = None


router = APIRouter(tags=["Ads"])


@router.get("/ads", response_model=List[Ad])
def get_ads():
    """
    서버에서 지정한 고정된 광고 목록을 가져옵니다.
    """
    # 미리 정의된 고정 광고 목록
    ads = [
        Ad(
            id="ad1",
            image_url="https://thediversitytimes.ca/wp-content/uploads/2021/10/bulletin-img_new.png",
            target_url="https://example.com/product/premium-sofa",
            title="프리미엄 소파 컬렉션",
            description="새로운 프리미엄 소파 컬렉션을 20% 할인된 가격에 만나보세요"
        ),
        Ad(
            id="ad2",
            image_url="https://example.com/ads/furniture2.jpg",
            target_url="https://example.com/seasonal-sale",
            title="시즌 세일",
            description="모든 침실 가구 최대 30% 할인 이벤트"
        ),
        Ad(
            id="ad3",
            image_url="https://example.com/ads/furniture3.jpg",
            target_url="https://example.com/new-arrivals",
            title="신상품 소개",
            description="최신 디자인의 가구 컬렉션이 출시되었습니다"
        )
    ]
    return ads