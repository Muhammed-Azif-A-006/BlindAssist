import cv2
from vision.camera import open_camera
from vision.detector import YoloV8Detector

def draw_detections(frame, detections):
    for d in detections:
        x1, y1, x2, y2 = d["bbox"]
        label = d["label"]
        conf = d["conf"]

        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.putText(
            frame,
            f"{label} {conf:.2f}",
            (x1, max(20, y1 - 10)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (0, 255, 0),
            2
        )

def main():
    cap = open_camera(index=0, width=640, height=480)

    # yolov8n.pt = fastest on CPU
    detector = YoloV8Detector(model_name="yolov8n.pt", conf=0.4)

    print("Day 2: YOLOv8 detection running.")
    print("First run may download model weights. Press 'q' to quit.")

    while True:
        ok, frame = cap.read()
        if not ok:
            print("Failed to read frame.")
            break

        detections = detector.detect(frame)
        draw_detections(frame, detections)

        cv2.imshow("BlindAssist - Day 2 YOLOv8", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
