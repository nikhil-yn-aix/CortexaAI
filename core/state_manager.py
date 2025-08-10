"""
User session and learning state management.
Tracks emotions, progress, and adaptive teaching state across WebSocket connections.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Optional
import uuid

from core.config import settings


@dataclass
class UserState:
    """Individual user's learning session state."""
    
    session_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    session_start: datetime = field(default_factory=datetime.now)
    
    # Real-time emotional state
    current_emotion: str = "neutral"
    emotion_confidence: float = 0.0
    engagement_score: float = settings.DEFAULT_ENGAGEMENT
    
    # Adaptive learning state
    current_topic: str = "transformers"
    difficulty_level: float = settings.DEFAULT_DIFFICULTY
    learning_progress: Dict[str, float] = field(default_factory=dict)
    
    # Performance tracking
    confusion_count: int = 0
    success_count: int = 0


class StateManager:
    """Manages all active user sessions."""
    
    def __init__(self):
        self.active_sessions: Dict[str, UserState] = {}
    
    def create_session(self) -> str:
        """Create new user session and return session ID."""
        user_state = UserState()
        self.active_sessions[user_state.session_id] = user_state
        return user_state.session_id
    
    def get_session(self, session_id: str) -> Optional[UserState]:
        """Get session by ID, returns None if not found."""
        return self.active_sessions.get(session_id)
    
    def end_session(self, session_id: str) -> bool:
        """Remove session and cleanup, returns True if session existed."""
        return self.active_sessions.pop(session_id, None) is not None
    
    def update_emotion(self, session_id: str, emotion: str, confidence: float):
        """Update user's current emotional state."""
        if session := self.get_session(session_id):
            session.current_emotion = emotion
            session.emotion_confidence = confidence
    
    def update_engagement(self, session_id: str, engagement: float):
        """Update user's engagement level from VIR system."""
        if session := self.get_session(session_id):
            session.engagement_score = max(0.0, min(1.0, engagement))
    
    def adjust_difficulty(self, session_id: str, adjustment: float):
        """Adjust content difficulty level within bounds."""
        if session := self.get_session(session_id):
            new_difficulty = session.difficulty_level + adjustment
            session.difficulty_level = max(0.1, min(1.0, new_difficulty))
    
    def record_progress(self, session_id: str, topic: str, score: float):
        """Record learning progress for specific topic."""
        if session := self.get_session(session_id):
            session.learning_progress[topic] = max(0.0, min(1.0, score))
    
    def increment_confusion(self, session_id: str):
        """Track confusion incident for adaptation patterns."""
        if session := self.get_session(session_id):
            session.confusion_count += 1
    
    def increment_success(self, session_id: str):
        """Track success incident for adaptation patterns."""
        if session := self.get_session(session_id):
            session.success_count += 1


state_manager = StateManager()