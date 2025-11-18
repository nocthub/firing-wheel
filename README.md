# 🐋 Firing Wheel: System Monitor & Manager Game

A fun, interactive Flask application that runs inside a Docker container. It combines real-time system resource monitoring (CPU, RAM, Disk) with a satirical "Manager's Wheel" game to "fire" employees, all wrapped in a Docker-themed UI.

## ✨ Features

* **Live System Monitoring:** Uses WebSockets (`flask-socketio`) to display real-time CPU, Memory, and Disk usage from inside the container.
* **The Manager's Wheel:** An interactive HTML5 canvas game where you input names and spin the wheel to randomly "fire" someone (with sound effects!).
* **Docker Integration:** Fully containerized with `Dockerfile` and `docker-compose` for easy deployment.
* **Stress Test:** Includes a feature to artificially stress the CPU cores to test the monitoring gauges.
* **Whale Animation:** Features an animated ASCII art whale and a "danger" mode UI.

## 🚀 Getting Started

### Prerequisites
* Docker and Docker Compose installed on your machine.

### Installation (The Easy Way)

1.  Clone the repository:
    ```bash
    git clone [https://github.com/nocthub/firing-wheel.git](https://github.com/nocthub/firing-wheel.git)
    cd firing-wheel
    ```

2.  Run with Docker Compose:
    ```bash
    docker-compose up -d --build
    ```

3.  Open your browser and visit:
    `http://localhost:5577`
    
### Installation (The Quick Way: Docker Pull)

If you have Docker installed, you can skip the building step and pull the ready image directly from Docker Hub:

1.  Pull the image:
    ```bash
    docker pull vandire/firing-wheel:latest
    ```

2.  Run the container:
    ```bash
    docker run -d -p 5577:5577 vandire/firing-wheel:latest
    ```

3.  Open your browser and visit:
    `http://localhost:5577`
### Manual Installation (Without Docker)

1.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
2.  Run the application:
    ```bash
    python app.py
    ```

## 📂 Project Structure

* `app.py`: The main Flask application containing the logic for WebSockets, the stress test, and the HTML rendering.
* `Dockerfile`: Instructions to build the Python 3.11 lightweight image.
* `docker-compose.yml`: Configuration to run the container and map port 5577.
* `static/`: Contains the sound effects (`spinning.mp3`, `win.mp3`, etc.).

## 🛠 Technologies Used

* **Backend:** Python, Flask, Flask-SocketIO, Psutil.
* **Frontend:** HTML5, CSS3 (Animations), JavaScript, Socket.io-client.
* **Containerization:** Docker.

## 📝 License

This project is open source and available under the [MIT License](LICENSE).
