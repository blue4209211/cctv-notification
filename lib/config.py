from dotenv import load_dotenv

load_dotenv()

import os

telegram_api_id = os.environ.get("TELEGRAM_API_ID")
telegram_api_hash = os.environ.get("TELEGRAM_API_HASH")

# for cctv camera use rtsp://username:password@ip_address:554/user=username_password='password'_channel=channel_number_stream=0.sdp'
# for default use 0
cctv_camera = os.environ.get("CCTV_CAMERA", 0)

motion_min_area = os.environ.get("MOTION_MIN_AREA", 4000)
motion_delta_thresh = os.environ.get("MOTION_DELTA_THRESHOLD", 5)
motion_min_frames = os.environ.get("MOTION_MIN_FRAMES", 8)
