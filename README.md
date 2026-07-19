# Call Center Queue Control

A Streamlit-based call center dashboard with:

- a standard FIFO queue
- a VIP priority queue with aging
- a fairness policy between VIP and standard callers
- SQLite persistence for active callers and handled-call history
- live analytics and auto-refresh support

## Run

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Start the app:

```bash
streamlit run app.py
```

## Data Model

- `active_calls`: callers currently waiting in the queue
- `call_logs`: callers who have already been served

## Main Files

- `app.py`: Streamlit entry point
- `Frontend/UI_components.py`: dashboard UI and operator actions
- `Frontend/charts.py`: analytics visualizations
- `Backend/queue_manager.py`: fairness and queue coordination logic
- `Backend/Normal_Queue.py`: FIFO queue for standard callers
- `Backend/priority_queue_logic.py`: linked-list priority queue for VIP callers
- `Database/db_setup.py`: SQLite setup and persistence helpers
