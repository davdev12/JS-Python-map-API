import mapImage from "./assets/map.png"
import pinImage from "./assets/Google_Maps_pin.svg.png"
import gpsImage from "./assets/gps.png"
import { useState, useRef } from "react"

function App() {

    const [x, setX] = useState(300)
    const [y, setY] = useState(200)
    const animationRef = useRef(null)
    const [gps, setGps] = useState({
    x: 700,
    y: 312
});
    const [path, setPath] = useState([])

    const [angle, setAngle] = useState(0)
function moveTo(targetX, targetY) {

    cancelAnimationFrame(animationRef.current)

    return new Promise(resolve => {

        const speed = 2

        function animate() {

            setGps(prev => {

                const dx = targetX - prev.x
                const dy = targetY - prev.y
                const angle =
                Math.atan2(dy, dx) * 180 / Math.PI + 90

                setAngle(angle)
                const distance = Math.sqrt(dx * dx + dy * dy)

                if (distance < speed) {

                    resolve()

                    return {
                        x: targetX,
                        y: targetY
                    }
                }

                const vx = dx / distance
                const vy = dy / distance

                return {
                    x: prev.x + vx * speed,
                    y: prev.y + vy * speed
                }
            })

            animationRef.current =
                requestAnimationFrame(animate)
        }

        animate()
    })
}
    function handleClick(event) {

        const clickX = event.clientX
        const clickY = event.clientY

        setX(clickX)
        setY(clickY)

        fetch(
    `http://127.0.0.1:8000/route?start_x=${gps.x}&start_y=${gps.y}&goal_x=${clickX}&goal_y=${clickY}`
)
.then(r => r.json())
.then(async data => {

    console.log(data)

    setPath(data.path)

    moveTo(clickX-50, clickY)

    for (const point of data.path) {

    await moveTo(point.x, point.y)

}
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
        transform: `rotate(${angle}deg)`,
        transformOrigin: "center center",
        position: "absolute",
        left: gps.x - 20 + "px",
        top: gps.y - 20 + "px",
        width: "40px"
    }}
/>

        </div>
    )
}


export default App