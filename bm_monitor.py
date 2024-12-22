#!/usr/bin/env python3
#################################################################################

# Brandmeister Monitor
# Developed by: Michael Clemens, DK1MI
# Refactored by: Jeff Lehman, N8ACL
# Further Refactoring by: mauvehed, K0MVH
# Current Version: 1.3.2
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
logging.basicConfig(
    level=logging.DEBUG if cfg.verbose else logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler()  # Ensure logs are sent to stdout
    ]
)

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

logging.debug("Configuration loaded:")
logging.debug(f"pushover_token: {cfg.pushover_token}")
logging.debug(f"pushover_user: {cfg.pushover_user}")
logging.debug(f"discord_wh_url: {cfg.discord_wh_url}")
logging.debug(f"telegram_api_id: {cfg.telegram_api_id}")
logging.debug(f"telegram_api_hash: {cfg.telegram_api_hash}")
logging.debug(f"talkgroups: {cfg.talkgroups}")
logging.debug(f"callsigns: {cfg.callsigns}")
logging.debug(f"noisy_calls: {cfg.noisy_calls}")

#############################
##### Define Functions

# Handle graceful shutdown on Ctrl+C or SIGTERM
def signal_handler(sig, frame):
    """Handles system signal interrupts for graceful application shutdown.

    This function is designed to intercept system signals and perform a clean disconnection from the socket connection before terminating the application. It ensures that resources are properly released and the application exits smoothly.

    Args:
        sig (int): The signal number received.
        frame (frame): The current stack frame.

    Returns:
        None
    """
    logging.info("Shutting down gracefully...")
    sio.disconnect()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

# Send push notification via Pushover. Disabled if not configured in config.py
def push_pushover(msg):
    """Sends a notification to a Discord channel or thread via webhook.

    This function sends a message to a specified Discord webhook URL, with optional support for posting to a specific thread. It utilizes the discord-webhook library to execute the webhook request.

    Args:
        wh_url (str): The Discord webhook URL.
        msg (str): The message content to be sent.
        thread_id (str, optional): The thread ID for posting to a specific thread. Defaults to None.

    Returns:
        None
    """
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
    try:
        if thread_id:
            wh_url = f"{wh_url}?thread_id={thread_id}"
        webhook = DiscordWebhook(url=wh_url, content=msg)
        response = webhook.execute()
        logging.info("Discord notification sent.")
    except Exception as e:
        logging.error(f"Failed to send Discord notification: {e}")

# Send pager notification via DAPNET. Disabled if not configured in config.py
def push_dapnet(msg):
    """Sends a pager notification via the DAPNET (Digital Amateur Paging Network) service.

    This function sends an emergency text message to specified DAPNET callsigns and transmitter groups using the configured DAPNET credentials. It prepares a JSON payload and submits a POST request to the DAPNET API.

    Args:
        msg (str): The message content to be sent via DAPNET.

    Returns:
        None
    """
    dapnet_json = json.dumps({"text": msg, "callSignNames": cfg.dapnet_callsigns, "transmitterGroupNames": [cfg.dapnet_txgroup], "emergency": True})
    response = requests.post(cfg.dapnet_url, data=dapnet_json, auth=HTTPBasicAuth(cfg.dapnet_user,cfg.dapnet_pass))

# Construct the message to be sent
def construct_message(c):
    """Constructs a formatted message string for a transmission event.

    This function generates a human-readable description of a radio transmission, including details about the source, destination, time, and duration. It provides a comprehensive text representation of a communication event.

    Args:
        c (dict): A dictionary containing transmission details with keys including:
            - DestinationID
            - Stop
            - Start
            - TalkerAlias
            - SourceCall
            - SourceName
            - DestinationName

    Returns:
        str: A formatted message string describing the transmission event.
    """
    tg = c["DestinationID"]
    out = ""
    duration = c["Stop"] - c["Start"]
    # convert unix time stamp to human readable format
    time = dt.datetime.fromtimestamp(c["Start"], dt.timezone.utc).astimezone(ZoneInfo("US/Central")).strftime("%Y/%m/%d %H:%M")
    # construct text message from various transmission properties
    if c["TalkerAlias"]:
        out += c["TalkerAlias"] + ' was active on '
    else:
        out += c["SourceCall"] + ' (' + c["SourceName"] + ') was active on '
    if c["DestinationName"] != '':
        out += str(tg) + ' (' + c["DestinationName"] + ') at '
    else:
        out += str(tg) + ' at '
    out += time + ' (' + str(duration) + ' seconds) US/Central'
    logging.debug(f"Constructed message: {out}")
    return out

#############################
##### Define SocketIO Callback Functions

@sio.event
def connect():
    logging.info('Connection established with Brandmeister network.')

@sio.on("mqtt")
def on_mqtt(data):
    """Processes MQTT messages from the Brandmeister network and manages notification logic.

    This function handles incoming MQTT messages by evaluating communication events, tracking activity across talkgroups and callsigns, and triggering notifications based on configured criteria. It determines whether a communication event meets the notification requirements and dispatches messages through configured notification channels.

    Args:
        data (dict): A dictionary containing the MQTT payload with communication event details.

    Returns:
        None
    """
    call = json.loads(data['payload'])

    tg = call["DestinationID"]
    callsign = call["SourceCall"]
    talkeralias = call["TalkerAlias"]
    start_time = call["Start"]
    stop_time = call["Stop"]
    event = call["Event"]
    notify = False
    now = int(time.time())

    if cfg.verbose and callsign in cfg.noisy_calls:
        logging.info(f"Ignored noisy ham {callsign}")

    elif event == 'Session-Stop' and callsign != '':
        if cfg.verbose:
            if str(tg) in map(str, cfg.talkgroups):
                logging.debug(f"Processing event: Event={event}, Callsign={callsign}, Talkgroup={tg}")
        if callsign in cfg.callsigns:
            if callsign not in last_OM_activity:
                logging.debug(f"First activity recorded for {callsign}")
                last_OM_activity[callsign] = 9999999
            inactivity = now - last_OM_activity[callsign]
            logging.debug(f"Inactivity for {callsign}: {inactivity} seconds")
            if inactivity >= cfg.min_silence:
                if tg in cfg.talkgroups and stop_time > 0:
                    logging.debug(f"Activity matches monitored talkgroups: {tg}")
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
                    logging.info(f"Ignored activity in TG {tg} from {callsign}: last action {inactivity} seconds ago.")
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
                if cfg.verbose:
                    logging.info(f"Discord message {construct_message(call)} sent to thread {thread_id} for TG {tg}")

@sio.event
def disconnect():
    logging.warning('Disconnected from Brandmeister network.')

#############################
##### Main Program

sio.connect(url='https://api.brandmeister.network', socketio_path="/lh/socket.io", transports="websocket")
sio.wait()
