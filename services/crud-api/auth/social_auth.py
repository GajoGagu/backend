import httpx
from typing import Optional
from models.auth import SocialUserInfo


async def verify_google_token(access_token: str) -> Optional[SocialUserInfo]:
    """Verify Google access token and get user info"""
    try:
        async with httpx.AsyncClient() as client:
            # Get user info from Google
            response = await client.get(
                "https://www.googleapis.com/oauth2/v2/userinfo",
                headers={"Authorization": f"Bearer {access_token}"}
            )
            
            if response.status_code == 200:
                data = response.json()
                return SocialUserInfo(
                    id=data.get("id"),
                    email=data.get("email"),
                    name=data.get("name"),
                    picture=data.get("picture")
                )
    except Exception as e:
        print(f"Google token verification error: {e}")
    
    return None


async def verify_kakao_token(access_token: str) -> Optional[SocialUserInfo]:
    """Verify Kakao access token and get user info"""
    try:
        async with httpx.AsyncClient() as client:
            # Get user info from Kakao
            response = await client.get(
                "https://kapi.kakao.com/v2/user/me",
                headers={"Authorization": f"Bearer {access_token}"}
            )
            
            if response.status_code == 200:
                data = response.json()
                kakao_account = data.get("kakao_account", {})
                profile = kakao_account.get("profile", {})
                
                return SocialUserInfo(
                    id=str(data.get("id")),
                    email=kakao_account.get("email"),
                    name=profile.get("nickname"),
                    picture=profile.get("profile_image_url")
                )
    except Exception as e:
        print(f"Kakao token verification error: {e}")
    
    return None


async def verify_social_token(access_token: str, provider: str) -> Optional[SocialUserInfo]:
    """Verify social login token based on provider"""
    if provider == "google":
        return await verify_google_token(access_token)
    elif provider == "kakao":
        return await verify_kakao_token(access_token)
    else:
        return None
