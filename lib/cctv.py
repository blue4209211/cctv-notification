import cv2
import asyncio

from lib import config


camera = cv2.VideoCapture(config.cctv_camera)
face_cascade = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")
upper_body_cascade = cv2.CascadeClassifier("haarcascade_upperbody.xml")

event_loop = asyncio.get_event_loop()


async def _detect_face(frame, gray=None):
    if gray is None:
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(30, 30),
        flags=cv2.CASCADE_SCALE_IMAGE,
    )
    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
    return faces


async def _detect_body(frame, gray=None):
    if gray is None:
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = upper_body_cascade.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(30, 30),
        flags=cv2.CASCADE_SCALE_IMAGE,
    )
    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
    return faces


# TODO
# detect animals
async def _detect_objects(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    detection_response = await asyncio.gather(
        _detect_body(frame, gray), _detect_face(frame, gray)
    )
    return (detection_response[0], detection_response[1])


def get_feed():
    while True:
        success, frame = camera.read()

        if not success:
            break
        else:
            try:
                bodies, faces = event_loop.run_until_complete(_detect_objects(frame))
                yield (frame, bodies, faces)
            except Exception as e:
                print("unable to detect features", e)
