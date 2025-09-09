#!/usr/bin/env python3

import httpx
import json

# Test the API endpoints manually
BASE_URL = "http://localhost:8000"

def test_signup():
    """Test user signup"""
    url = f"{BASE_URL}/auth/users/signup"
    data = {
        "email": "test@example.com",
        "password": "testpassword123",
        "name": "Test User",
        "phone": "010-1234-5678"
    }
    
    try:
        response = httpx.post(url, json=data)
        print(f"Signup Status: {response.status_code}")
        if response.status_code == 201:
            result = response.json()
            print(f"User ID: {result['user']['id']}")
            print(f"Access Token: {result['tokens']['access_token'][:20]}...")
            print(f"Refresh Token: {result['tokens']['refresh_token'][:20]}...")
            return result['tokens']['refresh_token']
        else:
            print(f"Error: {response.text}")
            return None
    except Exception as e:
        print(f"Exception: {e}")
        return None

def test_refresh(refresh_token):
    """Test token refresh"""
    url = f"{BASE_URL}/auth/users/refresh"
    data = {
        "refresh_token": refresh_token
    }
    
    try:
        response = httpx.post(url, json=data)
        print(f"Refresh Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"New Access Token: {result['tokens']['access_token'][:20]}...")
            print(f"New Refresh Token: {result['tokens']['refresh_token'][:20]}...")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Exception: {e}")

def test_logout(access_token):
    """Test logout"""
    url = f"{BASE_URL}/auth/users/logout"
    data = {
        "access_token": access_token
    }
    
    try:
        response = httpx.post(url, json=data)
        print(f"Logout Status: {response.status_code}")
        if response.status_code == 200:
            print(f"Success: {response.json()}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    print("Testing API endpoints...")
    
    # Test signup
    refresh_token = test_signup()
    
    if refresh_token:
        # Test refresh
        test_refresh(refresh_token)
        
        # Test logout (we'll need to get a new access token first)
        # For now, just test with the original token
        print("\nNote: Logout test would need a valid access token")
