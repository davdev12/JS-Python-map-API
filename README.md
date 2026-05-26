<h1>Javascript API</h1>
This JS code creates a background in form of a map. I decided to use a simplified version of the Salt Lake City, Utah (please don't ask why).
I also imported a pin or destination location marker and a gps arrow or current location marker.
<img width="1206" height="633" alt="Bildschirmfoto 2026-05-27 um 00 46 39" src="https://github.com/user-attachments/assets/14616325-0f4a-4e83-aebd-f38641ec794b" />

<h1>Python API</h1>
In this project we use the flask module to be able to communicate with the browser window.
<img width="396" height="139" alt="Bildschirmfoto 2026-05-27 um 00 50 10" src="https://github.com/user-attachments/assets/724e3c84-01ce-4893-b551-89dc5a0d8a4a" />
And for the route calculation we use the pathfinding module, especially the A* algorithm.

<h2>Grid/matrix</h2>
To calculate the best possible route for our moving object pathfinding requires a special grid or matrix
<img width="285" height="118" alt="Bildschirmfoto 2026-05-27 um 00 44 11" src="https://github.com/user-attachments/assets/e1a19403-a7ee-4606-a207-d601d6aa0357" />
It depicts our map in a for pathfinding relevant form: 1 are dots where the object CAN move, 2 dots that act as obstacles, like walls, or other boundaries .
