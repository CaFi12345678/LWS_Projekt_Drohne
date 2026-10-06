import os
import time
import cv2
import KeyboardTelloModule as kp
from djitellopy import tello

# Konfiguration
SAVE_PATH = "Resources/Images"
if not os.path.exists(SAVE_PATH):
    os.makedirs(SAVE_PATH)


def getKeyboardInput(drone_instance, current_frame):
    """Liest Tastatureingaben aus und steuert die Drohne."""
    # LEFT/RIGHT, FRONT/BACK, UP/DOWN, YAW VELOCITY
    lr, fb, ud, yv = 0, 0, 0, 0

    speed = 80
    liftSpeed = 80
    moveSpeed = 85
    rotationSpeed = 100

    # Bewegung: Links / Rechts
    if kp.getKey("LEFT"):
        lr = -speed
    elif kp.getKey("RIGHT"):
        lr = speed

    # Bewegung: Vorwärts / Rückwärts
    if kp.getKey("UP"):
        fb = moveSpeed
    elif kp.getKey("DOWN"):
        fb = -moveSpeed

    # Bewegung: Hoch / Runter
    if kp.getKey("w"):
        ud = liftSpeed
    elif kp.getKey("s"):
        ud = -liftSpeed

    # Rotation: Drehung Links / Rechts
    if kp.getKey("d"):
        yv = rotationSpeed
    elif kp.getKey("a"):
        yv = -rotationSpeed

    # Landen und Starten
    if kp.getKey("q"):
        drone_instance.land()
        time.sleep(3)
    elif kp.getKey("e"):
        drone_instance.takeoff()

    # Screenshot speichern
    if kp.getKey("z"):
        if current_frame is not None:
            filename = f"{SAVE_PATH}/img_{int(time.time())}.jpg"
            cv2.imwrite(filename, current_frame)
            print(f"Screenshot gespeichert unter: {filename}")
            time.sleep(0.3)

    # Flip ausführen (hier beispielhaft nach rechts 'r')
    elif kp.getKey("f"):
        # Mögliche Werte: 'l' (links), 'r' (rechts), 'f' (vorne), 'b' (hinten)
        drone_instance.flip("r")
        time.sleep(0.5)

    return [lr, fb, ud, yv]


# Tastatur-Modul initialisieren
kp.init()

# Verbindung zur Drohne aufbauen
drone = tello.Tello()
drone.connect()

# Batteriestatus prüfen
battery_percentage = drone.get_battery()
print(f"Batteriestatus: {battery_percentage}%")

# Kamera-Stream starten
drone.streamon()
# Holen des Stream-Objekts (verhindert Lags beim Abrufen des Frames)
frame_read = drone.get_frame_read()

print("Steuerung bereit. Drücke 'e' zum Starten, 'q' zum Landen.")

while True:
    # 1. Aktuelles Bild der Kamera auslesen
    img = frame_read.frame

    if img is not None:
        # Bild anzeigen (Größenänderung optional, 1080x720)
        img_display = cv2.resize(img, (1080, 720))
        cv2.imshow("DroneCapture", img_display)
    else:
        img_display = None

    # 2. Eingaben abfragen und Werte berechnen
    keyValues = getKeyboardInput(drone, img_display)

    # 3. Steuerbefehle an die Drohne senden
    drone.send_rc_control(
        keyValues[0], keyValues[1], keyValues[2], keyValues[3]
    )

    # OpenCV Event-Loop (wichtig für die Darstellung des Fensters)
    if cv2.waitKey(1) & 0xFF == ord("c"):  # Beendet das Skript bei Taste 'c'
        break

    # Kurze Pause, um die CPU und den Netzwerkbuffer zu entlasten
    time.sleep(0.05)

# Ressourcen freigeben
drone.streamoff()
cv2.destroyAllWindows()
