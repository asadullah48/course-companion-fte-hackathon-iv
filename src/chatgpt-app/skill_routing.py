"""
Skill Routing Logic for Course Companion ChatGPT App

Implements the intent detection rules for routing user inputs to the appropriate skill.
This is a conceptual implementation showing how ChatGPT would determine which skill to activate.
"""

import re
from typing import Dict, List, Tuple

class SkillRouter:
    """
    Determines which skill should handle a user's input based on trigger patterns.
    """
    
    def __init__(self):
        self.SKILL_TRIGGERS = {
            "concept_explainer": {
                "keywords": ["explain", "what is", "what are", "how does", "how do", "define", "tell me about", "describe"],
                "patterns": [
                    r"explain\s+.+",
                    r"what\s+(is|are)\s+.+",
                    r"how\s+(does|do)\s+.+\s+work",
                    r"define\s+.+",
                    r"tell\s+me\s+about\s+.+",
                    r"can\s+you\s+explain\s+.+"
                ],
                "priority": 2
            },
            "quiz_master": {
                "keywords": ["quiz", "test", "assess", "practice", "questions", "exam"],
                "patterns": [
                    r"quiz\s+me",
                    r"test\s+my\s+knowledge",
                    r"give\s+me\s+.+\s+questions",
                    r"practice\s+.+",
                    r"assess\s+my\s+.+"
                ],
                "priority": 1
            },
            "socratic_tutor": {
                "keywords": ["help me think", "guide me", "stuck", "don't tell me", "don't give me the answer"],
                "patterns": [
                    r"help\s+me\s+(think|understand)",
                    r"guide\s+me\s+through",
                    r"i('m|\s+am)\s+stuck",
                    r"don't\s+(tell|give)\s+me\s+(the\s+)?answer",
                    r"work\s+through\s+this",
                    r"why\s+does\s+.+\s+work",
                    r"coach\s+me"
                ],
                "priority": 1
            },
            "progress_motivator": {
                "keywords": ["progress", "streak", "achievements", "my stats", "completion"],
                "patterns": [
                    r"(my|show)\s+progress",
                    r"(my|current)\s+streak",
                    r"(my|show)\s+achievements",
                    r"how\s+(am\s+i|'m\s+i)\s+(doing|progressing)",
                    r"how\s+far\s+(have\s+i|am\s+i)",
                    r"what\s+have\s+i\s+(completed|learned|finished)",
                    r"show\s+me\s+my\s+stats",
                    r"how\s+am\s+i\s+doing",
                    r"how\s+far\s+am\s+i"
                ],
                "priority": 1
            }
        }
    
    def detect_intent(self, user_input: str) -> str:
        """
        Detects the most appropriate skill for the user's input.

        Args:
            user_input: The user's message

        Returns:
            The name of the skill that should handle the input
        """
        user_input_lower = user_input.lower().strip()

        # Calculate match scores for each skill
        skill_scores = {}

        for skill_name, triggers in self.SKILL_TRIGGERS.items():
            score = 0

            # Check for pattern matches first (higher weight)
            for pattern in triggers["patterns"]:
                if re.search(pattern, user_input_lower):
                    score += 5  # Patterns are weighted more heavily than keywords

            # Check for keyword matches
            for keyword in triggers["keywords"]:
                if keyword in user_input_lower:
                    score += 2  # Keywords are weighted moderately

            skill_scores[skill_name] = score

        # Find the skill with the highest score
        best_skill = max(skill_scores, key=skill_scores.get)

        # If no skill has a positive score, default to concept_explainer
        if skill_scores[best_skill] <= 0:
            return "concept_explainer"

        return best_skill
    
    def get_available_skills(self) -> List[str]:
        """
        Returns a list of all available skills.
        """
        return list(self.SKILL_TRIGGERS.keys())
    
    def get_skill_description(self, skill_name: str) -> str:
        """
        Returns a description of the specified skill.
        """
        descriptions = {
            "concept_explainer": "Explains AI Agent concepts at the learner's comprehension level",
            "quiz_master": "Conducts engaging, educational quiz sessions with immediate feedback",
            "socratic_tutor": "Guides learners to understanding through strategic questioning",
            "progress_motivator": "Celebrates achievements, tracks progress, and motivates continued learning"
        }
        return descriptions.get(skill_name, "Unknown skill")


# Example usage
if __name__ == "__main__":
    router = SkillRouter()
    
    # Test examples from the specification
    test_inputs = [
        "Explain MCP to me",
        "Quiz me on Chapter 1",
        "Help me understand how agents make decisions. Don't just give me the answer.",
        "How's my progress?",
        "What will I learn in this course?"
    ]
    
    print("Skill Routing Examples:")
    print("-" * 50)
    
    for inp in test_inputs:
        skill = router.detect_intent(inp)
        print(f"Input: '{inp}'")
        print(f"Detected Skill: {skill}")
        print(f"Description: {router.get_skill_description(skill)}")
        print("-" * 50)