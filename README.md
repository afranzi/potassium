<div align="center">
  <img src="./docs/potassium-logo.png" alt="Potassium Logo" width="150">
  <h1>Potassium</h1>
  <p><b>The tool to manage Debezium Signalling with precision and elegance.</b></p>
  <p>
    <a href="#-purpose">Purpose</a> •
    <a href="#-key-features">Features</a> •
    <a href="#-tech-stack">Stack</a> •
    <a href="#-architecture">Architecture</a> •
    <a href="#-getting-started">Installation</a> •
    <a href="#-deployment">Deployment</a>
  </p>
</div>

---

## 🎯 Purpose

**Potassium** is a web application and service designed to simplify and control the powerful [Debezium Signalling](https://debezium.io/documentation/reference/stable/configuration/signalling.html) feature. The goal is to provide an intuitive user interface that allows data and engineering teams to:

* **Visualize and manage** all active Debezium connectors in a Kafka Connect cluster.
* **Explore the schemas** of tables captured by each connector.
* **Initiate incremental snapshots safely**, allowing filters only on indexed columns to ensure maximum performance of the source database.

The name "Potassium" (chemical symbol K) is a play on words with Kafka and Debezium, representing its role as an "essential element" or catalyst that triggers key processes in the ecosystem.

## ✨ Key Features

* **Centralized Dashboard:** Lists all Debezium connectors and their real-time status.
* **Schema Explorer:** Allows viewing columns and data types of any monitored table.
* **Index Identification:** Connects to the source database to identify which columns are indexed, a crucial feature for operational safety.
* **Safe Incremental Snapshots:** The UI only allows defining filters on indexed columns to prevent performance-degrading snapshots.
* **Modern & Reactive UI:** Built with the latest technologies for a smooth user experience.
* **Cloud-Native Ready:** Designed from the ground up to be deployed on Kubernetes via a Helm chart.

## 🧰 Tech Stack

Potassium uses a modern, high-performance stack:

| Component  | Technology            | Purpose                                      |
| :--------- | :-------------------- | :------------------------------------------- |
| **Frontend** | **Next.js (React)** | Framework for the user interface.          |
|            | **TypeScript** | Static typing for more robust code.        |
|            | **Tailwind CSS** | Rapid and maintainable utility-first styling.|
| **Backend** | **FastAPI (Python)** | High-performance API framework.            |
|            | **`uv`** | Ultra-fast package and environment manager. |
|            | **Pydantic** | Data validation and serialization.         |
| **Deployment** | **Docker** | Application containerization.              |
|            | **Kubernetes** | Container orchestration.                   |
|            | **Helm** | Management of Kubernetes deployments.      |

## 🏛️ Architecture

The application follows a simple microservices architecture, ideal for containerized deployments:

1.  **Frontend (Next.js):** A Single-Page Application (SPA) that runs in the user's browser and communicates exclusively with the backend via its REST API.
2.  **Backend (FastAPI):** The brain of the application. It is stateless and performs three main tasks:
    * Queries the **Kafka Connect** REST API for connector information.
    * Connects directly to **source databases** to fetch schema and index metadata.
    * Produces messages to a **Kafka topic** to send signals to Debezium.
3.  **Infrastructure (Kubernetes):** Both services are designed to run as independent deployments within a Kubernetes cluster, exposed through a single Ingress that routes traffic accordingly.

## 🚀 Getting Started

Follow these steps to get the Potassium environment up and running on your local machine.

### Prerequisites

Ensure you have the following installed:
* Git
* Node.js (v18+)
* Python (v3.9+) and `uv`
* Docker
* A local Kubernetes cluster (e.g., Minikube, Kind, Docker Desktop)
* `kubectl` and `helm`

### Installation

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/](https://github.com/)[YOUR_USERNAME]/potassium.git
    cd potassium
    ```

2.  **Set up the Backend:**
    ```bash
    cd backend
    uv venv           # Create the virtual environment
    source .venv/bin/activate # Activate the environment
    uv pip install -r requirements.txt # Install dependencies
    ```
    To run the backend in development mode:
    ```bash
    uvicorn app.main:app --reload
    ```
    The backend will be available at `http://127.0.0.1:8000`.

3.  **Set up the Frontend:**
    ```bash
    cd ../frontend
    npm install
    ```
    To run the frontend in development mode:
    ```bash
    npm run dev
    ```
    The frontend will be available at `http://localhost:3000`.

## 🚢 Deployment

Potassium is designed to be deployed on Kubernetes using the included Helm chart.

1.  **Build the Docker images:**
    From the project root, run:
    ```bash
    docker build -t potassium-backend:latest ./backend
    docker build -t potassium-frontend:latest ./frontend
    ```

2.  **Load the images into your local cluster:**
    If you use Minikube:
    ```bash
    minikube image load potassium-backend:latest
    minikube image load potassium-frontend:latest
    ```
    (Check the documentation for your local Kubernetes tool for the equivalent command).

3.  **Deploy with Helm:**
    First, review and adjust the parameters in `helm/potassium/values.yaml` to match your configuration. Then, deploy:
    ```bash
    helm upgrade --install potassium ./helm/potassium
    ```
    Helm will create all the necessary resources in your Kubernetes cluster.

## 🗺️ Roadmap

* [ ] **Authentication & Authorization:** Implement a login system to secure the application.
* [ ] **Support for More Signal Types:** Add support for other Debezium signals (e.g., schema changes, ad-hoc).
* [ ] **Logging & Auditing:** Keep a history of signals sent and who sent them.
* [ ] **Testing:** Add a suite of unit and integration tests.
* [ ] **CI/CD Pipeline:** Automate builds and deployments with GitHub Actions.

## 📜 License

Distributed under the MIT License. See `LICENSE` for more information.

<div align="center">
  <p>---</p>
  <p><em>Made with ❤️ to simplify life with Debezium.</em></p>
</div>