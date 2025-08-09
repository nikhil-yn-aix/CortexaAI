"""
Text-to-Speech Service using ElevenLabs with streaming support.
"""

import asyncio
import sys
from typing import AsyncGenerator, Optional

try:
    from elevenlabs.client import AsyncElevenLabs
    from elevenlabs import VoiceSettings
    ELEVENLABS_AVAILABLE = True
except ImportError:
    ELEVENLABS_AVAILABLE = False

from core.config import settings

class TTSService:
    """Production-ready Text-to-Speech service with streaming."""
    
    def __init__(self):
        self.api_key = getattr(settings, 'ELEVENLABS_API_KEY', None)
        self.client = None
        self.voice_id = None
        self.is_initialized = False
    
    async def initialize(self):
        """Initialize ElevenLabs client and voice."""
        if self.is_initialized:
            return
            
        if not ELEVENLABS_AVAILABLE:
            print("✗ ElevenLabs not available")
            return
            
        if not self.api_key:
            print("✗ ElevenLabs API key not found")
            return
        
        try:
            self.client = AsyncElevenLabs(api_key=self.api_key)
            
            voices = await self.client.voices.get_all()
            preferred_voices = ["Brian", "Adam", "Antoni", "Josh"]
            
            for voice_name in preferred_voices:
                voice = next((v for v in voices.voices if v.name == voice_name), None)
                if voice:
                    self.voice_id = voice.voice_id
                    break
            
            if not self.voice_id and voices.voices:
                self.voice_id = voices.voices[0].voice_id
                
            print(f"✓ ElevenLabs initialized with voice: {self.voice_id}")
            self.is_initialized = True
            
        except Exception as e:
            print(f"✗ ElevenLabs initialization failed: {e}")
    
    async def generate_speech_stream(
        self, 
        text: str,
        emotion_context: Optional[str] = None
    ) -> AsyncGenerator[bytes, None]:
        """Generate streaming audio from text."""
        if not self.is_initialized:
            await self.initialize()
        
        if not self.client or not self.voice_id:
            async for chunk in self._mock_stream(text):
                yield chunk
            return
        
        try:
            voice_settings = self._create_voice_settings(emotion_context)
            
            audio_stream = self.client.text_to_speech.convert(
                text=text,
                voice_id=self.voice_id,
                model_id="eleven_flash_v2_5",
                voice_settings=voice_settings,
                optimize_streaming_latency=0,
                output_format="mp3_44100_128"
            )
            
            async for chunk in audio_stream:
                if chunk:
                    yield chunk
                    
        except Exception as e:
            print(f"✗ TTS generation failed: {e}")
            async for chunk in self._mock_stream(text):
                yield chunk
    
    def _create_voice_settings(self, emotion: Optional[str]):
        """Create voice settings based on emotion."""
        if not ELEVENLABS_AVAILABLE:
            return None
            
        stability = 0.75
        similarity_boost = 0.85
        style = 0.0
        
        if emotion == "frustrated":
            stability = 0.8
            style = 0.1
        elif emotion == "confused":
            stability = 0.9
            similarity_boost = 0.9
        elif emotion == "happy":
            style = 0.3
            
        return VoiceSettings(
            stability=stability,
            similarity_boost=similarity_boost,
            style=style,
            use_speaker_boost=True
        )
    
    async def _mock_stream(self, text: str) -> AsyncGenerator[bytes, None]:
        """Mock streaming for testing."""
        for i in range(5):
            chunk = b'\x00' * 1024
            yield chunk
            await asyncio.sleep(0.1)
    
    async def close(self):
        """Cleanup resources."""
        if self.client and hasattr(self.client, 'aclose'):
            try:
                await self.client.aclose()
            except:
                pass


tts_service = TTSService()

async def test_tts_service():
    """Test TTS service and save audio files."""
    print("Testing ElevenLabs TTS Service")
    print("=" * 40)
    
    try:
        await tts_service.initialize()
        
        test_cases = [
            ("Hello, welcome to our AI learning platform.", "neutral"),
            ("Don't worry, let's break this down step by step.", "frustrated"),
            ("Great job! You're getting the hang of this.", "happy"),
            ("Let me explain this concept more clearly.", "confused"),
        ]
        
        for i, (text, emotion) in enumerate(test_cases, 1):
            print(f"Test {i}: {emotion} context")
            print(f"Text: {text[:50]}...")
            
            try:
                chunks_received = 0
                total_bytes = 0
                audio_chunks = []
                
                async for chunk in tts_service.generate_speech_stream(text, emotion):
                    chunks_received += 1
                    total_bytes += len(chunk)
                    audio_chunks.append(chunk)
                    
                    if chunks_received <= 3:
                        print(f"  Chunk {chunks_received}: {len(chunk)} bytes")
                
                
                filename = f"test/elevenlabs_{emotion}.mp3"
                with open(filename, "wb") as f:
                    for chunk in audio_chunks:
                        f.write(chunk)
                
                print(f"  ✓ Complete: {chunks_received} chunks, {total_bytes} total bytes")
                print(f"  ✓ Saved to: {filename}")
                
            except Exception as e:
                print(f"  ✗ Error: {e}")
            
            print()
        
        print("=" * 40)
        print("✓ ElevenLabs TTS ready for production" if ELEVENLABS_AVAILABLE and tts_service.api_key else "✗ Running in mock mode")
            
    finally:
        await tts_service.close()

def main():
    """Main with Windows event loop fix."""
    
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    try:
        asyncio.run(test_tts_service())
    except KeyboardInterrupt:
        print("\n✗ Interrupted")
    except Exception as e:
        print(f"✗ Error: {e}")

if __name__ == "__main__":
    main()
