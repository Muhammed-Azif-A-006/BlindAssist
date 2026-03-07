from voice.listen import listen_for_command
import time
from audio.tts import TTS
from spatial.smoother import StableLabel
from spatial.distance import compute_distance
from spatial.direction import compute_direction
import cv2
from vision.camera import open_camera
from vision.detector import YoloV8Detector

TARGET_OBJECT = "person"
MIN_CONF = 0.40

SUPPORTED_OBJECTS = {
    "person", "bottle", "chair", "cup", "laptop",
    "cell phone", "book", "backpack"
}


def bbox_area(bbox):
    x1, y1, x2, y2 = bbox
    return max(0, x2 - x1) * max(0, y2 - y1)


def pick_best(detections):
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
    target_object = TARGET_OBJECT
    MIC_INDEX = None

    cap = open_camera(index=0, width=640, height=480)
    detector = YoloV8Detector(model_name="yolov8n.pt", conf=MIN_CONF)

    dir_smoother = StableLabel(window=3)
    dist_smoother = StableLabel(window=3)

    tts = TTS(rate=175)

    # ================= STATE MACHINE =================
    prev_direction = None
    prev_distance = None
    was_visible = False

    print(f"Filtering enabled. Target = '{target_object}'")
    print("Press 'v' for voice command, 'q' to quit.")

    while True:
        ok, frame = cap.read()
        if not ok:
            print("Failed to read frame.")
            break

        detections = detector.detect(frame)

        key = cv2.waitKey(1) & 0xFF

        # ================= VOICE INTENT =================
        if key == ord("v"):
            cmd = listen_for_command(device_index=MIC_INDEX)

            if not cmd:
                continue

            print("Command received:", cmd)

            if "stop" in cmd:
                target_object = None
                tts.speak("Search stopped")
                prev_direction = None
                prev_distance = None
                was_visible = False
                continue

            if "what" in cmd and "see" in cmd:
                if detections:
                    labels = sorted(set(d["label"] for d in detections))
                    seen = ", ".join(labels)
                    tts.speak(f"I see {seen}")
                else:
                    tts.speak("I see nothing")
                continue

            if "find" in cmd:
                words = cmd.split()
                candidate = words[-1]

                if candidate in SUPPORTED_OBJECTS:
                    target_object = candidate
                    tts.speak(f"Searching for {target_object}")

                    dir_smoother = StableLabel(window=3)
                    dist_smoother = StableLabel(window=3)

                    prev_direction = None
                    prev_distance = None
                    was_visible = False
                else:
                    tts.speak(f"{candidate} is not supported")

        if key == ord("q"):
            break

        # ================= SEARCH STATE =================
        if target_object is None:
            draw_status(frame, "SEARCH STOPPED")
            cv2.imshow("BlindAssist - Event Intelligence", frame)
            continue

        matches = [
            d for d in detections
            if d["label"].lower() == target_object.lower()
            and d["conf"] >= MIN_CONF
        ]

        if not matches:
            draw_status(frame, f"{target_object} NOT VISIBLE")

            if was_visible:
                tts.speak(f"{target_object} lost")
                was_visible = False
                prev_direction = None
                prev_distance = None

        else:
            best = pick_best(matches)

            h, w = frame.shape[:2]
            direction = compute_direction(best["bbox"], w)
            distance = compute_distance(best["bbox"], w, h)

            direction = dir_smoother.update(direction)
            distance = dist_smoother.update(distance)

            draw_single(frame, best)
            draw_status(
                frame,
                f"FOUND: {target_object} | {direction.upper()} | {distance.upper()} (x{len(matches)})"
            )

            # ================= IMPROVED EVENT LOGIC =================

            # First detection → speak full spatial info
            if not was_visible:
                tts.speak(f"{target_object} {direction} {distance}")
                was_visible = True

            else:
                # Direction changed
                if direction != prev_direction:
                    tts.speak(direction)

                # Distance changed
                elif distance != prev_distance:
                    if distance == "near":
                        tts.speak("very close")
                    else:
                        tts.speak(distance)

            prev_direction = direction
            prev_distance = distance

        cv2.imshow("BlindAssist - Event Intelligence", frame)

    tts.close()
    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()