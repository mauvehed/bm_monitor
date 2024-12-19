# adapt the following variables to your needs
talkgroups = [312752,98638] # Talkgroups to monitor, seperated by commas
callsigns = [] # Callsigns to monitor, seperated by commas
noisy_calls = [] # Noisy calls signs that will be ignored
min_duration = 0 # Min. duration of a QSO to qualify for a push notification
min_silence = 300 # Min. time in seconds after the last QSO before a new push notification will be send
verbose = True # Enable extra messages (console only)
thread_map = {
    "312752": "1319353057267683490",  # Replace with actual talkgroup and thread IDs
}

# Pushover configuration
pushover = False # Enable or disable notifications via Pushover
pushover_token = "1234567890" # Your Pushover API token
pushover_user = "abcdefghijklm" # Your Pushover user key

# Telegram configuration
telegram = False # Enable or disable notifications via Telegram
telegram_api_id = "1234567"
telegram_api_hash = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
telegram_username = "foo_bot"
phone = "+491234567890"

# DAPNet configuration
dapnet = False # Enable or disable notifications via dapnet
dapnet_user = "mycall"
dapnet_pass = "xxxxxxxxxxxxxxxxxxxx"
dapnet_url = 'http://www.hampager.de:8080/calls'
dapnet_callsigns = ["MYCALL"]
dapnet_txgroup = "dl-all"

# Discord Configuration
discord = True
discord_wh_url = 'https://discord.com/api/webhooks/1319099638170783784/6aLLten73sHzq9hiNGCptVIKTl4q39WgweuGfRyiYe6hn9FHKzDLb7VOdVi3W0V5ccAB'