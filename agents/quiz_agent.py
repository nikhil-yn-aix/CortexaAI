"""
Quiz generation agent using Gemini 2.5 Pro with chain of thought prompting.
"""

import json
import asyncio
import re
from typing import List, Dict, Any, Optional
from pathlib import Path

try:
    import google.generativeai as genai
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False

from core.config import settings

class QuizAgent:
    """Generate adaptive quizzes using Gemini 2.5 Pro with deep reasoning."""
    
    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY  

        self.model = None
        self.is_initialized = False
    
    async def initialize(self):
        """Initialize Gemini 2.5 Pro model."""
        if self.is_initialized:
            return
            
        if not GENAI_AVAILABLE:
            print("✗ Google Generative AI not available")
            return
            
        if not self.api_key:
            print("✗ Google AI API key not found in config")
            return
            
        try:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-2.5-pro')
            self.is_initialized = True
            print("✓ Gemini 2.5 Pro initialized")
        except Exception as e:
            print(f"✗ Gemini initialization failed: {e}")
    
    async def generate_quiz(
        self, 
        content: str, 
        emotion_context: Optional[str] = None,
        difficulty: str = "intermediate"
    ) -> Dict[str, Any]:
        """Generate quiz from content with emotion adaptation."""
        if not self.is_initialized:
            await self.initialize()
        
        if not self.model:
            return self._mock_quiz(content)
        
        try:
            prompt = self._build_deep_prompt(content, emotion_context, difficulty)
            response = await asyncio.to_thread(
                self.model.generate_content, prompt
            )
            
            quiz_data = self._parse_quiz_response(response.text)
            await self._save_quiz(quiz_data)
            return quiz_data
            
        except Exception as e:
            print(f"✗ Quiz generation failed: {e}")
            return self._mock_quiz(content)
    
    def _build_deep_prompt(self, content: str, emotion_context: str, difficulty: str) -> str:
        """Build deep chain of thought prompt for quiz generation."""
        
        emotion_instructions = {
            "frustrated": "Create simpler questions with more hints and explanations. Focus on fundamental concepts.",
            "confused": "Generate clear, step-by-step questions with detailed explanations. Avoid ambiguity.",
            "happy": "Include challenging questions that build on concepts. Add some advanced applications.",
            "neutral": "Create balanced questions covering core concepts with progressive difficulty."
        }
        
        emotion_guide = emotion_instructions.get(emotion_context, emotion_instructions["neutral"])
        
        return f"""
<thinking>
I need to create a high-quality quiz from the provided content. Let me analyze what I have:

1. Content Analysis:
   - I need to identify the main topics and concepts
   - Find the most important learning objectives
   - Ensure each question targets different aspects
   - Consider the user's emotional state: {emotion_context or 'neutral'}

2. Question Strategy:
   - {emotion_guide}
   - Difficulty level: {difficulty}
   - Create exactly 5 questions covering different topics
   - Each question should test understanding, not just memorization
   - Include clear explanations for each answer

3. Question Types:
   - Multiple choice with 4 options
   - One clearly correct answer
   - Distractors should be plausible but incorrect
   - Questions should be pedagogically sound

Let me identify the key topics from the content and create targeted questions.
</thinking>

<reflect>
Am I creating questions that truly test understanding rather than rote memorization?
Are the questions appropriately difficult for someone who is {emotion_context or 'neutral'}?
Do the questions cover the breadth of the content provided?
Are the answer explanations clear and educational?
</reflect>

You are an expert educational content creator. Analyze the following content and create exactly 5 high-quality quiz questions.

Content to analyze:
{content}

Requirements:
- Create exactly 5 multiple-choice questions
- Each question should cover a different main topic from the content
- Questions should test comprehension and application, not just recall
- Provide 4 answer options (A, B, C, D) with exactly one correct answer
- Include detailed explanations for why the correct answer is right
- {emotion_guide}

Output the quiz in valid JSON format within <output></output> tags:

<output>
{{
  "quiz_metadata": {{
    "title": "Generated Quiz",
    "difficulty": "{difficulty}",
    "emotion_context": "{emotion_context or 'neutral'}",
    "total_questions": 5,
    "estimated_time_minutes": 10
  }},
  "questions": [
    {{
      "id": 1,
      "question": "Clear, specific question text",
      "options": {{
        "A": "First option",
        "B": "Second option", 
        "C": "Third option",
        "D": "Fourth option"
      }},
      "correct_answer": "A",
      "explanation": "Detailed explanation of why this answer is correct and why others are wrong",
      "topic": "Main topic this question covers",
      "difficulty": "easy|medium|hard"
    }}
  ]
}}
</output>

Generate the quiz now, ensuring each question targets a different key concept from the content.
"""
    
    def _parse_quiz_response(self, response_text: str) -> Dict[str, Any]:
        """Parse quiz JSON from model response."""
        try:
            # Extract JSON from output tags
            pattern = r"<output>(.*?)</output>"
            match = re.search(pattern, response_text, re.DOTALL)
            
            if match:
                json_str = match.group(1).strip()
                quiz_data = json.loads(json_str)
                
                # Validate structure
                if self._validate_quiz_structure(quiz_data):
                    return quiz_data
                    
        except json.JSONDecodeError as e:
            print(f"✗ JSON parsing failed: {e}")
        except Exception as e:
            print(f"✗ Response parsing failed: {e}")
        
        # Fallback to mock quiz
        return self._mock_quiz("parsing failed")
    
    def _validate_quiz_structure(self, quiz_data: Dict[str, Any]) -> bool:
        """Validate quiz JSON structure."""
        required_keys = ["quiz_metadata", "questions"]
        if not all(key in quiz_data for key in required_keys):
            return False
            
        questions = quiz_data.get("questions", [])
        if len(questions) != 5:
            return False
            
        for q in questions:
            required_q_keys = ["id", "question", "options", "correct_answer", "explanation"]
            if not all(key in q for key in required_q_keys):
                return False
                
            options = q.get("options", {})
            if not all(opt in options for opt in ["A", "B", "C", "D"]):
                return False
                
        return True
    
    async def _save_quiz(self, quiz_data: Dict[str, Any]) -> None:
        """Save quiz to outputs/quiz.json."""
        try:
            output_dir = Path("outputs")
            output_dir.mkdir(exist_ok=True)
            
            quiz_file = output_dir / "quiz.json"
            with open(quiz_file, "w", encoding="utf-8") as f:
                json.dump(quiz_data, f, indent=2, ensure_ascii=False)
                
            print(f"✓ Quiz saved to {quiz_file}")
            
        except Exception as e:
            print(f"✗ Failed to save quiz: {e}")
    
    def _mock_quiz(self, content: str) -> Dict[str, Any]:
        """Generate mock quiz when API unavailable."""
        return {
            "quiz_metadata": {
                "title": "Mock Quiz - Neural Networks & Transformers",
                "difficulty": "intermediate",
                "emotion_context": "neutral",
                "total_questions": 5,
                "estimated_time_minutes": 10
            },
            "questions": [
                {
                    "id": 1,
                    "question": "What is the primary function of activation functions in neural networks?",
                    "options": {
                        "A": "To store weights and biases",
                        "B": "To introduce non-linearity for complex relationships",
                        "C": "To reduce computational cost",
                        "D": "To prevent data leakage"
                    },
                    "correct_answer": "B",
                    "explanation": "Activation functions like ReLU and sigmoid introduce non-linearity, allowing networks to model complex relationships beyond linear transformations.",
                    "topic": "Neural Network Fundamentals",
                    "difficulty": "medium"
                },
                {
                    "id": 2,
                    "question": "What key mechanism allows transformers to process sequences in parallel?",
                    "options": {
                        "A": "Recurrent connections",
                        "B": "Convolutional layers", 
                        "C": "Self-attention mechanism",
                        "D": "Pooling operations"
                    },
                    "correct_answer": "C",
                    "explanation": "Self-attention allows transformers to weigh relationships between all positions simultaneously, enabling parallel processing unlike sequential RNNs.",
                    "topic": "Transformer Architecture",
                    "difficulty": "medium"
                }
            ]
        }

# Global service instance
quiz_agent = QuizAgent()

async def test_quiz_agent():
    """Test quiz generation with neural networks content."""
    print("Testing Quiz Agent with Gemini 2.5 Pro")
    print("=" * 50)
    
    test_content = """
Neural networks are computing systems inspired by the biological neural networks that constitute animal brains. They consist of layers of interconnected nodes, "neurons", which process input data and pass signals to subsequent layers. The key components include an input layer, one or more hidden layers, and an output layer. Neural networks learn to perform tasks by adjusting the weights of the connections based on the difference between the predicted and actual outcomes.

Transformers are a type of neural network architecture designed to handle sequential data, primarily used in natural language processing tasks. Unlike recurrent neural networks, transformers use self-attention mechanisms to weigh the influence of different parts of the input data, allowing for parallelization and improved context understanding. They have revolutionized the field by enabling better handling of long-range dependencies in text.

The training of neural networks involves feeding data forward through the network and then using backpropagation to adjust weights in the direction that minimizes error. This process leverages gradient descent optimization algorithms. Regularization techniques like dropout and batch normalization are applied to prevent overfitting and improve generalization.

Activation functions such as sigmoid, tanh, and ReLU introduce non-linearity, allowing the network to model complex relationships. Each neuron applies an activation function to its input signal, determining the final output it passes forward.

Convolutional neural networks (CNNs) are specialized for processing grid-like data, such as images. They use convolutional layers to extract local features and pooling layers to reduce dimensionality, thus improving computational efficiency.

Recurrent neural networks (RNNs) are built for sequence data, utilizing loops to maintain information across time steps. Variants include long short-term memory (LSTM) and gated recurrent units (GRU), which handle vanishing gradient problems.

The transformer architecture introduced multi-head self-attention, enabling the model to focus on different parts of the input simultaneously. This allows transformers to capture various types of relationships within the data more effectively.

Transfer learning has become a powerful approach, where a neural network pretrained on one large dataset is fine-tuned on a smaller, task-specific dataset. This dramatically reduces training time and improves performance.

Optimization strategies in training include learning rate schedules, early stopping, and the use of advanced optimizers like Adam and RMSprop.

Understanding the architecture, training mechanisms, and optimization techniques of neural networks and transformers is crucial for designing effective AI models.
"""
    
    test_cases = [
        ("neutral", "intermediate"),
        ("frustrated", "beginner"),
        ("happy", "advanced"),
        ("confused", "beginner")
    ]
    
    for emotion, difficulty in test_cases:
        print(f"\nTest: {emotion} learner, {difficulty} difficulty")
        print("-" * 30)
        
        try:
            quiz = await quiz_agent.generate_quiz(
                content=test_content,
                emotion_context=emotion,
                difficulty=difficulty
            )
            
            metadata = quiz.get("quiz_metadata", {})
            questions = quiz.get("questions", [])
            
            print(f"✓ Generated quiz: {metadata.get('title', 'Unknown')}")
            print(f"  Questions: {len(questions)}")
            print(f"  Difficulty: {metadata.get('difficulty', 'Unknown')}")
            print(f"  Emotion context: {metadata.get('emotion_context', 'Unknown')}")
            
            # Show first question as sample
            if questions:
                q1 = questions[0]
                print(f"  Sample Q1: {q1.get('question', '')[:60]}...")
                
        except Exception as e:
            print(f"✗ Test failed: {e}")
    
    print("\n" + "=" * 50)
    print("✓ Quiz agent testing complete")
    print("Check outputs/quiz.json for the latest generated quiz")

if __name__ == "__main__":
    asyncio.run(test_quiz_agent())
