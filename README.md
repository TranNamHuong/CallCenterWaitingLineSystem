# Call Center Waiting Line System

A fairness-aware call center queue management application built with Streamlit, Python, and SQLite.

This project manages two different waiting lines in one dashboard:

- a standard FIFO queue for regular callers
- a VIP priority queue for premium callers

The goal is not only to prioritize VIP customers, but also to make sure standard callers are still handled fairly when wait time becomes too long.

## Project Goal

In a real call center, always serving VIP callers first can improve premium service quality, but it can also cause starvation for standard customers.

This system solves that problem by combining:

- queue simulation
- fairness-based dispatching
- live operator controls
- persistent local storage
- analytics for queue activity and call history

## Core Features

- Standard caller intake with FIFO ordering
- VIP caller intake with tier-based priority
- Dynamic VIP ranking using an effective priority score
- Fairness protection for standard callers
- Operator dispatch button for serving the next call
- Persistent storage for active calls and completed call history
- Real-time queue visibility in the dashboard
- Analytics charts for queue distribution and historical activity

## System Architecture

The project is organized into three main layers:

### 1. Frontend Layer

The frontend is built with Streamlit and is responsible for:

- page layout and styling
- caller intake forms
- queue tables and live status cards
- analytics charts and reporting panels

Main frontend files:

- `app.py`
- `Frontend/UI_components.py`
- `Frontend/charts.py`

### 2. Backend Layer

The backend handles queue logic and dispatch rules:

- standard FIFO queue operations
- VIP priority queue operations
- fairness enforcement between both queues
- queue restoration from database state

Main backend files:

- `Backend/Normal_Queue.py`
- `Backend/priority_queue_logic.py`
- `Backend/queue_manager.py`

### 3. Database Layer

The database layer uses SQLite for local persistence:

- storing currently waiting callers
- storing completed call logs
- reloading active queue data when the app starts again

Main database file:

- `Database/db_setup.py`

## Project Structure

```text
CallCenterWaitingLineSystem/
|-- app.py
|-- .gitignore
|-- README.md
|-- Backend/
|   |-- Normal_Queue.py
|   |-- priority_queue_logic.py
|   |-- queue_manager.py
|-- Database/
|   |-- call_center.db
|   |-- db_setup.py
|-- Frontend/
|   |-- UI_components.py
|   |-- charts.py
```

## Main File Responsibilities

- `app.py`
  Streamlit entry point. It configures the page, initializes the database, creates session state, and renders the Operations and Analytics tabs.

- `Backend/Normal_Queue.py`
  Implements the standard queue using FIFO behavior for regular callers.

- `Backend/priority_queue_logic.py`
  Implements the VIP linked-list priority queue and computes effective priority based on VIP level and waiting time.

- `Backend/queue_manager.py`
  Coordinates both queues, applies fairness rules, restores active queue data from SQLite, and decides which caller should be served next.

- `Database/db_setup.py`
  Creates database tables, writes active queue entries, moves served calls into call history, and loads history data for analytics.

- `Frontend/UI_components.py`
  Builds the operator dashboard, input forms, queue tables, status cards, and custom visual styling.

- `Frontend/charts.py`
  Generates analytics charts and summary views from stored call data.

## Queue Design

### Standard Queue

The standard queue follows classic FIFO behavior:

- the first standard caller added is the first one to be served
- positions are updated whenever a caller is added or removed

### VIP Queue

The VIP queue is priority-based:

- callers are ranked by VIP level
- waiting time increases the effective priority score over time
- higher score callers move ahead in the queue

VIP tiers currently used:

- `30` = Platinum VIP
- `20` = Gold VIP
- `10` = Silver VIP

## Fairness Logic

The fairness policy is the key part of this project.

Without fairness protection, the standard queue could be starved if VIP callers keep arriving.  
To avoid that, the backend uses two rules:

- allow at most `2` consecutive VIP calls
- if the first standard caller waits longer than `120 seconds`, prioritize the standard queue

This means the system still respects VIP urgency, but it does not let the standard line get ignored indefinitely.

## Dispatch Algorithm

When the operator clicks `Serve Next Call`, the system follows this logic:

1. Recalculate VIP ordering based on effective score
2. Check whether the standard queue must be protected by fairness rules
3. If fairness applies, serve the first standard caller
4. Otherwise, serve the highest-ranked VIP caller
5. Move the served caller from `active_calls` to `call_logs`
6. Update the dashboard state

## Example Fairness Scenario

Example:

1. Two VIP callers are served in a row
2. A standard caller is still waiting
3. On the next dispatch, the system serves the standard caller even if another VIP exists

Another example:

1. A standard caller waits more than `120` seconds
2. A new VIP caller joins with higher priority
3. The standard caller is still served next because fairness protection is triggered

## Database Design

The local SQLite database stores both live queue state and handled-call history.

### Table: `active_calls`

Used for callers who are still waiting:

- `id`
- `name`
- `customer_type`
- `call_type`
- `joined_at`
- `vip_level`

### Table: `call_logs`

Used for callers who have already been served:

- `id`
- `name`
- `customer_type`
- `call_type`
- `joined_at`
- `served_at`

## Data Flow

The data flow of the system is:

1. User enters caller data in the Streamlit sidebar
2. Frontend sends input to `queue_manager`
3. `queue_manager` writes the caller into SQLite using `db_setup.py`
4. Caller is inserted into either the standard queue or VIP queue in memory
5. Operator dispatches the next call
6. Served caller is removed from `active_calls`
7. Served caller is inserted into `call_logs`
8. Frontend refreshes queue tables, metrics, and analytics

## Analytics

The analytics tab helps visualize queue activity using Plotly charts.

Current analytics focus on:

- customer group distribution
- service type mix
- handled call history
- queue activity summaries

## Technology Stack

- Python
- Streamlit
- SQLite
- Pandas
- Plotly

## Local Setup

### Requirements

- Python 3.10 or newer is recommended
- Streamlit
- Pandas
- Plotly

### Install Dependencies

```bash
pip install streamlit pandas plotly
```

### Run The App

```bash
streamlit run app.py
```

After that, open the local URL shown in the terminal, usually:

```text
http://localhost:8501
```

## How To Use

1. Start the app with Streamlit
2. Add standard callers or VIP callers from the sidebar
3. Watch queue positions update in the Operations tab
4. Click `Serve Next Call` to process the next caller
5. Review queue balance and fairness behavior
6. Open the Analytics tab to inspect the stored history visually

## How To Test The 120-Second Fairness Rule

You can test the fairness threshold manually like this:

1. Add one standard caller
2. Add one or more VIP callers
3. Wait more than `120` seconds
4. Click `Serve Next Call`
5. The standard caller should be served before the VIP queue continues

You can also observe another fairness case:

1. Add multiple VIP callers
2. Add one standard caller
3. Serve two VIP callers
4. On the next dispatch, the standard caller should be selected

## Notes About Persistence

- The database is local to your machine
- Active callers are saved immediately when they are added
- Served callers are moved into call history immediately
- Restarting the app can restore waiting callers from `active_calls`

## Current Limitations

- The system is designed for single-operator local use
- The database is local SQLite, not a shared production database
- There is no authentication or role management yet
- There is no export feature for reports yet
- There is no automated test suite yet

## Future Improvements

- Add CSV or Excel export
- Add multi-operator simulation
- Add configurable fairness settings from the UI
- Add authentication and role-based access
- Add deployment-ready environment configuration
- Add automated unit and integration tests

## Summary

This project is a queue management system that demonstrates how priority service and fairness can exist together in one workflow.

It is useful as:

- a DSA or software engineering project
- a queue simulation demo
- a small Streamlit dashboard application
- a fairness-aware service system prototype
