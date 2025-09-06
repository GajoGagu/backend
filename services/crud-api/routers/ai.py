from datetime import datetime
from fastapi import APIRouter
from ..models import AIStyleMatchRequest, AIStyleMatchResult, AIMatch, Product
from ..database import products_db

router = APIRouter(prefix="/ai", tags=["ai"])


@router.post("/style-match", response_model=AIStyleMatchResult)
def ai_style_match(request: AIStyleMatchRequest):
    # Simulate AI processing
    matches = []
    for product in list(products_db.values())[:request.top_k]:
        score = 0.8 + (hash(product["id"]) % 20) / 100  # Simulate score
        matches.append(AIMatch(
            product=Product(**product),
            score=score
        ))
    
    matches.sort(key=lambda x: x.score, reverse=True)
    
    return AIStyleMatchResult(
        matches=matches[:request.top_k],
        generated_at=datetime.now().isoformat()
    )
