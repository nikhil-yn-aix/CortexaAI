# ---------------------------------------------------------------------------- #
#      Continuous Student Attention & Emotion Monitor (Backend-Only)             #
# ---------------------------------------------------------------------------- #
#
# Description:
# This script is a "headless" or backend-only version that uses a webcam
# for analysis without displaying any video feed. It runs entirely in the
# terminal, performing three main tasks:
# 1. Face Detection: Identifies faces in the video stream.
# 2. Emotion Recognition: Classifies the emotion of each detected face.
# 3. Attention Estimation: Determines head direction (left, right, center).
#
# The analysis summary is printed directly to the console.
# To stop the script, press Ctrl+C in your terminal.
#
# ---------------------------------------------------------------------------- #

#pip install opencv-python dlib-bin torch transformers Pillow tqdm requests
import cv2
import dlib
import numpy as np
from transformers import pipeline
from PIL import Image
import os
import requests
from tqdm import tqdm
import bz2
import time

# --- 1. MODEL AND UTILITY SETUP ---

# Define the path for the dlib landmark predictor model
PREDICTOR_PATH = "shape_predictor_68_face_landmarks.dat"

def download_dlib_model():
    """
    Downloads the dlib facial landmark predictor model if it doesn't exist.
    """
    if not os.path.exists(PREDICTOR_PATH):
        print("Downloading dlib facial landmark model. This may take a moment...")
        url = "http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2"
        response = requests.get(url, stream=True)
        response.raise_for_status()

        total_size_in_bytes = int(response.headers.get('content-length', 0))
        block_size = 1024  # 1 Kibibyte
        
        progress_bar = tqdm(total=total_size_in_bytes, unit='iB', unit_scale=True)
        
        decompressor = bz2.BZ2Decompressor()
        with open(PREDICTOR_PATH, 'wb') as f:
            for data in response.iter_content(block_size):
                progress_bar.update(len(data))
                f.write(decompressor.decompress(data))
        progress_bar.close()

        if total_size_in_bytes != 0 and progress_bar.n != total_size_in_bytes:
            print("ERROR, something went wrong during download")
        else:
            print("Model downloaded successfully.")

# --- 2. LOAD MODELS ---
print("Loading models, please wait...")
download_dlib_model()

try:
    detector = dlib.get_frontal_face_detector()
    predictor = dlib.shape_predictor(PREDICTOR_PATH)
except RuntimeError as e:
    print(f"Error loading dlib model: {e}")
    print("Please ensure 'shape_predictor_68_face_landmarks.dat' is in the correct directory.")
    exit()

# Using a CPU-optimized, lightweight CNN-based model.
emotion_classifier = pipeline(
    "image-classification",
    model="dima806/facial_emotions_image_detection",
    top_k=1
)

print("Models loaded successfully.")

# --- 3. CORE PROCESSING FUNCTION (Optimized for backend) ---

def get_engagement_summary(frame: np.ndarray):
    """
    Analyzes a single frame and returns a text summary of the analysis.
    The input frame is expected to be in RGB color format.
    """
    if frame is None:
        return "No frame received."

    gray_frame = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
    faces = detector(gray_frame)

    if not faces:
        return "Status: No face detected"

    analysis_summary = ""

    for i, face in enumerate(faces):
        x1, y1, x2, y2 = face.left(), face.top(), face.right(), face.bottom()

        # --- Emotion Recognition ---
        primary_emotion = "N/A"
        try:
            face_crop_img = frame[y1:y2, x1:x2]
            pil_face = Image.fromarray(face_crop_img)
            
            emotion_results = emotion_classifier(pil_face)
            if emotion_results:
                primary_emotion = emotion_results[0]['label'].capitalize()

        except Exception as e:
            print(f"Emotion detection error: {e}")

        # --- Attention Estimation (via Head Pose) ---
        attention_status = "N/A"
        try:
            landmarks = predictor(gray_frame, face)
            nose_point = (landmarks.part(30).x, landmarks.part(30).y)
            left_face_point = (landmarks.part(0).x, landmarks.part(0).y)
            right_face_point = (landmarks.part(16).x, landmarks.part(16).y)

            face_center_x = (left_face_point[0] + right_face_point[0]) // 2
            horizontal_diff = nose_point[0] - face_center_x
            
            threshold = 10 
            attention_status = "Center"
            if horizontal_diff > threshold:
                attention_status = "Looking Left"
            elif horizontal_diff < -threshold:
                attention_status = "Looking Right"
        except Exception as e:
            print(f"Attention estimation error: {e}")
        
        analysis_summary += f"Face {i+1}: Emotion={primary_emotion}, Attention={attention_status}\n"

    return analysis_summary.strip()


# --- 4. MAIN LOOP TO CAPTURE AND PROCESS WEBCAM FEED ---
if __name__ == "__main__":
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Error: Could not open webcam.")
        exit()
    
    print("\nStarting backend analysis. Press Ctrl+C to stop.")
    
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Failed to grab frame. Exiting.")
                break

            # Convert BGR (from OpenCV) to RGB for the models
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Get the analysis summary
            summary = get_engagement_summary(frame_rgb)
            
            # Print summary to terminal only if a face was detected
            if "Face" in summary:
                os.system('cls' if os.name == 'nt' else 'clear')
                print("--- Engagement Analysis ---")
                print(summary)
                print("---------------------------")
                print("Running... Press Ctrl+C to stop.")
            
            # Wait for 1 second before processing the next frame to reduce CPU load
            time.sleep(1)

    except KeyboardInterrupt:
        print("\nScript interrupted by user.")
    finally:
        # --- 5. CLEANUP ---
        print("Shutting down and releasing webcam...")
        cap.release()
        print("Done.")