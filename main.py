#!/usr/bin/env python3
"""
CortexAI - Main Orchestrator
This script manages the end-to-end flow of an adaptive learning session.
"""

import asyncio
import json
import logging
import os
import shutil
from typing import Optional, Dict, List
from collections import Counter

# --- Configuration and Core Components ---
from core.config import settings
from core.state_manager import state_manager

# --- Agents ---
from agents.manim_agent import PodcastGenerator
from agents.slide_agent import SlidesAgent
from agents.quiz_agent import QuizAgent

# --- Services ---
from services.rag_pipeline.retriever import RAGRetriever
from services.tts_service import TTSService

# --- Logging Configuration ---
LOG_FILE = "cortexai_session.log"
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - [%(module)s] - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)

class LearningSessionOrchestrator:
    """Manages the state and flow of a single learning session."""

    def __init__(self, topic: str, user_name: str, input_pdf_dir: Optional[str] = "input/"):
        logging.info("--- CortexAI Orchestrator Initializing ---")
        self.topic = topic
        self.user_name = user_name
        self.input_pdf_dir = input_pdf_dir
        self.session_id = None
        self.output_dir = None

        # --- Data Stores ---
        self.rag_content: Optional[str] = None
        self.session_data: Dict[str, any] = {"segments": {}}
        self.session_metrics: List[str] = []

        # --- Service and Agent Instances ---
        self.rag_retriever: RAGRetriever
        self.podcast_generator: PodcastGenerator
        self.slides_agent: SlidesAgent
        self.quiz_agent: QuizAgent
        self.tts_service: TTSService

    async def initialize_services(self):
        """Pre-flight checks and service initializations."""
        logging.info("--- Running Pre-flight Checks and Initializing Services ---")

        # 1. Check for API Keys
        if not settings.GEMINI_API_KEY:
            raise ValueError("FATAL: GEMINI_API_KEY not found in .env file.")
        if not settings.ELEVENLABS_API_KEY:
            raise ValueError("FATAL: ELEVENLABS_API_KEY not found in .env file.")
        logging.info("✓ API keys found.")

        # 2. Check for Manim
        if not shutil.which("manim"):
            logging.warning("WARNING: 'manim' command not found in PATH. Video animations will be disabled.")
            self.manim_available = False
        else:
            logging.info("✓ 'manim' command found.")
            self.manim_available = True

        # 3. Initialize Services
        self.rag_retriever = RAGRetriever()
        self.podcast_generator = PodcastGenerator()
        self.slides_agent = SlidesAgent()
        await self.slides_agent.initialize() # Has async init
        self.quiz_agent = QuizAgent()
        await self.quiz_agent.initialize() # Has async init
        self.tts_service = TTSService()
        await self.tts_service.initialize()
        
        logging.info("--- All Services Initialized Successfully ---")

    async def _prepare_content_source(self):
        """Ingests content from PDFs or web, then retrieves a unified context."""
        logging.info("--- Phase 1: Content Ingestion and RAG Preparation ---")
        
        pdf_files = [f for f in os.listdir(self.input_pdf_dir) if f.endswith('.pdf')] if os.path.exists(self.input_pdf_dir) else []

        if pdf_files:
            logging.info(f"Found {len(pdf_files)} PDFs in '{self.input_pdf_dir}'. Ingesting them.")
            self.rag_retriever.batch_ingest_pdfs(self.input_pdf_dir)
        else:
            logging.info(f"No PDFs found. Scraping web for topic: '{self.topic}'.")
            self.rag_retriever.ingest_topic(self.topic, max_books=1)

        # Validate that ingestion was successful
        stats = self.rag_retriever.get_statistics()
        if stats['total_chunks'] == 0:
            raise RuntimeError("FATAL: Failed to ingest any content. The RAG database is empty. Cannot proceed.")
        logging.info(f"✓ Content ingested successfully. Total chunks in DB: {stats['total_chunks']}")

        # Retrieve a unified context for generation
        self.rag_content = self.rag_retriever.get_context(self.topic, max_tokens=4000)
        if not self.rag_content or len(self.rag_content) < 500:
            raise RuntimeError("FATAL: Could not retrieve sufficient context from RAG pipeline for the topic.")
        logging.info(f"✓ Retrieved {len(self.rag_content)} characters of context for content generation.")

    async def _generate_initial_learning_materials(self):
        """Creates the full suite of learning materials before the session starts."""
        logging.info("--- Phase 2: Generating Initial Learning Materials ---")

        # 1. Generate Podcast Scripts and Animations
        try:
            gen_input = {
                "session_id": self.session_id,
                "topic": self.topic,
                "rag_content": self.rag_content,
                "is_first": True
            }
            podcast_result = await self.podcast_generator.generate_complete_session(gen_input)
            
            # Verify results and handle partial failures
            for i in range(1, 5):
                script_data = podcast_result.get("scripts", {}).get(i)
                anim_path = podcast_result.get("animations", {}).get(i)
                
                if not script_data:
                    raise RuntimeError(f"FATAL: Failed to generate script for segment {i}.")
                
                self.session_data["segments"][i] = {
                    "script": script_data["content"],
                    "animation_path": anim_path if self.manim_available else None
                }
                
                if self.manim_available and not anim_path:
                    logging.warning(f"Animation for segment {i} failed to render. Proceeding with audio only.")

            logging.info("✓ Podcast scripts and animations generated.")
            self.session_data["podcast_scripts"] = [s['script'] for s in self.session_data["segments"].values()]

        except Exception as e:
            logging.error(f"Error during podcast generation: {e}", exc_info=True)
            raise RuntimeError("FATAL: Could not generate primary podcast content.")

        # 2. Generate Slides/Flashcards
        try:
            slides_result = await self.slides_agent.generate_flashcards(
                content_chunks=self.session_data["podcast_scripts"],
                emotion_context="neutral"
            )
            self.session_data["slides_path"] = slides_result.get("ppt_file_path")
            logging.info(f"✓ Slides generated at: {self.session_data['slides_path']}")
        except Exception as e:
            logging.warning(f"Could not generate slides: {e}. Session will continue without them.")
            self.session_data["slides_path"] = None

        # 3. Generate Quiz
        try:
            quiz_result = await self.quiz_agent.generate_quiz(
                content=self.rag_content,
                emotion_context="neutral"
            )
            self.session_data["quiz"] = quiz_result
            logging.info(f"✓ Quiz with {len(quiz_result.get('questions',[]))} questions generated.")
        except Exception as e:
            logging.warning(f"Could not generate quiz: {e}. Session will continue without it.")
            self.session_data["quiz"] = None

    async def _present_segment(self, segment_index: int):
        """Simulates presenting a segment by logging, saving TTS, and waiting."""
        logging.info(f"--- Presenting Segment {segment_index} ---")
        segment = self.session_data["segments"][segment_index]
        
        # 1. "Play" Video
        if segment["animation_path"]:
            logging.info(f"[PRESENTING] Video: {segment['animation_path']}")
        else:
            logging.info("[PRESENTING] No video for this segment.")

        # 2. Generate and Save TTS Audio
        audio_path = os.path.join(self.output_dir, f"segment_{segment_index}_audio.mp3")
        try:
            with open(audio_path, "wb") as f:
                async for chunk in self.tts_service.generate_speech_stream(segment["script"]):
                    f.write(chunk)
            logging.info(f"[PRESENTING] Audio: {audio_path}")
        except Exception as e:
            logging.error(f"Failed to generate TTS for segment {segment_index}: {e}")

        # 3. Simulate segment duration
        # In a real app, you would use a media player and wait for it to finish.
        # e.g., using ffpyplayer or another library.
        await asyncio.sleep(45)

    def _get_current_user_state(self) -> str:
        """
        Simulates real-time monitoring by reading from engagement_analysis.json.
        NOTE: For this to work, vision.py must be running as a separate process.
        """
        try:
            with open("engagement_analysis.json", 'r') as f:
                data = json.load(f)
            if data.get("faces_data"):
                # For simplicity, use the emotion of the first detected face
                emotion = data["faces_data"][0].get("emotion", "neutral").lower()
                return emotion
            return "neutral"
        except (FileNotFoundError, json.JSONDecodeError):
            logging.warning("engagement_analysis.json not found or invalid. Defaulting to 'neutral' state.")
            return "neutral"

    async def _adapt_content(self, completed_segments: List[int], emotion: str):
        """Calls the agent to update remaining scripts based on emotion."""
        logging.info(f"Adapting remaining content based on detected emotion: '{emotion}'")
        try:
            update_input = {
                "session_id": self.session_id,
                "emotion_context": emotion,
                "completed_segments": completed_segments,
                "is_first": False
            }
            update_result = await self.podcast_generator.update_remaining_scripts(update_input)
            
            # Update the scripts in our session data
            for segment_id, script_data in update_result.get("updated_scripts", {}).items():
                self.session_data["segments"][segment_id]["script"] = script_data["content"]
            logging.info(f"✓ Content adapted with pacing: {update_result.get('pacing_applied')}")
        except Exception as e:
            logging.error(f"Failed to adapt content: {e}")

    def _simulate_quiz_taking(self) -> float:
        """Placeholder to simulate user taking the quiz. Returns a score."""
        if not self.session_data.get("quiz"):
            return 0.0
        
        total_questions = len(self.session_data["quiz"]["questions"])
        # Simulate getting 80% of them right
        correct_answers = int(total_questions * 0.8)
        logging.info(f"User took the quiz and scored {correct_answers}/{total_questions}.")
        return correct_answers / total_questions if total_questions > 0 else 0.0

    async def _generate_final_report(self, quiz_score: float) -> str:
        """Compiles all session data into a final, human-readable markdown report."""
        logging.info("--- Generating Final Report ---")
        
        # Analyze engagement metrics
        emotion_counts = Counter(self.session_metrics)
        most_common_emotion = emotion_counts.most_common(1)[0][0] if emotion_counts else "N/A"
        
        report_lines = [
            f"# Learning Session Report for {self.user_name}",
            f"**Topic:** {self.topic}",
            f"**Session ID:** {self.session_id}",
            "---",
            "## Performance Summary",
            f"- **Final Quiz Score:** {quiz_score:.0%}",
            "---",
            "## Engagement Analysis",
            f"- **Dominant Emotional State:** {most_common_emotion.capitalize()}",
            "- **Emotion Trend during Session:** " + " -> ".join(self.session_metrics),
            "---",
            "## Personalized Feedback"
        ]
        
        feedback = ""
        if quiz_score < 0.7:
            feedback += "It seems you found some of the concepts challenging. We recommend reviewing the generated PowerPoint slides and re-listening to the podcast segments. "
        else:
            feedback += "Excellent work! You have a solid grasp of the material. "
            
        if "confused" in self.session_metrics or "frustrated" in self.session_metrics:
            feedback += "We noticed you may have been confused at times. The system adapted the content to be slower and more explanatory. Re-visiting those segments might be helpful."
        else:
            feedback += "Your engagement levels appeared stable and positive throughout the session."
            
        report_lines.append(feedback)
        
        report = "\n\n".join(report_lines)
        report_path = os.path.join(self.output_dir, "final_report.md")
        with open(report_path, 'w') as f:
            f.write(report)
        logging.info(f"✓ Final report saved to {report_path}")
        return report

    async def run(self):
        """Main entry point to run the entire orchestrated learning session."""
        try:
            # Phase 0: Setup
            await self.initialize_services()
            self.session_id = state_manager.create_session()
            self.output_dir = f"output/session_{self.session_id}"
            os.makedirs(self.output_dir, exist_ok=True)
            logging.info(f"--- Starting Session {self.session_id} for user '{self.user_name}' ---")

            # Phase 1: Content Prep
            await self._prepare_content_source()

            # Phase 2: Initial Generation
            await self._generate_initial_learning_materials()

            # Phase 3: Interactive Learning Loop
            completed_segments = []
            for i in range(1, 5):
                await self._present_segment(i)
                
                detected_emotion = self._get_current_user_state()
                self.session_metrics.append(detected_emotion)
                logging.info(f"User state after segment {i}: {detected_emotion}")

                completed_segments.append(i)
                if i < 4: # No need to adapt after the last segment
                    await self._adapt_content(completed_segments, detected_emotion)
            
            # Phase 4: Final Assessment & Reporting
            final_quiz_score = self._simulate_quiz_taking()
            await self._generate_final_report(final_quiz_score)

        except Exception as e:
            logging.critical(f"A critical error occurred during the session: {e}", exc_info=True)
        finally:
            if self.session_id:
                state_manager.end_session(self.session_id)
            logging.info(f"--- Session {self.session_id} Finished. ---")


async def main():
    """Configures and runs the orchestrator."""
    # NOTE: To run this, you must have an .env file with GEMINI_API_KEY and ELEVENLABS_API_KEY.
    # Also, ensure the 'input/' directory exists.
    # To test the vision system, run 'python vision/vision.py' in a separate terminal.
    
    orchestrator = LearningSessionOrchestrator(
        topic="The fundamentals of transformer neural networks",
        user_name="Naveen"
    )
    await orchestrator.run()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (ValueError, RuntimeError) as e:
        logging.critical(f"Orchestrator failed to start: {e}")
    except KeyboardInterrupt:
        logging.info("\nSession interrupted by user.")