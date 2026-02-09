import cv2

def open_camera(index=0, width=640, height=480):
    cap = cv2.VideoCapture(index)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

    if not cap.isOpened():
        raise RuntimeError(
            f"Could not open webcam (index={index}). "
            "Close Camera/Zoom/Browser and try index=1."
        )
    return cap

