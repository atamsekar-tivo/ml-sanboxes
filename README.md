# ml-sandboxes

# Local ML Sandbox (Jupyter + TensorFlow + Data Science)

This project provides a local, configurable JupyterLab sandbox for machine learning and data science, inspired by managed cloud environments like Vertex AI Notebooks and Whizlabs.

## Features
- JupyterLab with Python 3.11, TensorFlow, pandas, numpy, matplotlib, scikit-learn, seaborn, xgboost, lightgbm
- ARM64/Apple Silicon and x86_64 compatible (tested on macOS)
- Configurable CPU, RAM, and time limit (via web UI)
- Persistent storage for notebooks and data (`./notebooks`)
- Secure, minimal Docker image (non-root user, no build tools left behind)
- Modern Flask web UI for launching/stopping the sandbox and monitoring status

## Quick Start

1. **Install [Docker Desktop](https://www.docker.com/products/docker-desktop/) for Mac/Windows/Linux.**
2. **Clone this repo:**
   ```sh
   git clone <your-repo-url>
   cd ml-sanboxes
   ```
3. **Install Flask for the web UI:**
   ```sh
   pip install flask
   ```
4. **Run the web UI launcher:**
   ```sh
   python ui_launcher.py
   ```
5. **Open the UI:**
   Visit [http://localhost:5000](http://localhost:5000) in your browser. Set CPU, RAM, and (optionally) a time limit, then launch or stop the sandbox with a button.
6. **Open JupyterLab:**
   Click the "Open JupyterLab" button in the UI, or visit [http://localhost:8888](http://localhost:8888).

## Running the UI Launcher

### Development (Debug Mode, uses default secret key)
To run in development mode (debug on, default secret key):
```sh
export FLASK_DEBUG=1
python ui_launcher.py
```

### Production (Debug Off, requires secret key)
To run in production (debug off, must set a strong secret key):
```sh
export FLASK_SECRET_KEY='your-strong-secret-key'
export FLASK_DEBUG=0
python ui_launcher.py
```

- If `FLASK_DEBUG` is not set or is `0`, the app will require `FLASK_SECRET_KEY` to be set, otherwise it will not start.
- Never use the default secret key in production.

## Configuration
- **CPU/RAM/Timeout:** Set via the web UI before launching.
- **Disk:** The `./notebooks` folder is mounted for persistent storage.
- **ML Libraries:** See the `Dockerfile` for the full list. Add more as needed.
- **User/Permissions:** Container runs as a non-root user matching your host UID/GID for safe file access.

## Dockerfile Highlights
- Based on `python:3.11-slim` for security and reproducibility
- Installs all major ML/data science libraries
- Removes build tools after install to minimize vulnerabilities
- Runs JupyterLab with no authentication, remote access, and correct permissions

## Web UI Features
- Modern, professional design (Flask + HTML/CSS)
- Launch/stop sandbox with resource controls
- Status and container details with color-coded indicators
- Time limit option: auto-stops the sandbox after the specified duration
- Robust error handling and user feedback

---

**Happy experimenting!**