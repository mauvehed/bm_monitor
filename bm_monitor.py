#!/usr/bin/env python3
#################################################################################

# Brandmeister Monitor
# Developed by: Michael Clemens, DK1MI
# Refactored by: Jeff Lehman, N8ACL
# Further Refactoring by: mauvehed, K0MVH
# Current Version: 1.3.3
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
import asyncio

# Configure logging
# Create a logger
logger = logging.getLogger("bm_logger")
logger.setLevel(logging.DEBUG)  # Capture all messages

# Create a handler for STDOUT (prints only INFO and above)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

# Create a handler for file (captures all DEBUG and above)
file_handler = logging.FileHandler("bm_monitor.log", mode="w") # 'w' clears the file on app start
file_handler.setLevel(logging.DEBUG)

# Formatter (optional)
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
console_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)

# Add handlers to logger
logger.addHandler(console_handler)
logger.addHandler(file_handler)

# library only needed if Discord is configured in config.py
if cfg.discord:
    from discord_webhook import DiscordWebhook

# libraries only needed if dapnet or telegram is configured in config.py
if cfg.dapnet or cfg.telegram:
    import requests
    from requests.auth import HTTPBasicAuth

# library only needed if Matrix is configured in config.py
if cfg.matrix:
    from nio import AsyncClient, AsyncClientConfig

#############################
##### Define Variables

sio = socketio.Client()

last_TG_activity = {}
last_OM_activity = {}

logger.info("Configuration loaded:")
logger.info(f"pushover_token: {cfg.pushover_token}")
logger.info(f"pushover_user: {cfg.pushover_user}")
logger.info(f"discord_wh_url: {cfg.discord_wh_url}")
logger.info(f"telegram_api_id: {cfg.telegram_api_id}")
logger.info(f"telegram_api_hash: {cfg.telegram_api_hash}")
logger.info(f"talkgroups: {cfg.talkgroups}")
logger.info(f"callsigns: {cfg.callsigns}")
logger.info(f"noisy_calls: {cfg.noisy_calls}")

# Initialize Matrix client if enabled
matrix_client = None
if cfg.matrix:
    matrix_client = AsyncClient(cfg.matrix_homeserver, cfg.matrix_user_id)
    matrix_client.access_token = cfg.matrix_access_token
    # Initialize Matrix client in async context
    async def init_matrix():
        try:
            await matrix_client.sync()
            logger.info("Matrix client initialized and synced")
        except Exception as e:
            logger.error(f"Failed to initialize Matrix client: {e}")
    
    # Run the initialization
    asyncio.run(init_matrix())

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
    logger.info("Shutting down gracefully...")
    if matrix_client:
        asyncio.run(matrix_client.close())
        logger.info("Matrix client closed")
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
        logger.info("Discord notification sent.")
    except Exception as e:
        logger.error(f"Failed to send Discord notification: {e}")

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

# Send notification to Matrix room
async def push_matrix(msg):
    """Send notification to a Matrix room.
    
    This function sends a message to a specified Matrix room using the matrix-nio client.
    
    Args:
        msg (str): The message content to be sent.
        
    Returns:
        None
    """
    try:
        if matrix_client:
            await matrix_client.room_send(
                room_id=cfg.matrix_room_id,
                message_type="m.room.message",
                content={
                    "msgtype": "m.text",
                    "body": msg
                }
            )
            logger.info("Matrix notification sent.")
    except Exception as e:
        logger.error(f"Failed to send Matrix notification: {e}")

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
    logger.info(f"Constructed message: {out}")
    return out

#############################
##### Define SocketIO Callback Functions

@sio.event
def connect():
    logger.info('Connection established with Brandmeister network.')

@sio.on("mqtt")
def on_mqtt(data):
    """Processes MQTT messages from the Brandmeister network and manages notification logic."""

    call = json.loads(data['payload'])

    # Log all messages received
    logger.debug(f"Received Brandmeister message: {json.dumps(call, indent=2)}")

    tg = call["DestinationID"]
    callsign = call["SourceCall"]
    start_time = call["Start"]
    stop_time = call["Stop"]
    event = call["Event"]
    notify = False
    now = int(time.time())

    if cfg.verbose and callsign in cfg.noisy_calls:
        logger.info(f"Ignored noisy ham {callsign}")

    elif event == 'Session-Stop' and callsign != '':
        if cfg.verbose:
            if str(tg) in map(str, cfg.talkgroups):
                logger.info(f"Processing event: Event={event}, Callsign={callsign}, Talkgroup={tg}")
        if callsign in cfg.callsigns:
            if callsign not in last_OM_activity:
                logger.info(f"First activity recorded for {callsign}")
                last_OM_activity[callsign] = 9999999
            inactivity = now - last_OM_activity[callsign]
            logger.info(f"Inactivity for {callsign}: {inactivity} seconds")
            if inactivity >= cfg.min_silence:
                if tg in cfg.talkgroups and stop_time > 0:
                    logger.info(f"Activity matches monitored talkgroups: {tg}")
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
                    logger.info(f"Ignored activity in TG {tg} from {callsign}: last action {inactivity} seconds ago.")
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
                    logger.info(f"Discord message {construct_message(call)} sent to thread {thread_id} for TG {tg}")
            if cfg.matrix:
                asyncio.run(push_matrix(construct_message(call)))

@sio.event
def disconnect():
    logger.warning('Disconnected from Brandmeister network.')

#############################
##### Main Program

sio.connect(url='https://api.brandmeister.network', socketio_path="/lh/socket.io", transports="websocket")
sio.wait()
