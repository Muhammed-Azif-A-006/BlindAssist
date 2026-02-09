import time
import cv2
from vision.camera import open_camera

def main():
    cap = open_camera(index=0, width=640, height=480)

    print("Day 1: Webcam test running.")
    print("Press 'q' to quit.")

    frame_count = 0
    start = time.time()

    while True:
        ok, frame = cap.read()
        if not ok:
            print("ERROR: Failed to read frame.")
            break

        frame_count += 1
        if time.time() - start >= 1.0:
            print(f"FPS: {frame_count}")
            frame_count = 0
            start = time.time()

        cv2.imshow("BlindAssist - Day 1 Webcam", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
