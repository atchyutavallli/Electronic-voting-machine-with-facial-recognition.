import face_recognition
import cv2
import numpy as np
import os
import serial
import time
from PIL import Image
import os
os.chdir(r"C:\Users\91807\Desktop\EVM_Hardware_Arduino[2]\EVM_Hardware_Arduino[2]\Python_Code")


# Initialize Serial Communication (Ensure COM10 is correct for your setup)
try:
    s = serial.Serial('COM10', 9600, timeout=1)
    time.sleep(2)  # Allow Arduino to reset
except serial.SerialException:
    print("❌ Error: Could not open serial port COM10. Check the connection.")
    exit()

# Get current folder and define image paths
CurrentFolder = os.getcwd()
image_paths = {
    "deepika": os.path.join(CurrentFolder, 'deepika.png'),
    "valli": os.path.join(CurrentFolder, 'valli.png'),
    "pavitra": os.path.join(CurrentFolder, 'pavitra.png')
}

# ✅ Load face encodings (with format fix using PIL)
def load_face_encoding(image_path):
    if not os.path.exists(image_path):
        print(f"❌ Error: File not found - {image_path}")
        return None

    pil_image = Image.open(image_path).convert("RGB")  # Ensure proper format
    image = np.array(pil_image)

    print(f"✅ Encoding image: {image_path}, shape: {image.shape}, dtype: {image.dtype}")
    encodings = face_recognition.face_encodings(image)

    if len(encodings) == 0:
        print(f"⚠️ Warning: No face detected in {image_path}")
        return None

    return encodings[0]

# Load known faces
known_face_encodings = []
known_face_names = []

for name, path in image_paths.items():
    encoding = load_face_encoding(path)
    if encoding is not None:
        known_face_encodings.append(encoding)
        known_face_names.append(name)

if not known_face_encodings:
    print("❌ Error: No valid faces found. Exiting...")
    exit()

admin_name = "valli"

# Start video capture
video_capture = cv2.VideoCapture(0, cv2.CAP_DSHOW)
if not video_capture.isOpened():
    print("❌ Error: Could not open webcam.")
    exit()

face_locations = []
face_encodings = []
face_names = []
process_this_frame = True
already_voted = set()

while True:
    ret, frame = video_capture.read()
    if not ret:
        print("❌ Error: Could not read frame from webcam.")
        break

    small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
    rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

    if process_this_frame:
        face_locations = face_recognition.face_locations(rgb_small_frame)
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

        face_names = []
        for face_encoding in face_encodings:
            matches = face_recognition.compare_faces(known_face_encodings, face_encoding, tolerance=0.4)
            name = "Unknown"

            if matches:
                face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
                best_match_index = np.argmin(face_distances)
                if matches[best_match_index]:
                    name = known_face_names[best_match_index]

            face_names.append(name)
            print(f"🧠 Detected Face: {name}")

            if name != "Unknown" and name != admin_name:
                if name not in already_voted:
                    print(f"🗳️ Face recognized: {name} - Waiting for vote")
                    s.write(b'a')

                    start_time = time.time()
                    while time.time() - start_time < 5:
                        if s.in_waiting:
                            response = s.read().decode('utf-8').strip()
                            if response == 'v':
                                print(f"✅ Vote recorded for: {name}")
                                already_voted.add(name)
                                break
                            elif response == 'x':
                                print(f"⏱️ No vote registered for: {name}")
                                break
                else:
                    print(f"ℹ️ Vote already recorded for: {name}")
            elif name == admin_name:
                print("🔐 Admin access granted.")
                s.write(b'c')
            else:
                print("❌ Invalid voter.")
                s.write(b'b')

            time.sleep(1)

    process_this_frame = not process_this_frame

    # Draw boxes
    for (top, right, bottom, left), name in zip(face_locations, face_names):
        top *= 4
        right *= 4
        bottom *= 4
        left *= 4

        cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
        cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
        cv2.putText(frame, name, (left + 6, bottom - 6),
                    cv2.FONT_HERSHEY_DUPLEX, 1.0, (255, 255, 255), 1)

    cv2.imshow('EVM Face Recognition', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        print("🚪 Exiting...")
        break

# Cleanup
video_capture.release()
cv2.destroyAllWindows()
s.close()
