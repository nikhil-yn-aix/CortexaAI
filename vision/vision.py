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
import json
from datetime import datetime

PREDICTOR_PATH = "shape_predictor_68_face_landmarks.dat"
OUTPUT_FILE = "engagement_analysis.txt"
JSON_OUTPUT_FILE = "engagement_analysis.json"

def download_dlib_model():
    if not os.path.exists(PREDICTOR_PATH):
        print("Downloading dlib facial landmark model...")
        url = "http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2"
        response = requests.get(url, stream=True)
        response.raise_for_status()

        total_size_in_bytes = int(response.headers.get('content-length', 0))
        block_size = 1024
        progress_bar = tqdm(total=total_size_in_bytes, unit='iB', unit_scale=True)
        decompressor = bz2.BZ2Decompressor()
        
        with open(PREDICTOR_PATH, 'wb') as f:
            for data in response.iter_content(block_size):
                progress_bar.update(len(data))
                f.write(decompressor.decompress(data))
        progress_bar.close()
        print("Model downloaded successfully.")

def write_analysis_to_file(summary, faces_data=None):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(f"Last Updated: {timestamp}\n")
        f.write("=" * 50 + "\n")
        f.write(summary + "\n")
        f.write("=" * 50 + "\n")
    
    json_data = {
        "timestamp": timestamp,
        "status": "active",
        "summary": summary,
        "faces_detected": len(faces_data) if faces_data else 0,
        "faces_data": faces_data or []
    }
    
    with open(JSON_OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(json_data, f, indent=2, ensure_ascii=False)

def initialize_output_files():
    startup_message = "Starting engagement analysis...\nWaiting for face detection..."
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(f"Analysis Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("=" * 50 + "\n")
        f.write(startup_message + "\n")
    
    json_data = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "status": "initializing",
        "summary": startup_message,
        "faces_detected": 0,
        "faces_data": []
    }
    
    with open(JSON_OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(json_data, f, indent=2, ensure_ascii=False)

def test_camera_access():
    print("Testing camera access...")
    for i in range(3):
        print(f"Trying camera index {i}...")
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            ret, frame = cap.read()
            if ret:
                print(f"Camera {i} working!")
                cap.release()
                return i
            cap.release()
    return None

print("Loading models...")
download_dlib_model()

try:
    detector = dlib.get_frontal_face_detector()
    predictor = dlib.shape_predictor(PREDICTOR_PATH)
except RuntimeError as e:
    print(f"Error loading dlib model: {e}")
    exit()

emotion_classifier = pipeline(
    "image-classification",
    model="dima806/facial_emotions_image_detection",
    top_k=1,
    device=-1
)

print("Models loaded successfully.")
initialize_output_files()

def get_engagement_summary(frame: np.ndarray):
    if frame is None:
        return "No frame received.", []

    gray_frame = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
    faces = detector(gray_frame)

    if not faces:
        return "Status: No face detected", []

    analysis_summary = ""
    faces_data = []

    for i, face in enumerate(faces):
        x1, y1, x2, y2 = face.left(), face.top(), face.right(), face.bottom()

        primary_emotion = "N/A"
        try:
            face_crop_img = frame[y1:y2, x1:x2]
            pil_face = Image.fromarray(face_crop_img)
            emotion_results = emotion_classifier(pil_face)
            if emotion_results:
                primary_emotion = emotion_results[0]['label'].capitalize()
        except Exception as e:
            print(f"Emotion detection error: {e}")

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
        
        face_data = {
            "face_id": i + 1,
            "emotion": primary_emotion,
            "attention": attention_status,
            "bounding_box": {"x1": x1, "y1": y1, "x2": x2, "y2": y2}
        }
        faces_data.append(face_data)
        analysis_summary += f"Face {i+1}: Emotion={primary_emotion}, Attention={attention_status}\n"

    return analysis_summary.strip(), faces_data

if __name__ == "__main__":
    camera_index = test_camera_access()
    
    if camera_index is None:
        print("ERROR: No working camera found!")
        print("Solutions:")
        print("1. Close all apps using camera (Teams, Skype, Chrome)")
        print("2. Check Windows camera permissions")
        print("3. Restart your computer")
        exit()

    cap = cv2.VideoCapture(camera_index)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    cap.set(cv2.CAP_PROP_FPS, 30)
    
    print(f"Using camera {camera_index}")
    print("Starting analysis... Press Ctrl+C to stop.")
    
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Failed to grab frame. Retrying...")
                time.sleep(1)
                continue

            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            summary, faces_data = get_engagement_summary(frame_rgb)
            write_analysis_to_file(summary, faces_data)
            
            if "Face" in summary:
                os.system('cls' if os.name == 'nt' else 'clear')
                print("--- Live Analysis ---")
                print(summary)
                print("--------------------")
            
            time.sleep(1)

    except KeyboardInterrupt:
        print("\nStopping...")
        final_json = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "status": "stopped",
            "summary": "Analysis stopped.",
            "faces_detected": 0,
            "faces_data": []
        }
        
        with open(JSON_OUTPUT_FILE, 'w', encoding='utf-8') as f:
            json.dump(final_json, f, indent=2, ensure_ascii=False)
            
    finally:
        cap.release()
        print("Done.")