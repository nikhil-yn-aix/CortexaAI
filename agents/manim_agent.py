"""
Ultimate Podcast & Manim Generator
Complete bulletproof system with perfect prompting and clean parsing
"""

import os
import json
import asyncio
import subprocess
import logging
import re
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict

try:
    import google.generativeai as genai
except Exception:
    genai = None

try:
    from core.config import settings
except Exception:
    class _DummySettings:
        GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
    settings = _DummySettings()

logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')
logger = logging.getLogger(__name__)

@dataclass
class PodcastScript:
    segment_id: int
    title: str
    content: str
    duration_minutes: float
    pacing: str
    interaction_question: str
    created_at: str

@dataclass
class Session:
    session_id: str
    topic: str
    scripts: Dict[int, PodcastScript]
    animations: Dict[int, str]
    created_at: str

MANIM_TOOLKIT = """
MANIM COMMUNITY v0.19.0 - APPROVED OBJECTS ONLY

BASIC STRUCTURE:
from manim import *
class EducationalScene(Scene):
    def construct(self):
        pass

ALLOWED OBJECTS:
- Text(content, font_size=28, color=WHITE)
- Circle(radius=1.0, color=BLUE, fill_opacity=0.6)
- Rectangle(width=3, height=2, color=RED, fill_opacity=0.4)
- Square(side_length=2, color=GREEN, fill_opacity=0.5)
- Line(start=LEFT, end=RIGHT, color=WHITE, stroke_width=2)
- Arrow(start=LEFT, end=RIGHT, color=YELLOW, buff=0.1)
- VGroup(*objects)

POSITIONING:
- obj.move_to(ORIGIN)
- obj.to_edge(UP/DOWN/LEFT/RIGHT)
- obj.shift(UP*2 or DOWN*1.5 or LEFT*3 or RIGHT*2)
- obj.next_to(other_obj, UP/DOWN/LEFT/RIGHT, buff=0.8)
- obj.scale(0.8)
- obj.arrange(DOWN/UP/LEFT/RIGHT, buff=0.5)

ANIMATIONS:
- Write(text_obj, run_time=2)
- Create(shape_obj, run_time=1.5)
- FadeIn(obj, run_time=1)
- FadeOut(obj, run_time=1)
- Transform(obj1, obj2, run_time=2)

COLORS:
WHITE, BLACK, RED, BLUE, GREEN, YELLOW, PURPLE, PINK, ORANGE, GRAY
RED_A, RED_B, RED_C, BLUE_A, BLUE_B, BLUE_C, GREEN_A, GREEN_B, GREEN_C

DIRECTIONS:
UP, DOWN, LEFT, RIGHT, ORIGIN, UL, UR, DL, DR

TIMING:
- self.play(animation, run_time=2)
- self.wait(1)
- self.add(obj)
- self.remove(obj)
"""

def extract_tagged_content(text: str, tag: str) -> str:
    """Extract content between XML tags with multiple fallback strategies."""
    start_tag = f"<{tag}>"
    end_tag = f"</{tag}>"
    
    start_idx = text.find(start_tag)
    end_idx = text.find(end_tag)
    
    if start_idx != -1 and end_idx != -1:
        content = text[start_idx + len(start_tag):end_idx].strip()
        return content
    
    return ""

def parse_json_safely(text: str) -> Any:
    """Parse JSON with comprehensive fallback methods."""
    text = text.strip()
    
    try:
        return json.loads(text)
    except:
        pass
    
    json_patterns = [
        r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}',
        r'\[[^\[\]]*(?:\[[^\[\]]*\][^\[\]]*)*\]'
    ]
    
    for pattern in json_patterns:
        matches = re.findall(pattern, text, re.DOTALL)
        for match in matches:
            try:
                return json.loads(match)
            except:
                continue
    
    raise ValueError("Cannot parse JSON from response")

def clean_python_code(text: str) -> str:
    """Ultimate code cleaning with bulletproof extraction."""
    if not text or not isinstance(text, str):
        return ""
    
    cleaned = text
    
    markdown_patterns = [
        r'```python\s*\n?',
        r'```\s*\n?',
        r'^```.*$'
    ]
    
    for pattern in markdown_patterns:
        cleaned = re.sub(pattern, '', cleaned, flags=re.MULTILINE)
    
    if 'from manim import *' in cleaned and 'class EducationalScene' in cleaned:
        import_start = cleaned.find('from manim import *')
        return cleaned[import_start:].strip()
    
    class_match = re.search(r'(from manim import \*.*?class EducationalScene.*?)(?=\n\S|\Z)', cleaned, re.DOTALL)
    if class_match:
        return class_match.group(1).strip()
    
    lines = cleaned.split('\n')
    clean_lines = []
    include_line = False
    
    for line in lines:
        if line.strip().startswith('```') or (line.strip().startswith('#') and len(line.strip()) < 50):
            continue
        if 'from manim import' in line or 'class EducationalScene' in line:
            include_line = True
        if include_line:
            clean_lines.append(line)
    
    if clean_lines:
        return '\n'.join(clean_lines).strip()
    
    return cleaned.strip()

class PodcastGenerator:
    def __init__(self):
        if genai is not None:
            try:
                genai.configure(api_key=settings.GEMINI_API_KEY)
                self.model = genai.GenerativeModel('gemini-2.5-pro')
            except Exception:
                self.model = None
        else:
            self.model = None

    async def generate_complete_session(self, input_data: dict) -> dict:
        """Generate complete session with 4 scripts and animations."""
        session_id = input_data["session_id"]
        topic = input_data["topic"]
        rag_content = input_data["rag_content"]

        logger.info(f"Generating complete session: {session_id}")

        chunks = await self._generate_content_chunks(rag_content, topic)
        
        if len(chunks) != 4:
            raise RuntimeError(f"Expected 4 chunks, got {len(chunks)}")

        scripts = {}
        for i, chunk in enumerate(chunks, 1):
            script = await self._generate_podcast_script(chunk, i, topic)
            scripts[i] = script

        animations = {}
        for i, chunk in enumerate(chunks, 1):
            mp4_path = await self._generate_animation(chunk, scripts[i], session_id, i)
            if mp4_path:
                animations[i] = mp4_path

        session = Session(
            session_id=session_id,
            topic=topic,
            scripts=scripts,
            animations=animations,
            created_at=datetime.now().isoformat()
        )

        self._save_session(session)

        return {
            "session_id": session_id,
            "status": "complete",
            "scripts": {i: asdict(script) for i, script in scripts.items()},
            "animations": animations,
            "total_segments": 4
        }

    async def update_remaining_scripts(self, input_data: dict) -> dict:
        """Update remaining scripts based on emotion context."""
        session_id = input_data["session_id"]
        completed_segments = input_data.get("completed_segments", [])
        emotion_context = input_data.get("emotion_context", "neutral")

        logger.info(f"Updating scripts for session: {session_id}")

        session = self._load_session(session_id)

        pacing_map = {
            "confused": "slow", "frustrated": "slow",
            "excited": "fast", "engaged": "fast"
        }
        target_pacing = pacing_map.get(emotion_context, "normal")

        updated_scripts = {}
        for segment_id in range(len(completed_segments) + 1, 5):
            if segment_id in session.scripts:
                original_script = session.scripts[segment_id]
                updated_script = await self._adjust_script_pacing(original_script, target_pacing)
                session.scripts[segment_id] = updated_script
                updated_scripts[segment_id] = asdict(updated_script)

        self._save_session(session)

        return {
            "session_id": session_id,
            "status": "updated",
            "updated_scripts": updated_scripts,
            "pacing_applied": target_pacing
        }

    async def _generate_content_chunks(self, rag_content: str, topic: str) -> List[str]:
        """Generate exactly 4 logical content segments."""
        prompt = f"""
TASK: Transform educational content into exactly 4 animation-ready segments.

TOPIC: {topic}
CONTENT: {rag_content}

REQUIREMENTS:
- Each segment must focus on ONE main concept
- Segments should build logically (intro → core concepts → applications)
- Content must be visual and animation-friendly
- Each segment should support 45-second explanation

SEGMENT GUIDELINES:
Segment 1: Introduction and basic definition
Segment 2: Core mechanism or how it works
Segment 3: Key features or components
Segment 4: Applications or real-world impact

OUTPUT FORMAT (MANDATORY):
<CONTENT_SEGMENTS>
["Segment 1: Clear introductory content here", "Segment 2: Core mechanism explanation", "Segment 3: Key features breakdown", "Segment 4: Applications and impact"]
</CONTENT_SEGMENTS>

Return ONLY the JSON array within tags. No explanations. No other text.
"""

        if self.model is None:
            raise RuntimeError("AI model not configured")

        response = await self.model.generate_content_async(prompt)
        text = str(response.text if hasattr(response, 'text') else response)
        
        segments_text = extract_tagged_content(text, "CONTENT_SEGMENTS")
        if not segments_text:
            raise RuntimeError("No content segments found in AI response")
            
        segments = parse_json_safely(segments_text)
        
        if not isinstance(segments, list) or len(segments) != 4:
            raise RuntimeError(f"Expected 4 segments, got {len(segments) if isinstance(segments, list) else 'invalid'}")

        return segments

    async def _generate_podcast_script(self, chunk_content: str, segment_id: int, topic: str) -> PodcastScript:
        """Generate engaging podcast script for segment."""
        prompt = f"""
TASK: Create professional 45-second podcast script for educational segment.

TOPIC: {topic}
SEGMENT: {segment_id}/4
CONTENT: {chunk_content}

SCRIPT REQUIREMENTS:
- Conversational and engaging tone suitable for audio
- Exactly 45 seconds when spoken at normal pace
- Include 3-4 key learning points from content
- End with thought-provoking question for listener engagement
- Natural flow with smooth transitions
- If segment > 1, include brief connection to previous segment

QUALITY STANDARDS:
- Use active voice and clear language
- Include specific examples where relevant
- Build curiosity and maintain engagement
- Professional but accessible tone

OUTPUT FORMAT (MANDATORY):
<PODCAST_SCRIPT>
{{
    "title": "Clear, descriptive segment title",
    "content": "Complete 45-second script with natural flow and engagement...",
    "interaction_question": "Thought-provoking question that encourages reflection"
}}
</PODCAST_SCRIPT>

Return ONLY the JSON within tags. No explanations outside tags.
"""

        if self.model is None:
            raise RuntimeError("AI model not configured")

        response = await self.model.generate_content_async(prompt)
        text = str(response.text if hasattr(response, 'text') else response)
        
        script_text = extract_tagged_content(text, "PODCAST_SCRIPT")
        if not script_text:
            raise RuntimeError("No podcast script found in AI response")
            
        script_data = parse_json_safely(script_text)

        required_keys = ["title", "content", "interaction_question"]
        for key in required_keys:
            if key not in script_data:
                raise RuntimeError(f"Missing required script key: {key}")

        return PodcastScript(
            segment_id=segment_id,
            title=script_data["title"],
            content=script_data["content"],
            duration_minutes=0.75,
            pacing="normal",
            interaction_question=script_data["interaction_question"],
            created_at=datetime.now().isoformat()
        )

    async def _adjust_script_pacing(self, original_script: PodcastScript, target_pacing: str) -> PodcastScript:
        """Adjust script pacing while maintaining educational value."""
        prompt = f"""
TASK: Adjust podcast script pacing while preserving content and duration.

ORIGINAL SCRIPT: {original_script.content}
CURRENT PACING: {original_script.pacing}
TARGET PACING: {target_pacing}

PACING ADJUSTMENTS:
- slow: Add explanations, use simpler language, indicate natural pauses
- fast: More concise phrasing, higher energy, remove unnecessary words
- normal: Balanced pace with clear explanations

REQUIREMENTS:
- Maintain same learning objectives and key points
- Keep 45-second total duration
- Preserve educational value and engagement
- Ensure natural flow for audio delivery

OUTPUT FORMAT (MANDATORY):
<ADJUSTED_SCRIPT>
Adjusted script content maintaining the same educational value with new pacing...
</ADJUSTED_SCRIPT>

Return ONLY the adjusted script within tags. No explanations outside tags.
"""

        if self.model is None:
            raise RuntimeError("AI model not configured")

        response = await self.model.generate_content_async(prompt)
        text = str(response.text if hasattr(response, 'text') else response)
        
        adjusted_content = extract_tagged_content(text, "ADJUSTED_SCRIPT")
        if not adjusted_content:
            raise RuntimeError("No adjusted script found in AI response")

        return PodcastScript(
            segment_id=original_script.segment_id,
            title=original_script.title,
            content=adjusted_content,
            duration_minutes=0.75,
            pacing=target_pacing,
            interaction_question=original_script.interaction_question,
            created_at=datetime.now().isoformat()
        )

    async def _generate_animation(self, chunk_content: str, script: PodcastScript, session_id: str, segment_id: int) -> Optional[str]:
        """Generate complete animation with proper file management."""
        animation_code = await self._create_manim_animation(chunk_content, script)

        session_dir = f"sessions/{session_id}"
        os.makedirs(session_dir, exist_ok=True)

        manim_file = f"{session_dir}/segment_{segment_id}.py"
        try:
            with open(manim_file, 'w', encoding='utf-8') as f:
                f.write(animation_code)
            logger.info(f"Animation code saved: {manim_file}")
        except Exception as e:
            logger.error(f"Failed to save animation code: {e}")
            return None

        mp4_path = f"{session_dir}/segment_{segment_id}.mp4"
        success = await self._render_manim_animation(manim_file, mp4_path)

        if success:
            logger.info(f"Animation rendered successfully: {mp4_path} \u2705")
            return mp4_path
        else:
            logger.error(f"Animation rendering failed \u274c")
            return None

    async def _create_manim_animation(self, chunk_content: str, script: PodcastScript) -> str:
        """Create professional Manim animation with comprehensive planning."""
        prompt = f"""
TASK: Create professional educational animation using systematic planning and clean execution.

EDUCATIONAL CONTENT: {chunk_content}
ANIMATION TITLE: {script.title}

PHASE 1 - SPATIAL PLANNING (MANDATORY):
<SPATIAL_PLAN>
Before coding, plan your screen layout:
1. Identify 3-4 key visual concepts to animate
2. Map screen regions: Title area (top), Main content (center), Supporting visuals (sides)
3. Plan object positioning to avoid overlaps
4. Design smooth transitions between concepts
5. Ensure readability with proper spacing
</SPATIAL_PLAN>

PHASE 2 - TIMING STRUCTURE (MANDATORY):
<TIMING_PLAN>
Plan your 45-second animation structure:
0-5 seconds: Title introduction and setup
5-15 seconds: First concept with visuals
15-25 seconds: Second concept with transition
25-35 seconds: Third concept or synthesis
35-45 seconds: Summary and clean conclusion
</TIMING_PLAN>

PHASE 3 - TECHNICAL CONSTRAINTS:
APPROVED MANIM TOOLKIT:
{MANIM_TOOLKIT}

LAYOUT RULES (CRITICAL):
- Screen boundaries: x=[-6,6], y=[-3.5,3.5]
- Title: font_size=32, to_edge(UP), color=WHITE
- Main text: font_size=26-28, proper spacing with buff=0.8
- Objects: minimum buff=0.6 between all elements
- Never exceed 2 text objects visible simultaneously
- Use FadeOut to clear screen before introducing new concepts
- Position objects using next_to() with adequate spacing

ANIMATION QUALITY STANDARDS:
- Clean, professional appearance
- Smooth transitions between concepts
- Educational clarity over visual complexity
- Proper timing with natural pacing
- No overlapping or cluttered elements

PHASE 4 - CODE GENERATION (STRICT FORMAT):
Your response must follow this EXACT structure:

<SPATIAL_PLAN>
[Your spatial planning here]
</SPATIAL_PLAN>

<TIMING_PLAN>
[Your timing planning here]
</TIMING_PLAN>

<MANIM_CODE>
from manim import *

class EducationalScene(Scene):
    def construct(self):
        # Clean, well-structured animation code implementing your plans
        
        # Title setup
        title = Text("Your Title", font_size=32, color=WHITE)
        title.to_edge(UP)
        self.play(Write(title), run_time=2)
        self.wait(1)
        
        # Your planned animation sections here
        
        # Clean conclusion
        self.wait(2)
</MANIM_CODE>

CRITICAL REQUIREMENTS:
- Complete both planning phases before coding
- Use ONLY approved Manim objects from the toolkit
- Follow exact spacing and positioning rules
- Implement smooth transitions with proper timing
- End with self.wait(2)
- NO markdown formatting (```python) in your response
- NO explanations outside the required tags

FORBIDDEN IN YOUR RESPONSE:
- ```python or ``` anywhere
- Complex objects not in the approved toolkit
- Text outside the required tag structure
- Overlapping or crowded visual elements
- Timing calculations that could go negative

Begin with spatial planning, then timing planning, then clean code implementation.
"""

        if self.model is None:
            raise RuntimeError("AI model not configured")

        response = await self.model.generate_content_async(prompt)
        text = str(response.text if hasattr(response, 'text') else response)
        
        animation_code = extract_tagged_content(text, "MANIM_CODE")
        if not animation_code:
            animation_code = clean_python_code(text)
        
        if not animation_code or "class EducationalScene" not in animation_code:
            raise RuntimeError("No valid Manim animation code generated")

        final_code = clean_python_code(animation_code)
        return final_code

    async def _render_manim_animation(self, manim_file: str, output_path: str) -> bool:
        """Render animation and copy to session directory."""
        try:
            abs_manim_file = os.path.abspath(manim_file)
            abs_output_path = os.path.abspath(output_path)
            
            os.makedirs(os.path.dirname(abs_output_path), exist_ok=True)
            
            script_dir = os.path.dirname(abs_manim_file)
            script_name = os.path.basename(abs_manim_file)
            
            result = subprocess.run([
                "manim", "-pql", script_name, "EducationalScene"
            ], capture_output=True, text=True, timeout=120, cwd=script_dir)

            if result.returncode == 0:
                logger.info("Manim rendering completed successfully")
                
                base_name = os.path.splitext(script_name)[0]
                
                possible_paths = [
                    f"{script_dir}/media/videos/{base_name}/480p15/EducationalScene.mp4",
                    f"{script_dir}/media/videos/{base_name}/720p30/EducationalScene.mp4",
                    f"{script_dir}/media/videos/{base_name}/1080p60/EducationalScene.mp4",
                    f"media/videos/{base_name}/480p15/EducationalScene.mp4",
                    f"media/videos/{base_name}/720p30/EducationalScene.mp4"
                ]
                
                for path in possible_paths:
                    if os.path.exists(path):
                        logger.info(f"Found MP4 at: {path}")
                        import shutil
                        shutil.copy2(path, abs_output_path)
                        logger.info(f"Copied MP4 to session directory: {abs_output_path}")
                        return True
                
                search_dirs = [script_dir, "media"]
                for search_dir in search_dirs:
                    if os.path.exists(search_dir):
                        for root, dirs, files in os.walk(search_dir):
                            for file in files:
                                if file == "EducationalScene.mp4" and base_name in root:
                                    found_file = os.path.join(root, file)
                                    logger.info(f"Found MP4 at: {found_file}")
                                    import shutil
                                    shutil.copy2(found_file, abs_output_path)
                                    logger.info(f"Copied MP4 to session directory: {abs_output_path}")
                                    return True
                
                logger.warning("Manim succeeded but MP4 location not found for copying")
                return True
            else:
                logger.error(f"Manim rendering failed: {result.stderr}")
                return False

        except Exception as e:
            logger.error(f"Animation rendering exception: {e}")
            return False

    def _save_session(self, session: Session):
        """Save complete session data to JSON file."""
        session_dir = f"sessions/{session.session_id}"
        os.makedirs(session_dir, exist_ok=True)

        session_file = f"{session_dir}/session.json"
        try:
            with open(session_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "session_id": session.session_id,
                    "topic": session.topic,
                    "scripts": {str(k): asdict(v) for k, v in session.scripts.items()},
                    "animations": session.animations,
                    "created_at": session.created_at
                }, f, indent=2, ensure_ascii=False)
            logger.info(f"Session data saved: {session_file}")
        except Exception as e:
            logger.error(f"Failed to save session data: {e}")

    def _load_session(self, session_id: str) -> Session:
        """Load complete session data from JSON file."""
        session_file = f"sessions/{session_id}/session.json"

        if not os.path.exists(session_file):
            raise FileNotFoundError(f"Session file not found: {session_file}")

        with open(session_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        scripts = {}
        for k, v in data.get("scripts", {}).items():
            if isinstance(v, dict):
                v_converted = v.copy()
                if "segment_id" in v_converted:
                    try:
                        v_converted["segment_id"] = int(v_converted["segment_id"])
                    except:
                        pass
                scripts[int(k)] = PodcastScript(**v_converted)

        return Session(
            session_id=data["session_id"],
            topic=data["topic"],
            scripts=scripts,
            animations=data.get("animations", {}),
            created_at=data.get("created_at", "")
        )

class PodcastApp:
    def __init__(self):
        self.generator = PodcastGenerator()

    async def process_request(self, input_data: dict) -> dict:
        """Process complete podcast generation request."""
        if input_data.get("is_first", False):
            return await self.generator.generate_complete_session(input_data)
        else:
            return await self.generator.update_remaining_scripts(input_data)

async def test_complete_system():
    """Test the complete podcast generation system."""
    app = PodcastApp()

    print("Testing Neural Networks - Complete Generation")
    test_input = {
        "session_id": "test_neural_complete",
        "topic": "Neural Networks and Deep Learning",
        "emotion_context": "curious",
        "rag_content": """
        Neural networks are computational models inspired by biological neural networks. 
        They consist of interconnected nodes organized in layers. Each connection 
        has a weight that determines signal strength. During training, weights are 
        adjusted through backpropagation to minimize prediction errors. Deep learning 
        uses multiple hidden layers to learn complex patterns. Common architectures 
        include feedforward networks, convolutional neural networks for image 
        processing, and recurrent neural networks for sequential data. Activation 
        functions like ReLU introduce non-linearity. Gradient descent optimizes 
        the network by updating weights to reduce loss.
        """,
        "is_first": True
    }

    try:
        result = await app.process_request(test_input)
        print(f"Generation result: {result['status']}")
        print(f"Scripts created: {len(result['scripts'])}")
        print(f"Animations created: {len(result['animations'])}")
        for i, anim_path in result['animations'].items():
            if anim_path:
                print(f"Animation {i}: {anim_path} \u2705")
            else:
                print(f"Animation {i}: Failed \u274c")
    except Exception as e:
        print(f"Test failed: {e} \u274c")

    print("\nTesting Script Update - Confused User")
    update_input = {
        "session_id": "test_neural_complete",
        "emotion_context": "confused",
        "completed_segments": [1, 2],
        "is_first": False
    }

    try:
        result = await app.process_request(update_input)
        print(f"Update result: {result['status']} - Pacing: {result['pacing_applied']} \u2705")
    except Exception as e:
        print(f"Update test failed: {e} \u274c")

if __name__ == "__main__":
    asyncio.run(test_complete_system())