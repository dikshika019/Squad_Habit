import requests
import json

BASE_URL = "http://localhost:8000/api"

def test_auth():
    print("Testing Authentication...")
    # This would require a Google OAuth flow, but we'll test token validation
    token = input("Enter your JWT token from auth callback: ")
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(f"{BASE_URL}/auth/me", headers=headers)
    print(f"User info: {response.json()}")
    return token

def test_squad(token):
    print("\nTesting Squad Creation...")
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    # Create squad
    squad_data = {"name": "Test Squad", "description": "Testing squad creation"}
    response = requests.post(f"{BASE_URL}/squads/", json=squad_data, headers=headers)
    squad = response.json()
    print(f"Created squad: {squad}")
    return squad["id"]

def test_habit(token, squad_id):
    print("\nTesting Habit Creation...")
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    habit_data = {"name": "Exercise", "description": "30 minutes daily"}
    response = requests.post(f"{BASE_URL}/habits/squad/{squad_id}", json=habit_data, headers=headers)
    habit = response.json()
    print(f"Created habit: {habit}")
    return habit["id"]

def test_mark_habit(token, habit_id):
    print("\nTesting Habit Marking...")
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.post(f"{BASE_URL}/habits/{habit_id}/mark", headers=headers)
    print(f"Mark result: {response.json()}")

def test_leaderboard(token, squad_id):
    print("\nTesting Leaderboard...")
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(f"{BASE_URL}/leaderboard/squad/{squad_id}", headers=headers)
    print(f"Leaderboard: {response.json()}")

if __name__ == "__main__":
    print("🚀 Starting Squad Habits API Tests\n")
    
    # Step 1: Get token (you'll need to go through Google OAuth first)
    token = test_auth()
    
    # Step 2: Create squad
    squad_id = test_squad(token)
    
    # Step 3: Create habit
    habit_id = test_habit(token, squad_id)
    
    # Step 4: Mark habit done
    test_mark_habit(token, habit_id)
    
    # Step 5: Check leaderboard
    test_leaderboard(token, squad_id)
    
    print("\n✅ All tests completed!")