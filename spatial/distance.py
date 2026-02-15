def compute_distance(bbox, frame_width: int, frame_height: int) -> str:
    """
    Rough distance based on bbox area ratio.
    Returns: 'far' | 'mid' | 'near'
    """
    x1, y1, x2, y2 = bbox
    box_area = max(0, x2 - x1) * max(0, y2 - y1)
    frame_area = frame_width * frame_height if frame_width and frame_height else 1

    ratio = box_area / frame_area  # 0..1

    # Tune these thresholds based on your camera
    if ratio < 0.01:
        return "far"
    elif ratio > 0.15:
        return "near"
    return "mid"
