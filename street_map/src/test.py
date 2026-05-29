import requests
import os
import socket
from ultralytics import YOLO
from PIL import Image
import json
import time
import numpy as np
import cv2

# YOLO MODEL
model = YOLO(
    "/Users/davbot/PycharmProjects/street_map/runs/detect/train-5/weights/best.pt"
)

# CAMERA URL
CAM_URL = "http://192.168.0.219/capture"

# REQUEST SESSION (stabiler)
session = requests.Session()


# ─────────────────────────────────────
# GET CAMERA FRAME
# ─────────────────────────────────────

def get_frame():

    try:

        response = session.get(
            CAM_URL,
            timeout=5
        )

        img_array = np.frombuffer(
            response.content,
            np.uint8
        )

        frame = cv2.imdecode(
            img_array,
            cv2.IMREAD_COLOR
        )

        return frame

    except Exception as e:

        print("CAM ERROR:", e)

        return None


# ─────────────────────────────────────
# URL FIX
# ─────────────────────────────────────

def url_capture(url: str) -> str:

    if url.endswith('/capture'):
        return url

    return url.rstrip('/') + '/capture'


# ─────────────────────────────────────
# MAIN AI + SOCKET LOOP
# ─────────────────────────────────────

def neural_network_detection(url, arduino_ip, conf_thresh, port=12345):

    url = url_capture(url)

    # TCP SOCKET
    client_socket = socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM
    )

    client_socket.connect((arduino_ip, port))

    print("Verbunden mit ESP32")

    received_values = []

    save_path = 'daten2/obj'

    os.makedirs(save_path, exist_ok=True)

    try:

        while True:

            # DATEN EMPFANGEN
            data = client_socket.recv(1024).decode()

            # MEHRERE NACHRICHTEN VERARBEITEN
            messages = data.splitlines()

            for msg in messages:

                msg = msg.strip()

                if not msg:
                    continue

                try:

                    value = int(msg)

                    received_values.append(value)

                    print(f"Empfangen: {value}")

                    # ESP32 REQUEST
                    if value == 42:

                        frame = get_frame()

                        if frame is None:

                            client_socket.sendall(
                                ("STOP\n").encode()
                            )

                            continue

                        # OPTIONAL ROTATION
                        # frame = cv2.rotate(frame, cv2.ROTATE_180)

                        try:

                            # YOLO INFERENCE
                            results = model(
                                frame,
                                conf=conf_thresh
                            )

                            annotated = results[0].plot()

                            detected = False

                            command = "STOP"

                            # ALLE ERKANNTEN BOXEN
                            for box in results[0].boxes:

                                detected = True

                                cls = int(box.cls[0])

                                name = model.names[cls]

                                print("Detected:", name)

                                # BOX POSITION
                                x1, y1, x2, y2 = box.xyxy[0]

                                center_x = (x1 + x2) / 2

                                print("CENTER X:", center_x)

                                # AUTO STEUERUNG
                                if center_x < 220:

                                    command = "LEFT"

                                elif center_x > 420:

                                    command = "RIGHT"



                                else:

                                    command = "FORWARD"


                                print("COMMAND:", command)

                                # NUR ERSTE BOX BENUTZEN
                                break

                            # FALLS NICHTS ERKANNT
                            if not detected:

                                command = "STOP"

                            # COMMAND SENDEN
                            client_socket.sendall(
                                (command + "\n").encode()
                            )

                        except Exception as e:

                            print("YOLO ERROR:", e)

                            client_socket.sendall(
                                ("STOP\n").encode()
                            )

                except ValueError:

                    print(f"Ungültige Nachricht: {msg}")

            # OPTIONAL STOP
            if len(received_values) >= 300:

                print("Genug Werte empfangen.")

                break

    finally:

        client_socket.close()

        print("Socket geschlossen")


# ─────────────────────────────────────
# START
# ─────────────────────────────────────

neural_network_detection(
    url="http://192.168.0.219/capture",
    arduino_ip="192.168.0.73",
    port=12345,
    conf_thresh=0.5
)