#################################################################################

# Brandmeister Monitor
# Developed by: Michael Clemens, DK1MI
# Refactored by: Jeff Lehman, N8ACL
# Further Refactoring by: mauvehed, K0MVH
# Current Version: 1.3 (Threading Support Added)
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

# library only needed if Discord is configured in config.py
if cfg.discord:
    from discord_webhook import DiscordWebhook

# libraries only needed if dapnet or telegram is configured in config.py
if cfg.dapnet or cfg.telegram:
    import requests
    from requests.auth import HTTPBasicAuth

#############################
##### Define Variables

sio = socketio.Client()

last_TG_activity = {}
last_OM_activity = {}

#############################
##### Define Functions

# Send push notification via Pushover. Disabled if not configured in config.py
def push_pushover(msg):
    conn = http.client.HTTPSConnection("api.pushover.net:443")
    conn.request("POST", "/1/messages.json",
        urllib.parse.urlencode({
        "token": cfg.pushover_token,
        "user": cfg.pushover_user,
        "message": msg,
        }), { "Content-type": "application/x-www-form-urlencoded" })
    conn.getresponse()

# Send notification to Discord Channel or Thread via webhook
def push_discord(wh_url, msg, thread_id=None):
    """
    Send notification to Discord Channel or Thread via webhook
    :param wh_url: Discord webhook URL
    :param msg: Message content
    :param thread_id: Optional thread ID for posting to a specific thread
    """
    if thread_id:
        wh_url = f"{wh_url}?thread_id={thread_id}"
    webhook = DiscordWebhook(url=wh_url, content=msg)
    response = webhook.execute()

# Send pager notification via DAPNET. Disabled if not configured in config.py
def push_dapnet(msg):
    dapnet_json = json.dumps({"text": msg, "callSignNames": cfg.dapnet_callsigns, "transmitterGroupNames": [cfg.dapnet_txgroup], "emergency": True})
    response = requests.post(cfg.dapnet_url, data=dapnet_json, auth=HTTPBasicAuth(cfg.dapnet_user,cfg.dapnet_pass))

# Construct the message to be sent
def construct_message(c):
    tg = c["DestinationID"]
    out = ""
    duration = c["Stop"] - c["Start"]
    # convert unix time stamp to human readable format
    time = dt.datetime.fromtimestamp(c["Start"], dt.timezone.utc).astimezone(ZoneInfo("US/Central")).strftime("%Y/%m/%d %H:%M")
    # construct text message from various transmission properties
    out += c["SourceCall"] + ' (' + c["SourceName"] + ') was active on '
    out += str(tg) + ' (' + c["DestinationName"] + ') at '
    out += time + ' (' + str(duration) + ' seconds) US/Central'
    # finally return the text message
    return out

#############################
##### Define SocketIO Callback Functions

@sio.event
def connect():
    print('connection established')

@sio.on("mqtt")
def on_mqtt(data):
    call = json.loads(data['payload'])

    tg = call["DestinationID"]
    callsign = call["SourceCall"]
    start_time = call["Start"]
    stop_time = call["Stop"]
    event = call["Event"]
    notify = False
    now = int(time.time())

    if cfg.verbose and callsign in cfg.noisy_calls:
        print("ignored noisy ham " + callsign)

    elif event == 'Session-Stop' and callsign != '':
        if callsign in cfg.callsigns:
            if callsign not in last_OM_activity:
                last_OM_activity[callsign] = 9999999
            inactivity = now - last_OM_activity[callsign]
            if callsign not in last_OM_activity or inactivity >= cfg.min_silence:
                if tg in cfg.talkgroups and stop_time > 0:
                    last_TG_activity[tg] = now
                last_OM_activity[callsign] = now
                notify = True
        elif tg in cfg.talkgroups and stop_time > 0:
            if tg not in last_TG_activity:
                last_TG_activity[tg] = 9999999
            inactivity = now - last_TG_activity[tg]
            duration = stop_time - start_time
            if duration >= cfg.min_duration:
                if tg not in last_TG_activity or inactivity >= cfg.min_silence:
                    notify = True
                elif cfg.verbose:
                    print("ignored activity in TG " + str(tg) + " from " + callsign + ": last action " + str(inactivity) + " seconds ago.")
                last_TG_activity[tg] = now

        if notify:
            if cfg.pushover:
                push_pushover(construct_message(call))
            if cfg.telegram:
                push_telegram({'text': construct_message(call), 'chat_id': cfg.telegram_api_id, "disable_notification": True})
            if cfg.dapnet:
                push_dapnet(construct_message(call))
            if cfg.discord:
                thread_id = cfg.thread_map.get(str(tg))  # Fetch thread ID for the talkgroup
                push_discord(cfg.discord_wh_url, construct_message(call), thread_id=thread_id)

@sio.event
def disconnect():
    print('disconnected from server')

#############################
##### Main Program

sio.connect(url='https://api.brandmeister.network', socketio_path="/lh/socket.io", transports="websocket")
sio.wait()
