import cv2
from vision.camera import open_camera
from vision.detector import YoloV8Detector

TARGET_OBJECT = "cup"   # change this to test: "person", "chair", "cup", "laptop"
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
        else:
            best = pick_best(matches)
            draw_single(frame, best)
            draw_status(frame, f"FOUND: {TARGET_OBJECT} (x{len(matches)})")

        cv2.imshow("BlindAssist - Day 3 Filter Target", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
