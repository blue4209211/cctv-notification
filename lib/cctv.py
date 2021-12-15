import cv2
import asyncio
import imutils
import time
import atexit

from lib import config
from lib.image_utils import convert_gray

event_loop = asyncio.get_event_loop()


def _close():
    print("disconnecting cv2 client")
    cv2.destroyAllWindows()


atexit.register(_close)


class FaceDetector:
    face_cascade = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")

    async def detect(self, frame, gray=None):
        if gray is None:
            gray = convert_gray(frame)

        faces = self.face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=3,
            minSize=(50, 50),
            flags=cv2.CASCADE_SCALE_IMAGE,
        )
        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        return faces


class BodyDetector:
    upper_body_cascade = cv2.CascadeClassifier("haarcascade_upperbody.xml")

    async def detect(self, frame, gray=None):
        if gray is None:
            gray = convert_gray(frame)

        faces = self.upper_body_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=3,
            minSize=(50, 50),
            flags=cv2.CASCADE_SCALE_IMAGE,
        )
        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
        return faces


class MotionDetector:
    def __init__(self):
        self.avg_frame = None
        self.motion_counter = 0
        self.delta_frame = None

    async def detect(self, frame, gray=None):
        if gray is None:
            gray = convert_gray(frame)

        # if the average frame is None, initialize it
        if self.avg_frame is None:
            self.avg_frame = gray.copy().astype("float")
            return []

        # compute the absolute difference between the current frame and
        # first frame
        cv2.accumulateWeighted(gray, self.avg_frame, 0.5)
        self.delta_frame = cv2.absdiff(gray, cv2.convertScaleAbs(self.avg_frame))

        # threshold the delta image, dilate the thresholded image to fill
        # in holes, then find contours on thresholded image
        thresh = cv2.threshold(
            self.delta_frame, config.motion_delta_thresh, 255, cv2.THRESH_BINARY
        )[1]
        thresh = cv2.dilate(thresh, None, iterations=2)
        cnts = cv2.findContours(
            thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )
        cnts = imutils.grab_contours(cnts)

        # loop over the contours
        found = False
        for c in cnts:
            # if the contour is too small, ignore it
            if cv2.contourArea(c) < config.motion_min_area:
                continue
            # compute the bounding box for the contour, draw it on the frame,
            # and update the text
            (x, y, w, h) = cv2.boundingRect(c)
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            found = True

        if found:
            self.motion_counter = self.motion_counter + 1
            if self.motion_counter > config.motion_min_frames:
                self.motion_counter = 0
                return [frame]
            else:
                return []
        else:
            self.motion_counter = 0
            return []


# "face": FaceDetector(), "body": BodyDetector(),
DETECTORS = {"motion": MotionDetector()}


async def _detect_objects(frame):
    gray = convert_gray(frame)

    detector_keys = []
    detectors = []

    for key, d in DETECTORS.items():
        detector_keys.append(key)
        detectors.append(d)

    detection_response = await asyncio.gather(
        *[d.detect(frame, gray) for d in detectors]
    )

    return dict(zip(detector_keys, detection_response))


def _release_camara(camera):
    print("disconnecing camera")
    if camera:
        camera.release()


def get_feed():
    attempt = 0
    print("initializing video stream")
    camera = cv2.VideoCapture(config.cctv_camera)
    while True:
        success, frame = camera.read()

        if not success:
            time.sleep(2)
            attempt = attempt + 1
            print("unable to get feed", camera.isOpened())
            _release_camara(camera)
            if attempt > 100:
                break
        else:
            attempt = 0
            try:
                detections = event_loop.run_until_complete(_detect_objects(frame))
                yield (frame, detections)
            except Exception as e:
                print("unable to detect features", e)
                _release_camara(camera)
                break
    _release_camara(camera)
