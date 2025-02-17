# FastAPI Websockets

A Python project demonstrating the integration of **FastAPI** with **WebSockets** to build real-time, bidirectional communication between clients and servers. This setup is ideal for applications requiring live updates, such as chat applications, live notifications, or real-time dashboards.

## Features

- **Real-Time Communication:** Establishes persistent connections between clients and servers, enabling instant data exchange.
- **FastAPI Integration:** Utilizes FastAPI's asynchronous capabilities for efficient handling of WebSocket connections.
- **Scalability:** Designed to handle multiple concurrent WebSocket connections effectively.

## Installation

1. **Clone the Repository:**

``` bash
   git clone https://github.com/alsaif1431/FastAPI-Websockets.git
   cd FastAPI-Websockets
```

## Usage
python -m venv venv
source venv/bin/activate  # On Windows, use 'venv\Scripts\activate'

pip install -r requirements.txt

## Run
uvicorn main:app --host 0.0.0.0 --port 8000


