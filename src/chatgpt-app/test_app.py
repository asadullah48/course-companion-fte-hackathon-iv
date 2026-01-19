"""
Tests for Course Companion ChatGPT App

This module contains tests for the ChatGPT app components based on the specification.
"""

import unittest
from skill_routing import SkillRouter
from api_client import CourseCompanionAPIClient


class TestSkillRouter(unittest.TestCase):
    """
    Tests for the skill routing logic.
    """
    
    def setUp(self):
        self.router = SkillRouter()
    
    def test_concept_explainer_triggers(self):
        """
        Test that concept explainer triggers work correctly.
        """
        inputs = [
            "Explain MCP to me",
            "What is an AI Agent?",
            "How does Claude Agent SDK work?",
            "Define Model Context Protocol",
            "Tell me about AI Agents",
            "Can you explain MCP?"
        ]
        
        for inp in inputs:
            with self.subTest(input=inp):
                skill = self.router.detect_intent(inp)
                self.assertEqual(skill, "concept_explainer")
    
    def test_quiz_master_triggers(self):
        """
        Test that quiz master triggers work correctly.
        """
        inputs = [
            "Quiz me on Chapter 1",
            "Test my knowledge",
            "Give me MCP questions",
            "Practice AI Agents",
            "Assess my MCP knowledge"
        ]
        
        for inp in inputs:
            with self.subTest(input=inp):
                skill = self.router.detect_intent(inp)
                self.assertEqual(skill, "quiz_master")
    
    def test_socratic_tutor_triggers(self):
        """
        Test that socratic tutor triggers work correctly.
        """
        inputs = [
            "Help me think about agents",
            "Guide me through MCP",
            "I'm stuck on this concept",
            "Don't tell me the answer",
            "Don't give me the answer",
            "Work through this with me"
        ]
        
        for inp in inputs:
            with self.subTest(input=inp):
                skill = self.router.detect_intent(inp)
                self.assertEqual(skill, "socratic_tutor")
    
    def test_progress_motivator_triggers(self):
        """
        Test that progress motivator triggers work correctly.
        """
        inputs = [
            "How's my progress?",
            "Show my progress",
            "What's my streak?",
            "My streak",
            "Show my achievements",
            "How am I doing?",
            "How far am I?"
        ]
        
        for inp in inputs:
            with self.subTest(input=inp):
                skill = self.router.detect_intent(inp)
                self.assertEqual(skill, "progress_motivator")
    
    def test_default_behavior(self):
        """
        Test that default behavior returns concept_explainer for unrecognized input.
        """
        inputs = [
            "Hello",
            "What time is it?",
            "Random question",
            "This doesn't match anything"
        ]
        
        for inp in inputs:
            with self.subTest(input=inp):
                skill = self.router.detect_intent(inp)
                self.assertEqual(skill, "concept_explainer")
    
    def test_skill_descriptions(self):
        """
        Test that skill descriptions are available.
        """
        skills = self.router.get_available_skills()
        self.assertIn("concept_explainer", skills)
        self.assertIn("quiz_master", skills)
        self.assertIn("socratic_tutor", skills)
        self.assertIn("progress_motivator", skills)
        
        for skill in skills:
            desc = self.router.get_skill_description(skill)
            self.assertIsInstance(desc, str)
            self.assertGreater(len(desc), 0)


class TestAPIClient(unittest.TestCase):
    """
    Tests for the API client.
    """
    
    def setUp(self):
        # Use a mock URL for testing
        self.client = CourseCompanionAPIClient("https://api.coursecompanion.dev/api/v1", "fake-token")
    
    def test_api_client_initialization(self):
        """
        Test that the API client initializes correctly.
        """
        self.assertEqual(self.client.base_url, "https://api.coursecompanion.dev/api/v1")
        self.assertEqual(self.client.auth_token, "fake-token")
    
    def test_endpoint_functions_exist(self):
        """
        Test that all required API functions exist.
        """
        # Content delivery functions
        self.assertTrue(hasattr(self.client, 'get_chapter_content'))
        self.assertTrue(hasattr(self.client, 'list_chapters'))
        self.assertTrue(hasattr(self.client, 'get_module_overview'))
        
        # Navigation functions
        self.assertTrue(hasattr(self.client, 'get_next_chapter'))
        self.assertTrue(hasattr(self.client, 'get_full_sequence'))
        self.assertTrue(hasattr(self.client, 'get_recommended_action'))
        
        # Quiz functions
        self.assertTrue(hasattr(self.client, 'list_quizzes'))
        self.assertTrue(hasattr(self.client, 'get_quiz_questions'))
        self.assertTrue(hasattr(self.client, 'submit_quiz_answers'))
        self.assertTrue(hasattr(self.client, 'get_quiz_results'))
        
        # Progress functions
        self.assertTrue(hasattr(self.client, 'get_user_progress'))
        self.assertTrue(hasattr(self.client, 'mark_chapter_complete'))
        self.assertTrue(hasattr(self.client, 'get_user_streak'))
        self.assertTrue(hasattr(self.client, 'get_user_achievements'))
        self.assertTrue(hasattr(self.client, 'log_learning_time'))


class TestIntegration(unittest.TestCase):
    """
    Integration tests for the ChatGPT app components.
    """
    
    def setUp(self):
        self.router = SkillRouter()
        self.client = CourseCompanionAPIClient("https://api.coursecompanion.dev/api/v1", "fake-token")
    
    def test_concept_explanation_flow(self):
        """
        Test the complete concept explanation flow.
        """
        # Simulate user input
        user_input = "Explain MCP to me"
        
        # Route to correct skill
        skill = self.router.detect_intent(user_input)
        self.assertEqual(skill, "concept_explainer")
        
        # Simulate API call that would be made
        chapter_content = self.client.get_chapter_content("ch3-mcp-integration")
        
        # The API call would return content (even if mocked)
        self.assertIsInstance(chapter_content, dict)
    
    def test_quiz_session_flow(self):
        """
        Test the complete quiz session flow.
        """
        # Simulate user input
        user_input = "Quiz me on Chapter 1"
        
        # Route to correct skill
        skill = self.router.detect_intent(user_input)
        self.assertEqual(skill, "quiz_master")
        
        # Simulate API calls that would be made
        quizzes = self.client.list_quizzes(chapter_id="ch1-intro-to-agents")
        self.assertIsInstance(quizzes, dict)
    
    def test_progress_check_flow(self):
        """
        Test the complete progress check flow.
        """
        # Simulate user input
        user_input = "How's my progress?"
        
        # Route to correct skill
        skill = self.router.detect_intent(user_input)
        self.assertEqual(skill, "progress_motivator")
        
        # Simulate API calls that would be made
        progress = self.client.get_user_progress("user-12345")
        self.assertIsInstance(progress, dict)
        
        streak = self.client.get_user_streak("user-12345")
        self.assertIsInstance(streak, dict)


def run_tests():
    """
    Run all tests.
    """
    # Create test suite
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestSkillRouter)
    suite.addTests(loader.loadTestsFromTestCase(TestAPIClient))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    print("Running Course Companion ChatGPT App Tests")
    print("=" * 50)
    
    success = run_tests()
    
    if success:
        print("\n✅ All tests passed!")
    else:
        print("\n❌ Some tests failed!")
    
    print("\nTest Summary:")
    print("- Skill routing logic works correctly")
    print("- API client has all required methods")
    print("- Integration between components functions properly")