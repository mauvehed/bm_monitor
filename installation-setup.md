### Installation Steps

1. [Obtain API Keys/Webhook URL ](installation-setup.md#messaging-services)
2. [Install needed packages, clone Repo and install library dependencies](installation-setup.md#installing-the-script)
3. [Configure the script](installation-setup.md#configure-the-script)
4. [Run the Script](installation-setup.md#running-the-script)

---

### Messaging Services

Here we need to setup the service you want to send notifications to.

#### Discord Webhook URL

If you will be using Discord, you will need to configure a few pieces on your Discord server.

- Create a new text channel for the bot (I called mine #dmr-monitor).
- Go to the settings of your server and click on integrations (right click the server icon and go to server settings and then integrations).
- In the middle of the screen should be a button that says "Create Webhook". Click that.
- Give it a name (I used `BM Monitor` for mine) and select the new text channel you just created, or use an existing channel if you like.
- Click the "Copy Webhook URL" button at the bottom of the window. Paste this somewhere as you will need it here shortly again. (If you loose it, you can come back later after creation and click the Copy button again).
- Click "Save".
- _If posting to a thread_: Create a new thread in your chosen Channel for each TalkGroup you wish to send notifications to
- Right click and select _Copy Thread ID_. This value will go into your `config.ini`

Congrats! Your Webhook and Channel are ready.

#### Telegram

- If you plan on using Telegram:
  - You will need to first either create a Telegram bot or use an existing one you own. If this is your first bot, you can use the [steps here](https://core.telegram.org/bots#6-botfather) and talk to @BotFather to create your bot. You will need the bot token for the bot you are using/creating and this can also be obtained from talking to @BotFather.
  - You will also need your chatid. This can be obtained once your bot is up and running by sending a message to your bot and using the Telegram API by going to this url: [https://api.telegram.org/bot'API-access-token'/getUpdates?offset=0](https://api.telegram.org/bot<API-access-token>/getUpdates?offset=0) replacing 'API-access-token' with your bot access token you obtained in the previous step. You will see some json and you will be able to find your ID there in the From stanza.
  - Note that Influx DB provides some examples of what to look for in the above 2 steps. You can go to their page by [clicking here](https://docs.influxdata.com/kapacitor/v1.5/event_handlers/telegram/).

#### Pushover

- Pushover is a service that sends notifications to your phone, tablet and computer.
- **It is important to note that, while they have a free trial, it is a paid service. It is $4.99 for every platform you want to use it on after a 30 Day trial, but you only pay that $4.99 once for every platform you are using it on.**
- This is the only paid service that this app supports.
- While I am not advocating buying the service, I know that some people use it for other things already and it was an easy add to the program.
- More information about Pushover can be found [here](https://pushover.net/).
- To get your API keys for Pushover:
  - Log into your Pushover account.
  - Your User Key is the in the upper right hand corner of the screen there. Copy that someplace.
  - Next, you will need to register for an API key for Pushover to use the application with. Scroll to the bottom where it says "Your Applications" and click "Create and Application/API Token"
  - Give it a name, agree to the TOS and click create application.
  - On the next screen it shows you the API Key you will need. Copy that out and now you have the two pieces you need for message notifications to work with Pushover.

#### DAPNET

- To use you will need to have your DAPNET pager and Transmitter already setup and configured and working. You will need:
  - Your DAPNET Username
  - DAPNET Password
  - TX Group

## For more information about setting up your DAPNET credentials and getting signed up, you will need to go to [http://www.hampager.de](http://www.hampager.de). The site is in German and you will need to translate it, unless you speak German, in which case you won't.

### Installing the Script

The next step is installing the needed packages, cloning the repo to get the script and then installing the needed libraries for the script to work properly.

This is probably the easiest step to accomplish.

Please run the following commands on your server:

```bash
sudo apt-get update && sudo apt-get -y upgrade && sudo apt-get -y dist-upgrade

sudo apt-get install python3 python3-pip git screen

git clone https://github.com/mauvehed/bm_monitor.git

cd bm_monitor

pip3 install -r requirements.txt
```

**Notes:**

- Users may want to also consider tmux in lieu of screen as it is more modern and allows quoting of its escape character
- The pip3 may not fully succeed. If you're comfortable with bashing your python environment:
- pip3 install --upgrade --force-reinstall -r requirements.txt
- You are solely responsible for the health of your system.

_Conversion of these instructions to use a venv for change isolation would be most welcome._

---

## Configure the Script

Now that you have all of your keys/webhooks/what have you, let's configure the script.

Copy `config.tmpl` to a new file named `config.ini`. Open `config.ini` in your favorite text editor.

You should see something similiar:

```python
[talkgroups]
list = 123456,12345

[callsigns]
list = AB0CDE,A9BCD

[noisy_calls]
list = CD1E,A3ZE

[min]
duration = 0
silence = 300

[verbose]
enabled = False

[pushover]
enabled = False
token = 1234567890
user = abcdefghijklm

[telegram]
enabled = False
api_id = 1234567
api_hash = aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
username = foo_bot
phone = +491234567890

[dapnet]
enabled = False
user = mycall
pass = xxxxxxxxxxxxxxxxxxxx
url = http://www.hampager.de:8080/calls
callsigns = MYCALL
txgroup = dl-all

[discord]
enabled = False
wh_url = https://discord.com/api/webhooks/1234567890/abcdefghijklm
thread_map = 123456:12345678901234567890
```

Each section above contains what is needed for each service to operate. To enable sending to a service, you will need to set the service name from `False` to `True` and supply the needed keys/webhooks for that service.

---

## Running the Script

Once you have the config file edited, start the bot by typing the following:

```bash
screen -S bm_monitor
```

Then in the new window:

```bash
cd bm_monitor

python3 bm_monitor.py
```

Once that is done, hold `CTRL` and then tap `A` and then `D` to disconnect from the screen session. If something ever happens, you can reconnect to the session by typing:

```bash
screen -R bm_monitor
```

And see why it errored or quit. You will know it errored because it will send the error to whatever server you are using for notifications. This is useful if you need to contact me for support or want to restart the script.
