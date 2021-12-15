import cv2


def to_jpg(frame):
    ret, buffer = cv2.imencode(".jpg", frame)
    return buffer.tobytes()




def convert_gray(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (21, 21), 0)
    return gray

