import flask
from flask import request
from flask_cors import CORS

from pathfinding.core.grid import Grid
from pathfinding.finder.a_star import AStarFinder

app = flask.Flask(__name__)
CORS(app)
# ----------------------------
# GRID KOORDINATEN
# ----------------------------

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

# 1 = begehbar
# 0 = blockiert

matrix = [
    [1, 0, 0, 0, 1, 0, 1, 1],
    [1, 1, 1, 1, 1, 1, 1, 1],
    [1, 0, 1, 0, 1, 0, 1, 1],
    [1, 1, 1, 1, 1, 1, 1, 1]
]

grid = Grid(matrix=matrix)

# ----------------------------
# NÄCHSTEN GRID NODE FINDEN
# ----------------------------

def nearest_grid_node(mouse_x, mouse_y):

    best_distance = float("inf")
    best_node = None

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

# ----------------------------
# API ROUTE
# ----------------------------

@app.route("/route", methods=["GET"])
def route():
    start_x = int(request.args.get("start_x"))
    start_y = int(request.args.get("start_y"))

    goal_x = int(request.args.get("goal_x"))
    goal_y = int(request.args.get("goal_y"))

    # Startpunkt
    start = nearest_grid_node(start_x, start_y)

    # Zielpunkt
    end = nearest_grid_node(goal_x, goal_y)

    print("start:", start.x, start.y)
    print("end:", end.x, end.y)

    # Neues Grid pro Anfrage
    local_grid = Grid(matrix=matrix)

    # Nodes aus neuem Grid holen
    start_node = local_grid.node(start.x, start.y)
    end_node = local_grid.node(end.x, end.y)

    # A*
    finder = AStarFinder()

    path, runs = finder.find_path(
        start_node,
        end_node,
        local_grid
    )

    print("path:", path)

    # Bildschirm-Koordinaten erzeugen
    real_path = []

    for node in path:

        real_path.append({
            "x": matrix_x[node.y][node.x],
            "y": matrix_y[node.y][node.x]
        })

    print("real path:", real_path)

    # JSON an React senden
    return {
        "path": real_path
    }

# ----------------------------
# SERVER START
# ----------------------------

if __name__ == "__main__":
    app.run(port=8000, debug=True)