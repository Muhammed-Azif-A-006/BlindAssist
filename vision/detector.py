from ultralytics import YOLO

class YoloV8Detector:
    """
    YOLOv8 pretrained detector (CPU-friendly with yolov8n.pt).
    """
    def __init__(self, model_name: str = "yolov8n.pt", conf: float = 0.4):
        self.model = YOLO(model_name)
        self.conf = conf

    def detect(self, frame_bgr):
        """
        Returns list of detections:
        [{"label": str, "conf": float, "bbox": (x1,y1,x2,y2)}, ...]
        """
        results = self.model.predict(frame_bgr, conf=self.conf, verbose=False)
        r = results[0]

        detections = []
        if r.boxes is None:
            return detections

        names = r.names  # class_id -> class name

        for box in r.boxes:
            cls_id = int(box.cls[0].item())
            label = names[cls_id]
            conf = float(box.conf[0].item())
            x1, y1, x2, y2 = box.xyxy[0].tolist()

            detections.append({
                "label": label,
                "conf": conf,
                "bbox": (int(x1), int(y1), int(x2), int(y2)),
            })

        return detections
