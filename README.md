<div align="center">
<pre>
________/\\\\\\\\\____________________________________________________________________________/\\\\\\\\\_____/\\\\\\\\\\\_        
 _____/\\\////////___________________________________________________________________________/\\\\\\\\\\\\\__\/////\\\///__       
  ___/\\\/___________________________________________/\\\____________________________________/\\\/////////\\\_____\/\\\_____      
   __/\\\_________________/\\\\\_____/\\/\\\\\\\___/\\\\\\\\\\\_____/\\\\\\\\___/\\\____/\\\_\/\\\_______\/\\\_____\/\\\_____     
    _\/\\\_______________/\\\///\\\__\/\\\/////\\\_\////\\\////____/\\\/////\\\_\///\\\/\\\/__\/\\\\\\\\\\\\\\\_____\/\\\_____    
     _\//\\\_____________/\\\__\//\\\_\/\\\___\///_____\/\\\_______/\\\\\\\\\\\____\///\\\/____\/\\\/////////\\\_____\/\\\_____   
      __\///\\\__________\//\\\__/\\\__\/\\\____________\/\\\_/\\__\//\\///////______/\\\/\\\___\/\\\_______\/\\\_____\/\\\_____  
       ____\////\\\\\\\\\__\///\\\\\/___\/\\\____________\//\\\\\____\//\\\\\\\\\\__/\\\/\///\\\_\/\\\_______\/\\\__/\\\\\\\\\\\_ 
        _______\/////////_____\/////_____\///______________\/////______\//////////__\///____\///__\///________\///__\///////////__

</pre>
  <h1>CortexAI</h1>
  <p><strong>Learning That Listens. An AI Tutor That Adapts to You in Real-Time.</strong></p>
</div>

---

### What if your learning platform knew when you were confused?

Traditional online courses are a one-way street. They present information at a fixed pace, regardless of whether you're engaged, bored, or completely lost. They can't see the subtle furrow of your brow when a concept doesn't click.

**CortexAI is different.** It's a next-generation adaptive learning system that creates a personalized curriculum from any topic or document, and then watches, listens, and adapts to your emotional state. It's not just a course; it's a dynamic, responsive AI tutor.

---

## A Session with CortexAI

Meet Alex, who wants to learn the fundamentals of "Transformer Neural Networks."

### **[0:00]** — The Genesis of a Course
Alex provides CortexAI with a few research papers on the topic. In under a minute, CortexAI's RAG pipeline reads, chunks, and indexes the documents. Its team of AI agents then springs to life, generating a complete, four-part multimedia course:
*   Four animated video lectures.
*   Four corresponding podcast-style audio scripts.
*   A full deck of PowerPoint flashcards.
*   A comprehensive 5-question quiz.

### **[5:30]** — The Moment of Confusion
Alex breezes through the first two segments on the high-level architecture. But as Segment 3 dives into the complexities of "Scaled Dot-Product Attention," their expression changes.
*   **What Alex experiences:** A slight, almost imperceptible frown of concentration and confusion.
*   **What CortexAI sees:** In the background, the `vision` service detects a shift in Alex's facial landmarks. The emotion classifier's output flips from `neutral` to `confused`.

### **[5:45]** — The Real-Time Adaptation
No jarring pop-ups break Alex's focus. Instead, the system adapts seamlessly.
*   The AI-generated voice from the Text-to-Speech service, which was energetic, shifts to a calmer, more deliberate and encouraging tone for the next paragraph.
*   More importantly, CortexAI's `PodcastGenerator` agent instantly rewrites the script for the upcoming Segment 4. It adjusts the pacing from "normal" to "slow," adding more foundational analogies and breaking down complex ideas into simpler steps, all while preserving the core educational content.

**The result?** Alex navigates the difficult patch without frustration. The course didn't just plow ahead; it noticed, adapted, and helped them through it. At the end of the session, a detailed report highlights their strengths and pinpoints the exact concepts they found challenging, creating a clear path for future study.

---

## Why CortexAI is Different

| Feature                     | Description                                                                                                                                                                                           |
| :-------------------------- | :---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **🧠 Real-Time Adaptation**   | The only system of its kind that uses live facial expression and speech emotion analysis to adapt the pacing, tone, and style of educational content *during* the session.                              |
| **⚙️ Multi-Modal Generation** | It doesn't just present text. CortexAI autonomously generates a complete learning suite from scratch: Manim video animations, ElevenLabs audio podcasts, PowerPoint slides, and interactive quizzes. |
| **📚 Dynamic RAG Foundation**  | Feed it your own PDFs or simply give it a topic. Its powerful RAG (Retrieval-Augmented Generation) pipeline builds a robust knowledge base, ensuring all generated content is factually grounded.      |
| **📊 Insightful Reporting**    | At the end of each session, receive a personalized report detailing your quiz performance, engagement levels, and emotional trends, providing actionable feedback for your learning journey.             |

---

## The Intelligence Inside: How It Works

CortexAI operates as a sophisticated pipeline of interconnected services and intelligent agents, managed by a central orchestrator.

### 1. The Knowledge Core: The RAG Pipeline
This is the system's foundation. It ingests unstructured information and makes it queryable.
*   **Input**: A collection of PDFs from the `input/` folder or a topic string for web scraping.
*   **Process**:
    1.  `PDF Processor` extracts text.
    2.  `Text Chunker` intelligently splits text into manageable pieces.
    3.  `VectorDB` (using Sentence-Transformers & Qdrant) converts chunks into vector embeddings and stores them.
*   **Output**: A rich, persistent knowledge base that can be searched for relevant information instantly.

### 2. The Content Factory: Generation Agents
These agents take the synthesized knowledge from the RAG pipeline and craft the learning materials. They are powered by Google's Gemini Pro for reasoning and generation.
*   **`PodcastGenerator`**: The master creator. It takes the large context from the RAG and structures it into a 4-part narrative, then uses **Manim** to generate corresponding video animations for each part.
*   **`SlidesAgent`**: Receives the 4 generated podcast scripts and creates a perfectly aligned deck of PowerPoint slides/flashcards.
*   **`QuizAgent`**: Uses the full RAG context to generate a comprehensive quiz that tests understanding across the entire topic.

### 3. The Sensory Loop: Real-Time Feedback
This is what makes CortexAI adaptive. Two parallel services constantly monitor the user.
*   **`vision/vision.py`**: The "eyes" of the system. Uses OpenCV and Dlib to detect the user's facial expressions, classifying their emotion (neutral, happy, confused, etc.) and writing the output to `engagement_analysis.json`.
*   **`services/ser_service.py`**: The "ears." While not fully integrated into the adaptation loop in this version, it's capable of analyzing audio for emotional tone.

### 4. The Conductor: The Orchestrator (`main.py`)
The `LearningSessionOrchestrator` in `main.py` runs the entire show.

`Ingest Content` ➡️ `Generate All Materials` ➡️ `Loop:` (`Present Segment` ➡️ `Read Emotion` ➡️ `Adapt Next Segment`) ➡️ `Final Report`

This feedback loop ensures the system is not static but a living tutor that responds to the learner's needs.

---

## Getting Started

Follow these steps to run your own CortexAI session.

### Step 1: Prerequisites
*   Python 3.9+
*   Git
*   FFmpeg (for Manim). You must install this separately and ensure it's available in your system's PATH.
*   An environment with `PyTorch` and `TensorFlow` (as per `requirements.txt`).

### Step 2: Installation
```bash
# Clone the repository
git clone https://github.com/your-username/CortexAI.git
cd CortexAI

# Create a virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install the required packages
pip install -r requirements.txt
```

### Step 3: Configuration
1.  Locate the `.env.example` file in the `core/` directory.
2.  Rename it to `.env`.
3.  Open the `.env` file and add your API keys. The system will fail to start without them.
    ```env
    GEMINI_API_KEY="your_google_ai_studio_api_key"
    ELEVENLABS_API_KEY="your_elevenlabs_api_key"
    ```

### Step 4: Provide Learning Content
You have two options:

1.  **Use Your Own PDFs (Recommended):** Place any PDF documents you want to learn from inside the `input/` folder.
2.  **Use Web Scraping:** Leave the `input/` folder empty. The system will scrape sources like arXiv for content based on the `topic` set in `main.py`.

### Step 5: Run the System
CortexAI requires two processes to be run in parallel.

1.  **Terminal 1: Start the Vision Service**
    This process watches your webcam for facial expressions.
    ```bash
    python vision/vision.py
    ```    *Wait for it to initialize and say "Starting analysis...".*

2.  **Terminal 2: Start the Main Orchestrator**
    This runs the main learning session.
    ```bash
    python main.py
    ```

### Step 6: View the Output
All generated files are saved in the `output/` directory, organized by session ID.
*   **`output/session_[id]/final_report.md`**: Your personalized performance and engagement summary.
*   **`output/session_[id]/segment_[N]_audio.mp3`**: The generated audio for each segment.
*   **`output/flashcards.pptx`**: The generated PowerPoint presentation.
*   **`sessions/[session_id]/segment_[N].mp4`**: The rendered Manim video animations.