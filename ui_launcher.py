import os
import subprocess
import socket
from flask import Flask, render_template, request, redirect, flash
import logging

app = Flask(__name__)
app.secret_key = 'ml-sandbox-secret-key'

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ml-sandbox-ui")

@app.route("/", methods=["GET"])
def index():
    status, status_class, container_details = get_status_and_details()
    return render_template(
        "ui_launcher.html",
        cpu=1.0,
        ram=3.5,
        timeout=0,
        status=status,
        status_class=status_class,
        container_details=container_details
    )

@app.route("/launch", methods=["POST"])
def launch():
    cpu = request.form.get("cpu", "1.0")
    ram = request.form.get("ram", "3.5")
    timeout = int(request.form.get("timeout", "0"))
    dockerfile_path = os.path.join(os.getcwd(), "Dockerfile")
    if not os.path.exists(dockerfile_path):
        flash("Error: Dockerfile not found in the project directory. Please add a Dockerfile to build the image.", "error")
        return redirect("/")
    # Check if port 8888 is in use
    if is_port_in_use(8888):
        flash("Error: Port 8888 is already in use. Please stop any running JupyterLab or free the port before launching.", "error")
        return redirect("/")
    # Remove any existing container
    remove_sandbox_container()
    # Build the image
    try:
        subprocess.check_output(["docker", "build", "-t", "ml-sandbox-jupyter-img", "."], stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        logger.error(f"Error building image: {e.output.decode()}")
        flash("Error building image. Please check the logs for details.", "error")
        return redirect("/")
    # Run the container
    try:
        subprocess.check_output([
            "docker", "run", "-d",
            "--name", "ml-sandbox-jupyter",
            "-p", "8888:8888",
            "-v", f"{os.getcwd()}/notebooks:/tf/notebooks",
            "--cpus", str(cpu),
            "--memory", f"{ram}G",
            "ml-sandbox-jupyter-img"
        ], stderr=subprocess.STDOUT)
        flash("Jupyter Sandbox launched successfully!", "success")
        # If timeout is set, schedule stop
        if timeout > 0:
            import threading, time
            def stop_later():
                try:
                    time.sleep(timeout * 60)
                    remove_sandbox_container()
                except Exception:
                    pass
            threading.Thread(target=stop_later, daemon=True).start()
    except subprocess.CalledProcessError as e:
        logger.error(f"Error launching sandbox: {e.output.decode()}")
        flash("Error launching sandbox. Please check the logs for details.", "error")
    return redirect("/")

@app.route("/stop", methods=["POST"])
def stop():
    success, _ = remove_sandbox_container()
    if success:
        flash("Sandbox stopped successfully!", "success")
    else:
        flash("Error stopping sandbox. Please check the logs for details.", "error")
    return redirect("/")

def get_status_and_details():
    try:
        out = subprocess.check_output(["docker", "ps", "-a", "--filter", "name=ml-sandbox-jupyter", "--format", "{{.Status}}|{{.Names}}|{{.ID}}"], encoding="utf-8")
        if not out.strip():
            return 'No container', 'status-unknown', ''
        line = out.strip().splitlines()[0]
        status, name, cid = line.split('|')
        if 'Up' in status:
            return 'Running', 'status-running', line
        elif 'Exited' in status:
            return 'Stopped', 'status-stopped', line
        elif 'Created' in status:
            return 'Created', 'status-building', line
        else:
            return status, 'status-unknown', line
    except Exception as e:
        return f'Error: {e}', 'status-unknown', ''

def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('127.0.0.1', port)) == 0

def remove_sandbox_container():
    try:
        subprocess.check_output(["docker", "rm", "-f", "ml-sandbox-jupyter"], stderr=subprocess.STDOUT)
        return True, None
    except subprocess.CalledProcessError as e:
        logger.error(f"Error removing container: {e.output.decode()}")
        return False, None

if __name__ == "__main__":
    app.run(port=5000, debug=True)
