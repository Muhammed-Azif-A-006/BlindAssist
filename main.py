import time
from audio.tts import TTS
from spatial.smoother import StableLabel
from spatial.distance import compute_distance
from spatial.direction import compute_direction
import cv2
from vision.camera import open_camera
from vision.detector import YoloV8Detector

TARGET_OBJECT = "bottle"   # change this to test: "person", "chair", "cup", "laptop"
MIN_CONF = 0.40

def bbox_area(bbox):
    x1, y1, x2, y2 = bbox
    return max(0, x2 - x1) * max(0, y2 - y1)

def pick_best(detections):
    """
    Pick the 'closest' object = largest bbox area.
    """
    return max(detections, key=lambda d: bbox_area(d["bbox"]))

def draw_single(frame, det):
    x1, y1, x2, y2 = det["bbox"]
    label = det["label"]
    conf = det["conf"]

    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 3)
    cv2.putText(
        frame,
        f"TARGET: {label} {conf:.2f}",
        (x1, max(20, y1 - 10)),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (0, 255, 0),
        2
    )

def draw_status(frame, text):
    cv2.putText(
        frame,
        text,
        (15, 35),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.9,
        (0, 0, 255),
        2
    )

def main():
    cap = open_camera(index=0, width=640, height=480)
    detector = YoloV8Detector(model_name="yolov8n.pt", conf=MIN_CONF)
    dir_smoother = StableLabel(window=3)
    dist_smoother = StableLabel(window=3)
    tts = TTS(rate=175)
    last_spoken = ""
    last_spoken_time = 0.0
    SPEAK_COOLDOWN = 1.5  # seconds
    REPEAT_INTERVAL = 4.0  # repeat same guidance every 4 sec


    print(f"Filtering enabled. Target = '{TARGET_OBJECT}'")
    print("Press 'q' to quit.")

    while True:
        ok, frame = cap.read()
        if not ok:
            print("Failed to read frame.")
            break

        detections = detector.detect(frame)

        # 1) Filter by label + confidence
        matches = [
            d for d in detections
            if d["label"].lower() == TARGET_OBJECT.lower() and d["conf"] >= MIN_CONF
        ]

        # 2) Pick best match or show status
        if not matches:
            draw_status(frame, f"'{TARGET_OBJECT}' NOT VISIBLE")
            now = time.time()
            speech = f"{TARGET_OBJECT} not visible"
            print("speech:", speech)

            should_speak = False
            if speech != last_spoken and (now - last_spoken_time) >= 1.5:
                should_speak = True
            elif speech == last_spoken and (now - last_spoken_time) >= 6.0:  # repeat slower
                should_speak = True

            if should_speak:
                tts.speak(speech)
                last_spoken = speech
                last_spoken_time = now


        else:
            best = pick_best(matches)
            h, w = frame.shape[:2]
            direction = compute_direction(best["bbox"], w)
            distance = compute_distance(best["bbox"], w, h)
            direction = dir_smoother.update(direction)
            distance = dist_smoother.update(distance)

            draw_single(frame, best)
            draw_status(frame, f"FOUND: {TARGET_OBJECT} | {direction.upper()} | {distance.upper()} (x{len(matches)})")
            speech = f"{TARGET_OBJECT} {direction} {distance}"
            print("speech:", speech)

            now = time.time()
            should_speak = False

            # Speak if message changed and cooldown passed
            if speech != last_spoken and (now - last_spoken_time) >= SPEAK_COOLDOWN:
                should_speak = True

            # Or repeat same message occasionally (so user keeps hearing guidance)
            elif speech == last_spoken and (now - last_spoken_time) >= REPEAT_INTERVAL:
                should_speak = True

            if should_speak:
                tts.speak(speech)
                last_spoken = speech
                last_spoken_time = now


        cv2.imshow("BlindAssist - Day 3 Filter Target", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
    tts.close()
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
