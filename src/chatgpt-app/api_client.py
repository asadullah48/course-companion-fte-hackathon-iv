"""
Course Companion API Client for ChatGPT App

This module simulates how the ChatGPT app would interact with the backend API
based on the specification. It includes functions for all the API endpoints
defined in the action manifest.
"""

import json
import requests
from typing import Dict, List, Optional, Any
from datetime import datetime
import time

class CourseCompanionAPIClient:
    """
    API client for the Course Companion backend.
    Simulates how the ChatGPT app would interact with the backend API.
    """
    
    def __init__(self, base_url: str, auth_token: Optional[str] = None):
        self.base_url = base_url.rstrip('/')
        self.auth_token = auth_token
        self.session = requests.Session()
        
        if self.auth_token:
            self.session.headers.update({
                'Authorization': f'Bearer {self.auth_token}',
                'Content-Type': 'application/json'
            })
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """
        Make an HTTP request to the API.
        """
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            if response.status_code == 404:
                return {"error": "not_found", "message": "Resource not found"}
            elif response.status_code == 403:
                return {"error": "access_denied", "message": "Access denied - premium content or insufficient permissions"}
            elif response.status_code == 429:
                return {"error": "rate_limited", "message": "Rate limit exceeded"}
            else:
                return {"error": "api_error", "message": f"API request failed: {str(e)}"}
        except requests.exceptions.RequestException as e:
            return {"error": "network_error", "message": f"Network error: {str(e)}"}
    
    # Content Delivery API
    def get_chapter_content(self, chapter_id: str, format_type: str = "markdown") -> Dict[str, Any]:
        """
        Get chapter content verbatim from the backend.
        """
        params = {"format": format_type} if format_type else {}
        return self._make_request("GET", f"/chapters/{chapter_id}", params=params)
    
    def list_chapters(self, module: Optional[int] = None, include_locked: bool = False) -> Dict[str, Any]:
        """
        List all chapters with metadata and completion status.
        """
        params = {}
        if module is not None:
            params["module"] = module
        if include_locked:
            params["include_locked"] = "true"
        
        return self._make_request("GET", "/chapters", params=params)
    
    def get_module_overview(self, module_id: int) -> Dict[str, Any]:
        """
        Get module metadata and chapter list.
        """
        return self._make_request("GET", f"/modules/{module_id}")
    
    # Navigation API
    def get_next_chapter(self, chapter_id: str) -> Dict[str, Any]:
        """
        Get the next chapter in sequence based on completion status.
        """
        return self._make_request("GET", f"/chapters/{chapter_id}/next")
    
    def get_full_sequence(self) -> Dict[str, Any]:
        """
        Get the complete ordered list of chapters with progress.
        """
        return self._make_request("GET", "/navigation/sequence")
    
    def get_recommended_action(self) -> Dict[str, Any]:
        """
        Get recommended next action based on progress.
        """
        return self._make_request("GET", "/navigation/recommend")
    
    # Quiz API
    def list_quizzes(self, chapter_id: Optional[str] = None, module_id: Optional[int] = None, 
                     quiz_type: Optional[str] = None) -> Dict[str, Any]:
        """
        List available quizzes filtered by chapter or module.
        """
        params = {}
        if chapter_id:
            params["chapter_id"] = chapter_id
        if module_id:
            params["module_id"] = module_id
        if quiz_type:
            params["type"] = quiz_type
        
        return self._make_request("GET", "/quizzes", params=params)
    
    def get_quiz_questions(self, quiz_id: str, shuffle: bool = False) -> Dict[str, Any]:
        """
        Get quiz questions without correct answers.
        """
        params = {"shuffle": "true" if shuffle else "false"}
        return self._make_request("GET", f"/quizzes/{quiz_id}", params=params)
    
    def submit_quiz_answers(self, quiz_id: str, attempt_id: str, answers: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        Submit quiz answers for grading.
        """
        payload = {
            "attempt_id": attempt_id,
            "answers": answers
        }
        return self._make_request("POST", f"/quizzes/{quiz_id}/submit", json=payload)
    
    def get_quiz_results(self, quiz_id: str, attempt_id: str) -> Dict[str, Any]:
        """
        Get detailed results for a specific quiz attempt.
        """
        return self._make_request("GET", f"/quizzes/{quiz_id}/results/{attempt_id}")
    
    # Progress API
    def get_user_progress(self, user_id: str, include_chapters: bool = False) -> Dict[str, Any]:
        """
        Get overall progress across all modules and chapters.
        """
        params = {"include_chapters": "true" if include_chapters else "false"}
        return self._make_request("GET", f"/progress/{user_id}", params=params)
    
    def mark_chapter_complete(self, user_id: str, chapter_id: str, completion_type: str, 
                             time_spent_minutes: int, quiz_attempt_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Mark a chapter as completed.
        """
        payload = {
            "completion_type": completion_type,
            "time_spent_minutes": time_spent_minutes
        }
        if quiz_attempt_id:
            payload["quiz_attempt_id"] = quiz_attempt_id
        
        return self._make_request("PUT", f"/progress/{user_id}/chapters/{chapter_id}", json=payload)
    
    def get_user_streak(self, user_id: str, history_days: int = 30) -> Dict[str, Any]:
        """
        Get learning streak and history.
        """
        params = {"history_days": history_days}
        return self._make_request("GET", f"/progress/{user_id}/streak", params=params)
    
    def get_user_achievements(self, user_id: str, filter_type: str = "all") -> Dict[str, Any]:
        """
        Get user achievements (earned and locked).
        """
        params = {"filter": filter_type}
        return self._make_request("GET", f"/progress/{user_id}/achievements", params=params)
    
    def log_learning_time(self, user_id: str, chapter_id: str, duration_minutes: int, 
                         activity_type: str) -> Dict[str, Any]:
        """
        Log time spent learning for streak and analytics.
        """
        payload = {
            "chapter_id": chapter_id,
            "duration_minutes": duration_minutes,
            "activity_type": activity_type
        }
        return self._make_request("POST", f"/progress/{user_id}/time", json=payload)


# Example usage demonstrating the API interactions
def demonstrate_api_usage():
    """
    Demonstrates how the ChatGPT app would use the API client.
    """
    print("Course Companion API Client Demo")
    print("=" * 50)
    
    # Initialize client (in real usage, this would have a real token)
    client = CourseCompanionAPIClient("https://api.coursecompanion.dev/api/v1", "fake-token")
    
    # Example 1: Concept Explanation Flow
    print("\n1. Concept Explanation Flow:")
    print("-" * 30)
    
    # User asks "Explain MCP to me"
    chapter_content = client.get_chapter_content("ch3-mcp-integration")
    if "error" not in chapter_content:
        print(f"Retrieved chapter: {chapter_content.get('title', 'Unknown')}")
        print(f"Content length: {len(chapter_content.get('content', ''))} characters")
    else:
        print(f"Error retrieving content: {chapter_content['error']}")
    
    # Example 2: Quiz Session Flow
    print("\n2. Quiz Session Flow:")
    print("-" * 30)
    
    # Get available quizzes for Chapter 1
    quizzes = client.list_quizzes(chapter_id="ch1-intro-to-agents")
    if "error" not in quizzes and quizzes.get("quizzes"):
        quiz_id = quizzes["quizzes"][0]["quiz_id"]
        print(f"Selected quiz: {quiz_id}")
        
        # Get quiz questions
        quiz_data = client.get_quiz_questions(quiz_id)
        if "error" not in quiz_data:
            print(f"Retrieved {len(quiz_data.get('questions', []))} questions")
            print(f"Attempt ID: {quiz_data.get('attempt_id')}")
        else:
            print(f"Error getting quiz: {quiz_data['error']}")
    else:
        print("No quizzes available for Chapter 1")
    
    # Example 3: Progress Check Flow
    print("\n3. Progress Check Flow:")
    print("-" * 30)
    
    user_id = "user-12345"
    progress = client.get_user_progress(user_id)
    if "error" not in progress:
        print(f"Overall progress: {progress.get('overall', {}).get('percentage', 0)}%")
        
        streak = client.get_user_streak(user_id)
        if "error" not in streak:
            print(f"Current streak: {streak.get('current_streak', 0)} days")
        
        achievements = client.get_user_achievements(user_id)
        if "error" not in achievements:
            print(f"Achievements earned: {achievements.get('earned_count', 0)}")
    else:
        print(f"Error retrieving progress: {progress['error']}")
    
    print("\nDemo completed successfully!")


if __name__ == "__main__":
    demonstrate_api_usage()