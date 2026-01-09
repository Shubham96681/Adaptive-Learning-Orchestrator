#!/usr/bin/env python3
"""
Comprehensive API Test Script for Adaptive Learning Orchestrator
Run this script to verify all endpoints are working correctly.
"""

import requests
import json
import sys
from typing import Dict, Any
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000"
TIMEOUT = 10

# Colors for terminal output (works on Windows 10+ and Unix)
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_header(text: str):
    """Print a formatted header."""
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*60}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}{text.center(60)}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*60}{Colors.RESET}\n")

def print_success(text: str):
    """Print success message."""
    print(f"{Colors.GREEN}[PASS] {text}{Colors.RESET}")

def print_error(text: str):
    """Print error message."""
    print(f"{Colors.RED}[FAIL] {text}{Colors.RESET}")

def print_info(text: str):
    """Print info message."""
    print(f"{Colors.BLUE}[INFO] {text}{Colors.RESET}")

def print_warning(text: str):
    """Print warning message."""
    print(f"{Colors.YELLOW}[WARN] {text}{Colors.RESET}")

def test_health() -> bool:
    """Test the health endpoint."""
    print_header("Testing Health Endpoint")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=TIMEOUT)
        if response.status_code == 200:
            data = response.json()
            print_success(f"Health endpoint responded: {data}")
            return True
        else:
            print_error(f"Health endpoint returned status {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Failed to connect to server: {e}")
        print_warning("Make sure the server is running: uvicorn app.main:app --reload")
        return False

def test_problem_stats() -> bool:
    """Test the problem statistics endpoint."""
    print_header("Testing Problem Statistics")
    try:
        response = requests.get(f"{BASE_URL}/api/problems/stats", timeout=TIMEOUT)
        if response.status_code == 200:
            data = response.json()
            total = data.get("total_problems", 0)
            topics = data.get("topics", {})
            difficulties = data.get("difficulty_distribution", {})
            
            print_success(f"Total problems: {total}")
            print_info(f"Topics: {', '.join(f'{k}({v})' for k, v in topics.items())}")
            print_info(f"Difficulty distribution: {difficulties}")
            
            if total > 0:
                print_success("Problems are loaded successfully")
                return True
            else:
                print_warning("No problems found in database")
                return False
        else:
            print_error(f"Stats endpoint returned status {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Failed to get stats: {e}")
        return False

def test_get_problems() -> bool:
    """Test getting all problems."""
    print_header("Testing GET /api/problems")
    try:
        response = requests.get(f"{BASE_URL}/api/problems", timeout=TIMEOUT)
        if response.status_code == 200:
            problems = response.json()
            print_success(f"Retrieved {len(problems)} problems")
            if len(problems) > 0:
                print_info(f"Sample problem: {problems[0].get('id', 'N/A')}")
                return True
            return False
        else:
            print_error(f"GET /api/problems returned status {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Failed to get problems: {e}")
        return False

def test_get_problem_by_id() -> bool:
    """Test getting a specific problem by ID."""
    print_header("Testing GET /api/problems/{id}")
    try:
        # First, get a problem ID
        response = requests.get(f"{BASE_URL}/api/problems", timeout=TIMEOUT)
        if response.status_code != 200 or len(response.json()) == 0:
            print_warning("No problems available to test")
            return False
        
        problem_id = response.json()[0]["id"]
        
        # Now get that specific problem
        response = requests.get(f"{BASE_URL}/api/problems/{problem_id}", timeout=TIMEOUT)
        if response.status_code == 200:
            problem = response.json()
            print_success(f"Retrieved problem: {problem.get('text', 'N/A')[:50]}...")
            return True
        else:
            print_error(f"GET /api/problems/{problem_id} returned status {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Failed to get problem by ID: {e}")
        return False

def test_create_problem() -> str:
    """Test creating a new problem."""
    print_header("Testing POST /api/problems")
    try:
        payload = {
            "text": f"Test problem created at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "topic": "Algebra",
            "difficulty": 2,
            "estimated_time_to_solve_minutes": 5
        }
        response = requests.post(
            f"{BASE_URL}/api/problems",
            json=payload,
            timeout=TIMEOUT
        )
        if response.status_code == 201:
            problem = response.json()
            problem_id = problem.get("id")
            print_success(f"Created problem with ID: {problem_id}")
            return problem_id
        else:
            print_error(f"POST /api/problems returned status {response.status_code}")
            print_error(f"Response: {response.text}")
            return None
    except Exception as e:
        print_error(f"Failed to create problem: {e}")
        return None

def test_update_problem(problem_id: str) -> bool:
    """Test updating a problem."""
    print_header("Testing PUT /api/problems/{id}")
    if not problem_id:
        print_warning("Skipping update test - no problem ID available")
        return False
    
    try:
        payload = {"difficulty": 3}
        response = requests.put(
            f"{BASE_URL}/api/problems/{problem_id}",
            json=payload,
            timeout=TIMEOUT
        )
        if response.status_code == 200:
            problem = response.json()
            print_success(f"Updated problem difficulty to {problem.get('difficulty')}")
            return True
        else:
            print_error(f"PUT /api/problems/{problem_id} returned status {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Failed to update problem: {e}")
        return False

def test_delete_problem(problem_id: str) -> bool:
    """Test deleting a problem."""
    print_header("Testing DELETE /api/problems/{id}")
    if not problem_id:
        print_warning("Skipping delete test - no problem ID available")
        return False
    
    try:
        response = requests.delete(f"{BASE_URL}/api/problems/{problem_id}", timeout=TIMEOUT)
        if response.status_code == 204:
            print_success("Problem deleted successfully")
            return True
        else:
            print_error(f"DELETE /api/problems/{problem_id} returned status {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Failed to delete problem: {e}")
        return False

def test_assessment_generation(strategy: str, student_id: str, mastered: list, goals: list, time_limit: int) -> bool:
    """Test assessment generation with a specific strategy."""
    print_header(f"Testing Assessment Generation - {strategy}")
    try:
        payload = {
            "student_profile": {
                "id": student_id,
                "mastered_topics": mastered,
                "learning_goals": goals
            },
            "assessment_request": {
                "pedagogical_strategy": strategy,
                "max_total_time_minutes": time_limit
            }
        }
        
        response = requests.post(
            f"{BASE_URL}/api/assessments/generate",
            json=payload,
            timeout=TIMEOUT
        )
        
        if response.status_code == 201:
            assessment = response.json()
            
            # Validate response structure
            has_id = "assessment_id" in assessment
            has_planner = "planner_output" in assessment
            has_executor = "executor_output" in assessment
            
            if has_id and has_planner and has_executor:
                planner = assessment["planner_output"]
                executor = assessment["executor_output"]
                
                print_success(f"Assessment ID: {assessment['assessment_id']}")
                print_info(f"Strategy: {planner['assessment_plan']['strategy']}")
                print_info(f"Topics in plan: {len(planner['assessment_plan']['topic_rules'])}")
                print_info(f"Problems selected: {len(executor['selected_problems'])}")
                print_info(f"Total estimated time: {executor['total_estimated_time']} minutes")
                
                # Check if problems were actually selected
                if len(executor['selected_problems']) > 0:
                    print_success("Problems were successfully selected by executor")
                    # Show first problem as example
                    first_problem = executor['selected_problems'][0]
                    print_info(f"Sample problem: {first_problem['text'][:60]}...")
                else:
                    print_warning("No problems were selected (may be due to topic/difficulty mismatch)")
                
                return True
            else:
                print_error("Response missing required fields")
                return False
        else:
            print_error(f"POST /api/assessments/generate returned status {response.status_code}")
            print_error(f"Response: {response.text}")
            return False
    except Exception as e:
        print_error(f"Failed to generate assessment: {e}")
        return False

def test_error_handling() -> bool:
    """Test error handling for invalid requests."""
    print_header("Testing Error Handling")
    all_passed = True
    
    # Test 404 for non-existent problem
    try:
        response = requests.get(f"{BASE_URL}/api/problems/non-existent-id-12345", timeout=TIMEOUT)
        if response.status_code == 404:
            print_success("404 error handled correctly for non-existent problem")
        else:
            print_error(f"Expected 404, got {response.status_code}")
            all_passed = False
    except Exception as e:
        print_error(f"Error testing 404: {e}")
        all_passed = False
    
    # Test 422 for invalid request
    try:
        response = requests.post(
            f"{BASE_URL}/api/assessments/generate",
            json={"invalid": "request"},
            timeout=TIMEOUT
        )
        if response.status_code == 422:
            print_success("422 error handled correctly for invalid request")
        else:
            print_error(f"Expected 422, got {response.status_code}")
            all_passed = False
    except Exception as e:
        print_error(f"Error testing 422: {e}")
        all_passed = False
    
    return all_passed

def main():
    """Run all tests."""
    print(f"\n{Colors.BOLD}{Colors.CYAN}")
    print("=" * 60)
    print(" " * 10 + "Adaptive Learning Orchestrator API Tests" + " " * 10)
    print("=" * 60)
    print(f"{Colors.RESET}")
    
    results = {
        "health": False,
        "stats": False,
        "get_all": False,
        "get_by_id": False,
        "create": False,
        "update": False,
        "delete": False,
        "assessment_new_topic": False,
        "assessment_review": False,
        "assessment_challenge": False,
        "error_handling": False
    }
    
    # Basic connectivity test
    results["health"] = test_health()
    if not results["health"]:
        print_error("\nCannot connect to server. Please make sure it's running:")
        print_info("Run: uvicorn app.main:app --reload")
        sys.exit(1)
    
    # Problem endpoints
    results["stats"] = test_problem_stats()
    results["get_all"] = test_get_problems()
    results["get_by_id"] = test_get_problem_by_id()
    
    # CRUD operations
    created_problem_id = test_create_problem()
    results["create"] = created_problem_id is not None
    
    if created_problem_id:
        results["update"] = test_update_problem(created_problem_id)
        results["delete"] = test_delete_problem(created_problem_id)
    
    # Assessment generation - all strategies
    results["assessment_new_topic"] = test_assessment_generation(
        "NEW_TOPIC_INTRODUCTION",
        "student-test-1",
        ["Arithmetic", "Algebra"],
        ["Calculus", "Geometry"],
        60
    )
    
    results["assessment_review"] = test_assessment_generation(
        "REVIEW",
        "student-test-2",
        ["Algebra", "Geometry"],
        ["Statistics"],
        45
    )
    
    results["assessment_challenge"] = test_assessment_generation(
        "CHALLENGE",
        "student-test-3",
        ["Arithmetic", "Algebra", "Geometry"],
        ["Calculus", "Statistics"],
        90
    )
    
    # Error handling
    results["error_handling"] = test_error_handling()
    
    # Summary
    print_header("Test Summary")
    total_tests = len(results)
    passed_tests = sum(1 for v in results.values() if v)
    
    for test_name, passed in results.items():
        status = f"{Colors.GREEN}PASS{Colors.RESET}" if passed else f"{Colors.RED}FAIL{Colors.RESET}"
        print(f"{status} - {test_name.replace('_', ' ').title()}")
    
    print(f"\n{Colors.BOLD}Results: {passed_tests}/{total_tests} tests passed{Colors.RESET}")
    
    if passed_tests == total_tests:
        print(f"\n{Colors.GREEN}{Colors.BOLD}*** All tests passed! Everything is working correctly! ***{Colors.RESET}\n")
        return 0
    else:
        print(f"\n{Colors.YELLOW}{Colors.BOLD}WARNING: Some tests failed. Please review the output above.{Colors.RESET}\n")
        return 1

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}Tests interrupted by user{Colors.RESET}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{Colors.RED}Unexpected error: {e}{Colors.RESET}")
        sys.exit(1)

