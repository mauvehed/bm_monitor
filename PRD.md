# Product Requirements Document: Brandmeister Last Heard Monitor

## 1. Introduction

### 1.1 Purpose

This document outlines the functional and non-functional requirements for the Brandmeister Last Heard Monitor (`bm_monitor`) project.

### 1.2 Project Goal

The primary goal of `bm_monitor` is to monitor the Brandmeister Amateur Radio network's Last Heard API endpoint for specific user-configured activity (callsigns and/or Talkgroups) and notify the user via various supported messaging platforms when such activity is detected.

### 1.3 Target Audience

The intended users for this application are licensed Amateur Radio Operators who utilize the Brandmeister DMR network.

## 2. Functional Requirements

### 2.1 Core Monitoring

- **FR1**: The system MUST connect to the Brandmeister Last Heard API endpoint using the Socket.IO protocol.
- **FR2**: The system MUST listen for real-time transmission events broadcast by the API.
- **FR3**: The system MUST correctly parse incoming event data to extract relevant information such as Source Call, Destination ID (Talkgroup), Timestamp, etc.
- **FR4**: The system MUST include logic to handle potentially multiple events emitted by Brandmeister for a single transmission and correctly identify the specific event required to trigger a notification.

### 2.2 Configuration

- **FR5**: Users MUST be able to configure one or more specific Amateur Radio callsigns to monitor.
- **FR6**: Users MUST be able to configure one or more specific Brandmeister Talkgroup IDs to monitor.
- **FR7**: Users MAY configure the system to monitor for _either_ callsigns _or_ Talkgroups, _or both_ simultaneously.
- **FR8**: Users MUST be able to configure the credentials/API keys required for the selected notification services.
- **FR9**: Users MUST be able to configure a list of callsigns whose transmissions should be ignored (i.e., not trigger notifications).

### 2.3 Notification Services

The system MUST support sending notifications to the following platforms:

- **FR10**: **Discord**
  - **FR10.1**: Notifications MUST include relevant transmission details (e.g., Source Callsign, Destination Talkgroup, Time).
  - **FR10.2**: The system MUST optionally utilize the TalkerAlias information provided by Brandmeister within the Discord notification.
  - **FR10.3**: The system MUST optionally allow posting notifications within Discord Threads for configured channels.
- **FR11**: **Telegram**
  - **FR11.1**: Notifications MUST include relevant transmission details.
- **FR12**: **Pushover**
  - **FR12.1**: Notifications MUST include relevant transmission details.
- **FR13**: **DAPNET (Decentralized Amateur Paging Network)**
  - **FR13.1**: Notifications MUST include relevant transmission details formatted appropriately for DAPNET.

### 2.4 Filtering & Logic

- **FR14**: The system MUST check incoming events against the user-configured callsign(s) and/or Talkgroup(s).
- **FR15**: The system MUST trigger a notification _only_ if an event matches the configured criteria AND is _not_ from a callsign on the ignore list.
- **FR16**: The system MUST implement the refined logic (as per release 1.2) to correctly identify the necessary event when multiple events are received from Brandmeister close together.

### 2.5 Logging

- **FR17**: The system MUST provide standard application logging for operational status, warnings, and errors.
- **FR18**: The system MUST provide a separate, detailed debug log file (`bm_logging.py`) containing _all_ messages received from the Brandmeister API for troubleshooting purposes.

## 3. Non-Functional Requirements

### 3.1 Reliability

- **NFR1**: The system should maintain a persistent and stable connection to the Brandmeister API.
- **NFR2**: The system should reliably send notifications when configured trigger conditions are met.
- **NFR3**: The system should handle potential API connection errors or disruptions gracefully (e.g., attempt reconnection).

### 3.2 Usability

- **NFR4**: Configuration should be clear and manageable, likely through a dedicated configuration file.
- **NFR5**: Setup and installation instructions MUST be provided and easy to follow (referencing `installation-setup.md`).

### 3.3 Maintainability

- **NFR6**: The codebase should be structured logically, leveraging appropriate libraries (e.g., the updated `socketIO` library).

## 4. Future Considerations (Out of Scope for Current Definition)

_(This section can be used later to track potential feature ideas)_

- Support for additional notification platforms.
- Web-based UI for configuration.
- Statistical analysis of monitored activity.
