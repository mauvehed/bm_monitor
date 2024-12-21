[![Dependabot Updates](https://github.com/mauvehed/bm_monitor/actions/workflows/dependabot/dependabot-updates/badge.svg)](https://github.com/mauvehed/bm_monitor/actions/workflows/dependabot/dependabot-updates) [![Docker Publish](https://github.com/mauvehed/bm_monitor/actions/workflows/docker-publish.yml/badge.svg)](https://github.com/mauvehed/bm_monitor/actions/workflows/docker-publish.yml) [![CodeQL](https://github.com/mauvehed/bm_monitor/actions/workflows/github-code-scanning/codeql/badge.svg)](https://github.com/mauvehed/bm_monitor/actions/workflows/github-code-scanning/codeql) [![Pylint](https://github.com/mauvehed/bm_monitor/actions/workflows/pylint.yml/badge.svg)](https://github.com/mauvehed/bm_monitor/actions/workflows/pylint.yml)

# Brandmeister Last Heard Monitor

Brandmeister Last Heard Monitor/Notifier

This Python script will listen to the Brandmeister Last Heard API endpoint for any callsign or Talkgroup (or both) that you configure and it will send you a notification when there is activity for those callsigns and/or talkgroups.

## Origins

##### Created by [mclemens/pyBMNotify](https://codeberg.org/mclemens/pyBMNotify) then forked/refactored by [n8acl/bm_monitor](https://github.com/n8acl/bm_monitor) and finally you are here: [mauvehed/bm_monitor](https://github.com/mauvehed/bm_monitor).

> This script is really just a refactoring using a newer socketIO python library from what the original pyBMNotify script was using. Brandmesiter updated the protocol that their API was using a few months ago and the old script did not support the newer protocol, so I just refactored the script for this newer protocol.
>
> The actual logic and guts of the script are still the same as the original pyBMNotify script that [Michael Clemens, DK1MI](https://qrz.is/) wrote and that is all HIS work. That is why this is a fork, not an original work. I wanted to make sure that was clear. I did not do the heavy lifting for this project, I just refactored the connection. Everything else is his work.
>
> -n8acl

This script is for use by Amateur Radio Operators only.

---

## Supported Services

This script will push a notification to the following services:

- Discord
- Telegram
- Pushover
- DAPNET

---

## Installation/Setup Instructions

[Click here to see the installation and setup steps](https://github.com/mauvehed/bm_monitor/blob/master/installation-setup.md). Then come back here. This is a bit of a long document, so read it all carefully.

---

## Change Log

- 12/20/2024 - Point Release 1.3.1 - Add TalkerAlias compatibility when posting to Discord

- 12/19/2024 - Minor Update Release 1.3 - Add functionality to post Discord messages to Threads

- 05/20/2024 - Minor Update Release 1.2 - Added Logic to handle multiple events from BM to correctly identify the event needed to send a notification message

- 12/23/2022 - Minor Update Release 1.1 - Fixed logic for ignoring Noisy calls (Callsigns to ignore)

- 07/12/2022 - Inital Release
