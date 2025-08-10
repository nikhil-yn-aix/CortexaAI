"""
Podcast script generation agent using Gemini 2.5 Pro with emotion adaptation.
"""

import json
import asyncio
import re
from typing import Dict, Any, Optional, List
from pathlib import Path

try:
    import google.generativeai as genai
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False

from core.config import settings

class PodcastAgent:
    """Generate emotion-adaptive podcast scripts using Gemini 2.5 Pro."""
    
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
            print("✗ Gemini API key not found in config")
            return
            
        try:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-2.5-pro')
            self.is_initialized = True
            print("✓ Gemini 2.5 Pro initialized for podcast generation")
        except Exception as e:
            print(f"✗ Gemini initialization failed: {e}")
    
    async def generate_podcast_script(
        self,
        content: str,
        emotion_context: Optional[str] = None,
        duration_minutes: int = 8
    ) -> Dict[str, Any]:
        """Generate emotion-adaptive podcast script from content."""
        if not self.is_initialized:
            await self.initialize()
        
        if not self.model:
            return self._mock_podcast(content, emotion_context)
        
        try:
            prompt = self._build_podcast_prompt(content, emotion_context, duration_minutes)
            response = await asyncio.to_thread(
                self.model.generate_content, prompt
            )
            
            podcast_data = self._parse_podcast_response(response.text)
            await self._save_podcast(podcast_data)
            return podcast_data
            
        except Exception as e:
            print(f"✗ Podcast generation failed: {e}")
            return self._mock_podcast(content, emotion_context)
    
    def _build_podcast_prompt(
        self, 
        content: str, 
        emotion_context: str, 
        duration_minutes: int
    ) -> str:
        """Build deep chain of thought prompt for podcast script generation."""
        
        emotion_instructions = {
            "frustrated": {
                "tone": "encouraging and reassuring",
                "pace": "slower with more pauses",
                "language": "simple, supportive language with frequent reassurance",
                "structure": "smaller chunks with lots of analogies and real-world examples"
            },
            "confused": {
                "tone": "clear and methodical",
                "pace": "deliberate with emphasis on key points",
                "language": "step-by-step explanations with crystal clear transitions",
                "structure": "logical progression with frequent summarization"
            },
            "happy": {
                "tone": "energetic and engaging",
                "pace": "dynamic with varied rhythm",
                "language": "enthusiastic with challenging concepts and advanced insights",
                "structure": "fast-paced with deeper dives and exciting connections"
            },
            "neutral": {
                "tone": "friendly and professional",
                "pace": "steady and conversational",
                "language": "balanced mix of explanation and engagement",
                "structure": "well-organized with natural flow"
            }
        }
        
        emotion_guide = emotion_instructions.get(emotion_context, emotion_instructions["neutral"])
        
        return f"""
<thinking>
I need to create an engaging educational podcast script from the provided content. Let me analyze what I have:

1. Content Analysis:
   - I need to identify the key concepts and learning objectives
   - Break down complex topics into digestible segments
   - Create natural conversation flow like NotebookLM style
   - Consider the listener's emotional state: {emotion_context or 'neutral'}

2. Podcast Strategy:
   - Duration target: {duration_minutes} minutes
   - Tone: {emotion_guide['tone']}
   - Pace: {emotion_guide['pace']}
   - Language style: {emotion_guide['language']}
   - Content structure: {emotion_guide['structure']}

3. Educational Effectiveness:
   - Use conversational language, not lecture style
   - Include analogies and real-world examples
   - Create natural transitions between concepts
   - Build engagement through questions and insights
   - Make complex topics accessible and interesting

4. Podcast Elements:
   - Hook opening to grab attention immediately
   - Clear topic introduction with context
   - Main content in engaging segments
   - Natural transitions and connective tissue
   - Summary and actionable takeaways
   - Strong closing with next steps

Let me craft a script that feels like a natural conversation between knowledgeable friends.
</thinking>

<reflect>
Am I creating content that sounds natural when spoken aloud?
Does the script adapt appropriately to the listener's emotional state?
Are the concepts broken down in a logical, engaging sequence?
Would this keep a listener interested for the full duration?
Are there enough analogies and examples to make complex topics accessible?
Does the pacing and tone match what someone who is {emotion_context or 'neutral'} would need?
</reflect>

You are an expert educational content creator specializing in engaging podcast scripts. Create a compelling {duration_minutes}-minute podcast script from the provided content.

Content to transform into podcast:
{content}

Requirements:
- Create an engaging, conversational script that sounds natural when spoken
- Tone: {emotion_guide['tone']}
- Pace: {emotion_guide['pace']}
- Language: {emotion_guide['language']}
- Structure: {emotion_guide['structure']}
- Include delivery notes for natural speech patterns
- Use analogies, examples, and engaging storytelling
- Create smooth transitions between concepts
- Target duration: {duration_minutes} minutes

Output the podcast script in valid JSON format within <output></output> tags:

<output>
{{
  "podcast_metadata": {{
    "title": "Episode Title",
    "duration_minutes": {duration_minutes},
    "emotion_context": "{emotion_context or 'neutral'}",
    "target_audience": "learners interested in the topic",
    "learning_objectives": ["objective 1", "objective 2", "objective 3"],
    "key_concepts": ["concept1", "concept2", "concept3"]
  }},
  "script_segments": [
    {{
      "segment_type": "hook",
      "estimated_duration_seconds": 30,
      "content": "Attention-grabbing opening that hooks the listener",
      "delivery_notes": "Energetic, intriguing tone to draw listener in",
      "speaker_notes": "Natural pause after hook for impact"
    }},
    {{
      "segment_type": "intro",
      "estimated_duration_seconds": 45,
      "content": "Welcome and topic introduction with context",
      "delivery_notes": "Warm, welcoming tone establishing connection",
      "speaker_notes": "Set expectations for what listener will learn"
    }},
    {{
      "segment_type": "main_content",
      "estimated_duration_seconds": 120,
      "content": "First major concept explanation with examples",
      "delivery_notes": "Clear, engaging explanation with natural enthusiasm",
      "speaker_notes": "Include analogy here to make concept relatable"
    }},
    {{
      "segment_type": "transition",
      "estimated_duration_seconds": 15,
      "content": "Smooth bridge to next topic",
      "delivery_notes": "Natural conversational flow",
      "speaker_notes": "Connect previous concept to upcoming one"
    }},
    {{
      "segment_type": "main_content",
      "estimated_duration_seconds": 120,
      "content": "Second major concept with practical applications",
      "delivery_notes": "Enthusiastic tone when discussing applications",
      "speaker_notes": "Use real-world examples listener can relate to"
    }},
    {{
      "segment_type": "insight",
      "estimated_duration_seconds": 60,
      "content": "Key insight or connection between concepts",
      "delivery_notes": "Thoughtful, revelatory tone",
      "speaker_notes": "Pause for impact before delivering insight"
    }},
    {{
      "segment_type": "wrap_up",
      "estimated_duration_seconds": 45,
      "content": "Summary of key points and actionable takeaways",
      "delivery_notes": "Confident, encouraging tone",
      "speaker_notes": "Emphasize practical value for listener"
    }},
    {{
      "segment_type": "outro",
      "estimated_duration_seconds": 25,
      "content": "Closing with next steps and engagement call",
      "delivery_notes": "Warm, inviting tone for continued learning",
      "speaker_notes": "End on encouraging, forward-looking note"
    }}
  ],
  "emotion_adaptations": {{
    "tone_adjustments": "Specific adaptations made for {emotion_context or 'neutral'} listener",
    "pacing_notes": "How pacing was adjusted for emotional state",
    "language_choices": "Why certain words/phrases were chosen"
  }}
}}
</output>

Generate an engaging, natural podcast script that educates while entertaining, perfectly adapted for a {emotion_context or 'neutral'} learner.
"""
    
    def _parse_podcast_response(self, response_text: str) -> Dict[str, Any]:
        """Parse podcast JSON from model response."""
        try:
            pattern = r"<output>(.*?)</output>"
            match = re.search(pattern, response_text, re.DOTALL)
            
            if match:
                json_str = match.group(1).strip()
                podcast_data = json.loads(json_str)
                
                if self._validate_podcast_structure(podcast_data):
                    return podcast_data
                    
        except json.JSONDecodeError as e:
            print(f"✗ JSON parsing failed: {e}")
        except Exception as e:
            print(f"✗ Response parsing failed: {e}")
        
        return self._mock_podcast("parsing failed")
    
    def _validate_podcast_structure(self, podcast_data: Dict[str, Any]) -> bool:
        """Validate podcast JSON structure."""
        required_keys = ["podcast_metadata", "script_segments"]
        if not all(key in podcast_data for key in required_keys):
            return False
            
        metadata = podcast_data.get("podcast_metadata", {})
        required_meta = ["title", "duration_minutes", "emotion_context"]
        if not all(key in metadata for key in required_meta):
            return False
            
        segments = podcast_data.get("script_segments", [])
        if not segments or len(segments) < 3:
            return False
            
        for segment in segments:
            required_seg_keys = ["segment_type", "content", "delivery_notes"]
            if not all(key in segment for key in required_seg_keys):
                return False
                
        return True
    
    async def _save_podcast(self, podcast_data: Dict[str, Any]) -> None:
        """Save podcast script to outputs/podcast.json."""
        try:
            output_dir = Path("outputs")
            output_dir.mkdir(exist_ok=True)
            
            podcast_file = output_dir / "podcast.json"
            with open(podcast_file, "w", encoding="utf-8") as f:
                json.dump(podcast_data, f, indent=2, ensure_ascii=False)
                
            print(f"✓ Podcast script saved to {podcast_file}")
            
        except Exception as e:
            print(f"✗ Failed to save podcast: {e}")
    
    def _mock_podcast(self, content: str, emotion_context: str = "neutral") -> Dict[str, Any]:
        """Generate mock podcast when API unavailable."""
        return {
            "podcast_metadata": {
                "title": "The Neural Revolution: Understanding AI's Building Blocks",
                "duration_minutes": 8,
                "emotion_context": emotion_context or "neutral",
                "target_audience": "curious learners exploring AI concepts",
                "learning_objectives": [
                    "Understand what neural networks are and how they work",
                    "Grasp the revolutionary impact of transformer architecture",
                    "Connect AI concepts to real-world applications"
                ],
                "key_concepts": ["neural networks", "transformers", "deep learning", "AI applications"]
            },
            "script_segments": [
                {
                    "segment_type": "hook",
                    "estimated_duration_seconds": 30,
                    "content": "Imagine trying to teach a computer to recognize your grandmother's face in a photo. Sounds impossible, right? Well, that's exactly what neural networks do every day, and today we're diving into the fascinating world of AI that's changing everything around us.",
                    "delivery_notes": "Excited, intriguing tone with a slight pause after 'impossible, right?'",
                    "speaker_notes": "Start with energy and curiosity to draw listeners in immediately"
                },
                {
                    "segment_type": "intro",
                    "estimated_duration_seconds": 45,
                    "content": "Hey there, I'm your host, and welcome to today's deep dive into neural networks and transformers. Whether you're curious about AI, confused by all the tech buzz, or just want to understand what's happening behind the scenes of ChatGPT and other AI tools, you're in the right place. By the end of our chat, you'll have a solid grasp of these game-changing technologies.",
                    "delivery_notes": "Warm, welcoming tone that makes listeners feel included and comfortable",
                    "speaker_notes": "Establish personal connection and clear learning expectations"
                },
                {
                    "segment_type": "main_content",
                    "estimated_duration_seconds": 120,
                    "content": "So let's start with neural networks. Think of your brain for a moment - it's made up of billions of neurons all connected together, constantly passing signals back and forth. Artificial neural networks work similarly, but instead of biological neurons, we have mathematical functions. Here's the cool part: just like your brain learns by strengthening connections between neurons when you practice piano or learn a new language, neural networks learn by adjusting the strength of connections between their artificial neurons. When we show a network thousands of cat photos and tell it 'this is a cat,' it gradually adjusts its internal connections until it can spot cats in new photos it's never seen before. It's like teaching a very patient student who never gets tired of practice.",
                    "delivery_notes": "Enthusiastic but clear, emphasizing analogies with slight pauses for comprehension",
                    "speaker_notes": "The brain-to-network analogy is key here - make it feel relatable and understandable"
                }
            ],
            "emotion_adaptations": {
                "tone_adjustments": f"Adapted for {emotion_context} learner with appropriate pacing and encouragement",
                "pacing_notes": "Balanced conversational pace with strategic pauses for concept absorption",
                "language_choices": "Used accessible analogies and avoided technical jargon"
            }
        }

# Global service instance
podcast_agent = PodcastAgent()

async def test_podcast_agent():
    """Test podcast generation with neural networks content."""
    print("Testing Podcast Agent with Gemini 2.5 Pro")
    print("=" * 55)
    
    test_content = """
Neural networks are computing systems inspired by the biological neural networks that constitute animal brains. They consist of layers of interconnected nodes, "neurons", which process input data and pass signals to subsequent layers. The key components include an input layer, one or more hidden layers, and an output layer. Neural networks learn to perform tasks by adjusting the weights of the connections based on the difference between the predicted and actual outcomes.

Transformers are a type of neural network architecture designed to handle sequential data, primarily used in natural language processing tasks. Unlike recurrent neural networks, transformers use self-attention mechanisms to weigh the influence of different parts of the input data, allowing for parallelization and improved context understanding. They have revolutionized the field by enabling better handling of long-range dependencies in text.

The training of neural networks involves feeding data forward through the network and then using backpropagation to adjust weights in the direction that minimizes error. This process leverages gradient descent optimization algorithms. Regularization techniques like dropout and batch normalization are applied to prevent overfitting and improve generalization.

Activation functions such as sigmoid, tanh, and ReLU introduce non-linearity, allowing the network to model complex relationships. Each neuron applies an activation function to its input signal, determining the final output it passes forward.

Convolutional neural networks (CNNs) are specialized for processing grid-like data, such as images. They use convolutional layers to extract local features and pooling layers to reduce dimensionality, thus improving computational efficiency.

Recurrent neural networks (RNNs) are built for sequence data, utilizing loops to maintain information across time steps. Variants include long short-term memory (LSTM) and gated recurrent units (GRU), which handle vanishing gradient problems.

The transformer architecture introduced multi-head self-attention, enabling the model to focus on different parts of the input simultaneously. This allows transformers to capture various types of relationships within the data more effectively.

Transfer learning has become a powerful approach, where a neural network pretrained on one large dataset is fine-tuned on a smaller, task-specific dataset. This dramatically reduces training time and improves performance.

Optimization strategies in training include learning rate schedules, early stopping, and the use of advanced optimizers like Adam and RMSprop. Modern deep learning frameworks like PyTorch and TensorFlow have made implementing these techniques accessible to researchers and practitioners.

Understanding the architecture, training mechanisms, and optimization techniques of neural networks and transformers is crucial for designing effective AI models that can tackle real-world problems across various domains.
"""
    
    test_cases = [
        ("neutral", 8),
        ("frustrated", 6),
        ("happy", 10),
        ("confused", 7)
    ]
    
    for emotion, duration in test_cases:
        print(f"\nTest: {emotion} learner, {duration}-minute podcast")
        print("-" * 40)
        
        try:
            podcast = await podcast_agent.generate_podcast_script(
                content=test_content,
                emotion_context=emotion,
                duration_minutes=duration
            )
            
            metadata = podcast.get("podcast_metadata", {})
            segments = podcast.get("script_segments", [])
            
            print(f"✓ Generated podcast: {metadata.get('title', 'Unknown')}")
            print(f"  Duration: {metadata.get('duration_minutes', 'Unknown')} minutes")
            print(f"  Emotion context: {metadata.get('emotion_context', 'Unknown')}")
            print(f"  Segments: {len(segments)}")
            print(f"  Learning objectives: {len(metadata.get('learning_objectives', []))}")
            
            # Show sample segment
            if segments:
                hook = segments[0]
                content_preview = hook.get('content', '')[:80] + "..." if len(hook.get('content', '')) > 80 else hook.get('content', '')
                print(f"  Hook preview: '{content_preview}'")
                
        except Exception as e:
            print(f"✗ Test failed: {e}")
    
    print("\n" + "=" * 55)
    print("✓ Podcast agent testing complete")
    print("Check outputs/podcast.json for the latest generated script")

if __name__ == "__main__":
    asyncio.run(test_podcast_agent())
