#!/usr/bin/env python3
#################################################################################

# Brandmeister Monitor
# Developed by: Michael Clemens, DK1MI
# Refactored by: Jeff Lehman, N8ACL
# Further Refactoring by: mauvehed, K0MVH
# Now with even more refactoring!!! Each serving of BM Monitor now includes 10% more fiber! - AD0HW
# Current Version: 1.3.4 (with duplicate fix)
# Original Script: https://codeberg.org/mclemens/pyBMNotify
# Refactored Script: https://github.com/n8acl/bm_monitor
# Current Script: https://github.com/mauvehed/bm_monitor

#############################
##### Import Libraries and configs
import config as cfg
import json
import datetime as dt
import time
import socketio
import http.client, urllib
from zoneinfo import ZoneInfo
import logging
import signal
import sys

# Configure logging
logger = logging.getLogger("bm_logger")
logger.setLevel(logging.DEBUG)

# Handlers
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

file_handler = logging.FileHandler("bm_monitor.log", mode="w")
file_handler.setLevel(logging.DEBUG)

# Formatter
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
console_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)

logger.addHandler(console_handler)
logger.addHandler(file_handler)

# Conditional imports
if cfg.discord:
    from discord_webhook import DiscordWebhook

if cfg.dapnet or cfg.telegram:
    import requests
    from requests.auth import HTTPBasicAuth

#############################
##### Define Variables

sio = socketio.Client()
last_TG_activity = {}
last_OM_activity = {}
recent_calls = {}  # Changed to track {callsign: last_notification_time}

logger.info("Configuration loaded:")
logger.info(f"talkgroups: {cfg.talkgroups}")
logger.info(f"callsigns: {cfg.callsigns}")

#############################
##### Define Functions

def signal_handler(sig, frame):
    logger.info("Shutting down gracefully...")
    sio.disconnect()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

def push_pushover(msg):
    conn = http.client.HTTPSConnection("api.pushover.net:443")
    conn.request("POST", "/1/messages.json",
        urllib.parse.urlencode({
        "token": cfg.pushover_token,
        "user": cfg.pushover_user,
        "message": msg,
        }), { "Content-type": "application/x-www-form-urlencoded" })
    conn.getresponse()

def push_discord(wh_url, msg, thread_id=None):
    try:
        if thread_id:
            wh_url = f"{wh_url}?thread_id={thread_id}"
        webhook = DiscordWebhook(url=wh_url, content=msg)
        response = webhook.execute()
        logger.info("Discord notification sent.")
    except Exception as e:
        logger.error(f"Failed to send Discord notification: {e}")

def push_dapnet(msg):
    dapnet_json = json.dumps({"text": msg, "callSignNames": cfg.dapnet_callsigns, 
                            "transmitterGroupNames": [cfg.dapnet_txgroup], "emergency": True})
    response = requests.post(cfg.dapnet_url, data=dapnet_json, 
                           auth=HTTPBasicAuth(cfg.dapnet_user,cfg.dapnet_pass))

def construct_message(c):
    tg = c["DestinationID"]
    duration = c["Stop"] - c["Start"]
    time_str = dt.datetime.fromtimestamp(c["Start"], dt.timezone.utc).astimezone(
        ZoneInfo("US/Central")).strftime("%Y/%m/%d %H:%M")
    
    if c["TalkerAlias"]:
        out = f'{c["TalkerAlias"]} was active on '
    else:
        out = f'{c["SourceCall"]} ({c["SourceName"]}) was active on '
    
    out += f'{tg} ({c["DestinationName"]}) at {time_str} ({duration} seconds) US/Central'
    logger.info(f"Constructed message: {out}")
    return out

#############################
##### Define SocketIO Callback Functions

@sio.event
def connect():
    logger.info('Connection established with Brandmeister network.')

@sio.on("mqtt")
def on_mqtt(data):
    """Process MQTT messages with duplicate prevention"""
    call = json.loads(data['payload'])
    logger.debug(f"Received message: {json.dumps(call, indent=2)}")

    tg = call["DestinationID"]
    callsign = call["SourceCall"]
    event = call["Event"]
    now = int(time.time())
    notify = False

    if cfg.verbose and callsign in cfg.noisy_calls:
        logger.info(f"Ignored noisy ham {callsign}")
        return

    if event == 'Session-Stop' and callsign:
        # Cleanup old entries first
        expired = [call_sign for call_sign, t in recent_calls.items() 
                 if now - t > cfg.min_silence]
        for call_sign in expired:
            del recent_calls[call_sign]

        if callsign in cfg.callsigns:
            # Handle monitored callsigns
            inactivity = now - last_OM_activity.get(callsign, 0)
            if inactivity >= cfg.min_silence:
                notify = True
                last_OM_activity[callsign] = now
        elif tg in cfg.talkgroups:
            # Handle monitored talkgroups
            duration = call["Stop"] - call["Start"]
            if duration >= cfg.min_duration:
                last_activity = last_TG_activity.get(tg, 0)
                inactivity = now - last_activity
                
                # Check if we should notify
                call_is_new = callsign not in recent_calls
                silence_expired = (now - recent_calls.get(callsign, 0)) >= cfg.min_silence
                
                if call_is_new or silence_expired:
                    notify = True
                    recent_calls[callsign] = now  # Track notification time
                    last_TG_activity[tg] = now

        if notify:
            msg = construct_message(call)
            if cfg.pushover:
                push_pushover(msg)
            if cfg.discord:
                thread_id = cfg.thread_map.get(str(tg))
                push_discord(cfg.discord_wh_url, msg, thread_id=thread_id)
                if cfg.verbose:
                    logger.info(f"Sent to Discord: {msg}")

@sio.event
def disconnect():
    logger.warning('Disconnected from Brandmeister network.')

#############################
##### Main Program

if __name__ == "__main__":
    sio.connect(url='https://api.brandmeister.network', 
               socketio_path="/lh/socket.io", 
               transports="websocket")
    sio.wait()