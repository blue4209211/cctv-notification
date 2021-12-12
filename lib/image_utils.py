import cv2


def to_jpg(frame):
    ret, buffer = cv2.imencode(".jpg", frame)
    return buffer.tobytes()
