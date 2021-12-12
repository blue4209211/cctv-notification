from flask import Flask, render_template, Response
import cv2

from lib import messages
from lib import cctv
from lib import image_utils
import time

app = Flask(__name__)
send_message_time_delta = 10


def gen_frame_and_message():
    last_message_time = time.time()

    for frame, bodies, faces in cctv.get_feed():

        frame = image_utils.to_jpg(frame)
        yield (b"--frame\r\n" b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n")

        msg = "found face"
        if len(bodies) > 0:
            msg = "found body"
        if len(bodies) > 0 and len(faces) > 0:
            msg = "found body and face"

        if (
            len(faces) > 0 or len(bodies) > 0
        ) and time.time() - last_message_time > send_message_time_delta:
            try:
                messages.send_message(frame, msg)
            except Exception as e:
                print("unable to send message", e)
            last_message_time = time.time()


@app.route("/video_feed")
def video_feed():
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(
        gen_frame_and_message(), mimetype="multipart/x-mixed-replace; boundary=frame"
    )


@app.route("/")
def index():
    """Video streaming home page."""
    return render_template("index.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0")
