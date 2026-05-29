import flask
import time
import socket
import json
from flask import request
from flask_cors import CORS

from ultralytics import YOLO

from pathfinding.core.grid import Grid
from pathfinding.finder.a_star import AStarFinder

import cv2
import threading
import requests
import numpy as np

# ─────────────────────────────────────
# FLASK
# ─────────────────────────────────────

app = flask.Flask(__name__)
CORS(app)
received_values = []
# ─────────────────────────────────────
# YOLO MODEL
# ─────────────────────────────────────

model = YOLO(
    "/Users/davbot/PycharmProjects/street_map/runs/detect/train-5/weights/best.pt"
)

# ─────────────────────────────────────
# ESP32 CAM
# ─────────────────────────────────────

CAM_URL = "http://192.168.0.219/capture"

# ─────────────────────────────────────
# AUTO CAR
# ─────────────────────────────────────
CAM_IP = "192.168.0.219"
arduino_ip = "192.168.0.73"
arduino_port = 1234

# ─────────────────────────────────────
# GRID
# ─────────────────────────────────────

matrix_x = [
    [253, 334, 423, 485, 554, 634, 708, 752],
    [253, 334, 423, 485, 554, 634, 708, 793],
    [253, 334, 423, 485, 554, 634, 743, 803],
    [253, 334, 423, 485, 554, 634, 743, 803]
]

matrix_y = [
    [53, 53, 53, 53, 53, 53, 53, 53],
    [99, 104, 137, 131, 126, 127, 133, 154],
    [203, 203, 203, 203, 203, 203, 203, 203],
    [327, 327, 327, 327, 327, 327, 351, 365]
]

matrix = [
    [0, 1, 0, 0, 0, 1, 0, 1],
    [1, 1, 1, 1, 1, 1, 1, 1],
    [0, 1, 0, 1, 0, 1, 0, 1],
    [0, 1, 0, 1, 0, 1, 0, 0]
]

# ─────────────────────────────────────
# LAST FRAME
# ─────────────────────────────────────

last_good_frame = None
"""client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((arduino_ip, arduino_port))"""
# ─────────────────────────────────────
# ESP32 FRAME HOLEN
# ─────────────────────────────────────

def get_frame():

    global last_good_frame

    try:

        response = requests.get(
            CAM_URL,
            timeout=1
        )

        img_array = np.frombuffer(
            response.content,
            np.uint8
        )

        frame = cv2.imdecode(
            img_array,
            cv2.IMREAD_COLOR
        )

        if frame is not None:

            last_good_frame = frame.copy()

        return frame

    except Exception as e:

        print("CAM ERROR:", e)

        # Letztes funktionierendes Bild zurückgeben
        if last_good_frame is not None:
            return last_good_frame.copy()

        return None

# ─────────────────────────────────────
# AUTO CAR REQUEST
# ─────────────────────────────────────

"""def send_car_command(command):

    try:

        requests.get(
            f"http://{CAR_IP}/{command}",
            timeout=0.3
        )

        print("SEND:", command)

    except Exception as e:

        print("CAR ERROR:", e)
"""
# ─────────────────────────────────────
# YOLO LOOP
# ─────────────────────────────────────

def yolo_loop():

    print("YOLO LOOP START")

    cv2.namedWindow("YOLO")

    last_detection_time = 0
    annotated = np.zeros((480, 640, 3), dtype=np.uint8)

    last_command = ""
    no_detection_counter = 0

    while True:

        current_time = time.time()

        try:

            # Alle 0.5 Sekunden neue Detection
            if current_time - last_detection_time > 0.5:

                frame = get_frame()

                if frame is not None:

                    # OPTIONAL ROTATION
                    frame = cv2.rotate(frame, cv2.ROTATE_180)

                    try:

                        results = model(frame)

                        annotated = results[0].plot()

                        detected = False

                        for box in results[0].boxes:

                            detected = True

                            cls = int(box.cls[0])
                            name = model.names[cls]

                            print("Detected:", name)

                            # BOX POSITION
                            x1, y1, x2, y2 = box.xyxy[0]

                            center_x = (x1 + x2) / 2

                            print("CENTER X:", center_x)

                            command = "GO"
                            print("GO")
                            # AUTO STEUERUNG
                            if center_x < 220:

                                command = "LEFT"

                            elif center_x > 420:

                                command = "RIGHT"

                            else:

                                command = "FORWARD"
                            client_socket.sendall(command + "\n".encode())
                            # Nur senden wenn neuer Command
                            #if command != last_command:

                            #send_car_command(command)

                            #last_command = command

                        # Keine Detection
                        if not detected:

                            no_detection_counter += 1

                            # Erst nach mehreren Frames stoppen
                            if no_detection_counter > 3:

                                if last_command != "STOP":

                                    #send_car_command("STOP")

                                    last_command = "STOP"

                        else:

                            no_detection_counter = 0



                        """while True:
                            # Daten vom Arduino empfangen
                            response = client_socket.recv(1024).decode().strip()

                            if response:  # Falls eine Antwort empfangen wurde
                                try:

                                    value = str(response)  # Versuche, die Antwort in einn String umzuwandeln
                                    received_values.append(value)  # Wert in die Liste speichern
                                    print(f"Empfangen und gespeichert: {value}")
                                    if (1 == 1):
                                        image_path = capture_image(url)
                                        if image_path:
                                            classify_image(image_path)"""
                    except Exception as e:

                        print("YOLO ERROR:", e)

                last_detection_time = current_time

            # Fenster IMMER anzeigen
            cv2.imshow("YOLO", annotated)

            # Fenster stabil halten
            key = cv2.waitKey(1)

            # ESC zum Beenden
            if key == 27:
                break

            time.sleep(0.03)

        except Exception as e:

            print("MAIN LOOP ERROR:", e)

            time.sleep(0.5)

    cv2.destroyAllWindows()

# ─────────────────────────────────────
# GRID HELPER
# ─────────────────────────────────────

def nearest_grid_node(mouse_x, mouse_y):

    best_distance = float("inf")
    best_node = None

    grid = Grid(matrix=matrix)

    for row in range(len(matrix_x)):

        for col in range(len(matrix_x[row])):

            gx = matrix_x[row][col]
            gy = matrix_y[row][col]

            distance = (
                (mouse_x - gx) ** 2 +
                (mouse_y - gy) ** 2
            )

            if distance < best_distance:

                best_distance = distance
                best_node = grid.node(col, row)

    return best_node

# ─────────────────────────────────────
# ROUTE API
# ─────────────────────────────────────

@app.route("/route", methods=["GET"])
def route():

    start_x = int(request.args.get("start_x"))
    start_y = int(request.args.get("start_y"))

    goal_x = int(request.args.get("goal_x"))
    goal_y = int(request.args.get("goal_y"))

    start = nearest_grid_node(start_x, start_y)
    end = nearest_grid_node(goal_x, goal_y)

    local_grid = Grid(matrix=matrix)

    start_node = local_grid.node(start.x, start.y)
    end_node = local_grid.node(end.x, end.y)

    finder = AStarFinder()

    path, runs = finder.find_path(
        start_node,
        end_node,
        local_grid
    )

    real_path = []

    for node in path:

        real_path.append({
            "x": matrix_x[node.y][node.x],
            "y": matrix_y[node.y][node.x]
        })

    return {
        "path": real_path
    }

# ─────────────────────────────────────
# MAIN
# ─────────────────────────────────────

if __name__ == "__main__":

    # Flask Thread
    flask_thread = threading.Thread(
        target=lambda: app.run(
            host="0.0.0.0",
            port=8000,
            debug=False,
            use_reloader=False
        )
    )

    flask_thread.daemon = True
    flask_thread.start()

    # YOLO MAIN LOOP
    yolo_loop()