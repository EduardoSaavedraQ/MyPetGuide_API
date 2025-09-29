from fastapi.testclient import TestClient
from utils.supabase import get_supabase_client
from main import app
import json

client = TestClient(app)

def test_register_user_profile():
    
    supabase_client = get_supabase_client()
    
    user_data = {
        "email": "ado@test.com",
        "password": "password"
    }

    supabase_response = supabase_client.auth.sign_in_with_password(user_data)

    access_token = supabase_response.session.access_token

    profile_data = {
        "house_size": 120,
        "house_backyard_size": 50,
        "family_size": 4,
        "has_kids": True,
        "has_neighbors": False,
        "available_time_per_day": 3,
        "vet_access": True,
        "has_other_pets": False,
        "experience_with_pets": 2,
        "preferred_species": True
    }

    response = client.post("/user/profile", json=profile_data, headers={"Authorization": f"Bearer {access_token}"})
    print(response.json())

    assert response.status_code == 200