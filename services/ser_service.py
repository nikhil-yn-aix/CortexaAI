"""
Speech Emotion Recognition using emotion2vec+ foundation model.
"""

import asyncio
import os
import tempfile
import warnings
from typing import Tuple

warnings.filterwarnings("ignore")
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"

try:
    from funasr import AutoModel
    EMOTION2VEC_AVAILABLE = True
except ImportError:
    EMOTION2VEC_AVAILABLE = False

class SERService:
    """Speech emotion recognition using emotion2vec+ foundation model."""
    
    def __init__(self):
        self.model = None
        self.is_loaded = False
    
    async def load_model(self):
        """Load emotion2vec+ model asynchronously."""
        if self.is_loaded or not EMOTION2VEC_AVAILABLE:
            return
            
        try:
            loop = asyncio.get_event_loop()
            self.model = await loop.run_in_executor(None, self._load_model_sync)
            self.is_loaded = True
            print("✓ emotion2vec+ loaded")
        except Exception as e:
            print(f"✗ emotion2vec+ load failed: {e}")
    
    def _load_model_sync(self):
        """Load emotion2vec+ model synchronously."""
        return AutoModel(model="iic/emotion2vec_plus_large", hub="hf")
    
    async def analyze_emotion(self, audio_bytes: bytes) -> Tuple[str, float]:
        """Analyze emotion from audio bytes."""
        if not EMOTION2VEC_AVAILABLE:
            return self._mock_analysis()
            
        if not self.is_loaded:
            await self.load_model()
        
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
            tmp_file.write(audio_bytes)
            tmp_path = tmp_file.name
        
        try:
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(None, self._classify, tmp_path)
            return result
        finally:
            os.unlink(tmp_path)
    
    def _classify(self, audio_path: str) -> Tuple[str, float]:
        """Classify emotion using emotion2vec+."""
        try:
            result = self.model.generate(audio_path, granularity="utterance", extract_embedding=False)
            
            if result and len(result) > 0:
                prediction = result[0]
                
                if 'labels' in prediction and 'scores' in prediction:
                    labels = prediction['labels']
                    scores = prediction['scores']
                    
                    if labels and scores:
                        max_idx = scores.index(max(scores))
                        label = labels[max_idx]
                        score = scores[max_idx]
                        
                        if isinstance(label, str) and '/' in label:
                            emotion = label.split('/')[-1] 
                        else:
                            emotion = str(label)
                        
                        return emotion, float(score)
            
            return "neutral", 0.5
            
        except Exception as e:
            print(f"✗ emotion2vec+ error: {e}")
            return "neutral", 0.5
    
    def _mock_analysis(self) -> Tuple[str, float]:
        """Mock emotion analysis when FunASR unavailable."""
        import random
        emotions = ["angry", "happy", "sad", "neutral"]
        return random.choice(emotions), round(random.uniform(0.6, 0.95), 2)

ser_service = SERService()

async def test_ser_service():
    """Test the SER service with audio files."""
    print("Testing emotion2vec+ SER Service")
    print("=" * 40)
    
    await ser_service.load_model()
    
    test_files = ["test/sad1.wav", "test/sad2.wav", "test/sad3.wav", "test/happy.wav", "test/neutral.wav"]
    tests_run = 0
    
    for test_file in test_files:
        if os.path.exists(test_file):
            print(f"Testing: {test_file}")
            
            try:
                with open(test_file, "rb") as f:
                    audio_data = f.read()
                
                emotion, confidence = await ser_service.analyze_emotion(audio_data)
                print(f"Result: {emotion} ({confidence:.3f})")
                tests_run += 1
                
            except Exception as e:
                print(f"✗ Error: {e}")
    
    if tests_run == 0:
        print("Running mock test...")
        for i in range(3):
            emotion, confidence = await ser_service.analyze_emotion(b"mock_data")
            print(f"Mock {i+1}: {emotion} ({confidence:.3f})")
    
    print("=" * 40)
    print(f"Tests completed: {tests_run} real files")
    print("✓ emotion2vec+ ready" if EMOTION2VEC_AVAILABLE else "✗ Install: pip install funasr modelscope")

if __name__ == "__main__":
    asyncio.run(test_ser_service())
