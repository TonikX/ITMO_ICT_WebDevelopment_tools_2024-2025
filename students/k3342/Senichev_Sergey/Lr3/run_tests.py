import requests
import time
import json
from typing import Dict, Any


def test_api_endpoint(url: str, method: str = "GET", data: Dict[Any, Any] = None) -> Dict[Any, Any]:
    try:
        if method == "GET":
            response = requests.get(url, timeout=30)
        elif method == "POST":
            response = requests.post(url, json=data, timeout=30)
        else:
            raise ValueError(f"Unsupported method: {method}")
        
        response.raise_for_status()
        return response.json()
    
    except requests.exceptions.RequestException as e:
        print(f"Error testing {url}: {e}")
        return {"error": str(e)}


def test_task_management_api():
    print("=== Testing Task Management API ===")
    
    base_url = "http://localhost:8000"
    
    print("1. Testing root endpoint...")
    result = test_api_endpoint(f"{base_url}/")
    print(f"Root: {result}")
    
    print("\n2. Testing tasks endpoint...")
    result = test_api_endpoint(f"{base_url}/tasks/")
    print(f"Tasks: {result}")
    
    print("\n3. Testing sprints endpoint...")
    result = test_api_endpoint(f"{base_url}/sprints/")
    print(f"Sprints: {result}")
    
    print("\n4. Testing sprint creation...")
    sprint_data = {
        "title": "Test Sprint",
        "start_at": "2024-01-01T00:00:00",
        "end_at": "2024-01-31T23:59:59"
    }
    result = test_api_endpoint(f"{base_url}/sprints/", "POST", sprint_data)
    print(f"Create sprint: {result}")
    
    print("\n5. Testing task creation...")
    task_data = {
        "summary": "Test Task",
        "priority": "major",
        "description": "Test task description",
        "planned_end_at": "2024-01-15T12:00:00",
        "status": "open",
        "sprint_id": None
    }
    result = test_api_endpoint(f"{base_url}/tasks/", "POST", task_data)
    print(f"Create task: {result}")


def test_parser_api():
    print("\n=== Testing Parser API ===")
    
    base_url = "http://localhost:8001"
    
    print("1. Testing parser root endpoint...")
    result = test_api_endpoint(f"{base_url}/")
    print(f"Parser root: {result}")
    
    print("\n2. Testing parser health...")
    result = test_api_endpoint(f"{base_url}/health")
    print(f"Parser health: {result}")
    
    print("\n3. Testing synchronous parsing...")
    parse_data = {
        "repositories": ["python/cpython"]
    }
    result = test_api_endpoint(f"{base_url}/parse", "POST", parse_data)
    print(f"Sync parse: {result}")
    
    print("\n4. Testing asynchronous parsing...")
    result = test_api_endpoint(f"{base_url}/parse/async", "POST", parse_data)
    print(f"Async parse: {result}")
    
    if "task_id" in result:
        task_id = result["task_id"]
        print(f"\n5. Checking task status for {task_id}...")
        
        for i in range(5):
            time.sleep(2)
            status_result = test_api_endpoint(f"{base_url}/task/{task_id}")
            print(f"Task status (attempt {i+1}): {status_result}")
            
            if status_result.get("status") in ["SUCCESS", "FAILURE"]:
                break


def test_integration():
    """
    Тестирование интеграции между сервисами
    """
    print("\n=== Testing Integration ===")
    
    app_base_url = "http://localhost:8000"
    
    print("1. Testing parser call from main app...")
    parse_data = {
        "repositories": ["django/django"]
    }
    result = test_api_endpoint(f"{app_base_url}/parse", "POST", parse_data)
    print(f"App -> Parser sync: {result}")
    
    print("\n2. Testing async parser call from main app...")
    result = test_api_endpoint(f"{app_base_url}/parse/async", "POST", parse_data)
    print(f"App -> Parser async: {result}")


def main():
    print("Starting API tests...")
    print("Make sure all services are running with: docker-compose up")
    
    print("\nWaiting for services to start...")
    time.sleep(5)
    
    try:
        test_task_management_api()
        test_parser_api()
        test_integration()
        
        print("\n=== All tests completed ===")
        
    except KeyboardInterrupt:
        print("\nTests interrupted by user")
    except Exception as e:
        print(f"\nError during testing: {e}")


if __name__ == "__main__":
    main()