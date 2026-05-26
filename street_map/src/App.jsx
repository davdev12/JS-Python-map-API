import mapImage from "./assets/map.png"
import pinImage from "./assets/Google_Maps_pin.svg.png"
import gpsImage from "./assets/gps.png"

import { useState } from "react"

function App() {

    const [x, setX] = useState(300)
    const [y, setY] = useState(200)
    const [gpsX, setGpsX] = useState(700)
    const [gpsY, setGpsY] = useState(312)

    const [path, setPath] = useState([])

    const [angle, setAngle] = useState(0)

    function handleClick(event) {

        const clickX = event.clientX
        const clickY = event.clientY

        setX(clickX)
        setY(clickY)

        fetch(
    `http://127.0.0.1:8000/route?start_x=${gpsX}&start_y=${gpsY}&goal_x=${clickX}&goal_y=${clickY}`
)
.then(r => r.json())
.then(data => {

    console.log(data)

    setPath(data.path)

})
.catch(err => {
    console.error(err)
})
        .catch(err => {
            console.error(err)
        })
    }

    return (

        <div
            onClick={handleClick}
            style={{
                width: "100vw",
                height: "186vh",
                backgroundImage: `url(${mapImage})`,
                backgroundSize: "cover",
                backgroundPosition: "center",
                position: "absolute",
                overflow: "hidden"
            }}
        >

            {/* ROUTE */}

            {path.map((point, index) => (

                <div
                    key={index}
                    style={{
                        position: "absolute",
                        left: point.x - 5 + "px",
                        top: point.y - 5 + "px",
                        width: "10px",
                        height: "10px",
                        backgroundColor: "red",
                        borderRadius: "50%",
                        pointerEvents: "none"
                    }}
                />

            ))}

            {/* CLICK PIN */}

            <img
                src={pinImage}
                alt="pin"
                style={{
                    position: "absolute",
                    top: y - 35 + "px",
                    left: x - 10 + "px",
                    width: "20px",
                    pointerEvents: "none"
                }}
            />

            {/* GPS */}

            <img
    src={gpsImage}
    alt="location"
    style={{
        position: "absolute",
        left: gpsX + "px",
        top: gpsY + "px",
        width: "40px"
    }}
/>

        </div>
    )
}

export default App