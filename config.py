#
# example configuration is now in config.ini.tmpl - copy to config.ini and change to your values
#
import configparser

# Initialize configparser
config = configparser.ConfigParser()

# Load configuration from external INI file
config.read('config.ini')

# Not here! # Prefix all variables with 'cfg.'
talkgroups = [int(x) for x in config.get('talkgroups', 'list').split(',')]
callsigns = config.get('callsigns', 'list').split(',')
noisy_calls = config.get('noisy_calls', 'list').split(',')
min_duration = int(config.get('min', 'duration'))
min_silence = int(config.get('min', 'silence'))
verbose = config.getboolean('verbose', 'enabled')
pushover = config.getboolean('pushover', 'enabled')
pushover_token = config.get('pushover', 'token')
pushover_user = config.get('pushover', 'user')
telegram = config.getboolean('telegram', 'enabled')
telegram_api_id = config.get('telegram', 'api_id')
telegram_api_hash = config.get('telegram', 'api_hash')
telegram_username = config.get('telegram', 'username')
phone = config.get('telegram', 'phone')
dapnet = config.getboolean('dapnet', 'enabled')
dapnet_user = config.get('dapnet', 'user')
dapnet_pass = config.get('dapnet', 'pass')
dapnet_url = config.get('dapnet', 'url')
dapnet_callsigns = config.get('dapnet', 'callsigns').split(',')
dapnet_txgroup = config.get('dapnet', 'txgroup')
discord = config.getboolean('discord', 'enabled')
discord_wh_url = config.get('discord', 'wh_url')

# Parse thread_map into a dictionary
thread_map = dict([x.split(':') for x in config.get('discord', 'thread_map').split(',')])

# Matrix configuration
matrix = config.getboolean('matrix', 'enabled')
matrix_homeserver = config.get('matrix', 'homeserver')
matrix_user_id = config.get('matrix', 'user_id')
matrix_access_token = config.get('matrix', 'access_token')
matrix_room_id = config.get('matrix', 'room_id')

