from dotenv import load_dotenv

load_dotenv()

import os

telegram_api_id = os.environ.get("TELEGRAM_API_ID")
telegram_api_hash = os.environ.get("TELEGRAM_API_HASH")

# for cctv camera use rtsp://username:password@ip_address:554/user=username_password='password'_channel=channel_number_stream=0.sdp'
# for default use 0
cctv_camera = os.environ.get("CCTV_CAMERA", 0)
