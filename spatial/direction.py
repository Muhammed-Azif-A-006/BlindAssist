def compute_direction(bbox, frame_width: int) -> str:
    """
    bbox: (x1, y1, x2, y2)
    Uses bbox center vs frame center.
    Returns: 'left' | 'center' | 'right'
    """
    x1, _, x2, _ = bbox
    cx = (x1 + x2) / 2.0

    # Normalize to 0..1
    ratio = cx / frame_width

    if ratio < 0.40:
        return "left"
    elif ratio > 0.60:
        return "right"
    return "center"
