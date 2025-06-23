import os
import subprocess
import socket
from flask import Flask, render_template_string, request, redirect, flash
import logging

app = Flask(__name__)
app.secret_key = 'ml-sandbox-secret-key'

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ml-sandbox-ui")

TEMPLATE = """
<!DOCTYPE html>
<html lang='en'>
<head>
    <meta charset='UTF-8'>
    <meta name='viewport' content='width=device-width, initial-scale=1.0'>
    <title>ML Sandbox Launcher</title>
    <link href='https://fonts.googleapis.com/css?family=Roboto:400,700&display=swap' rel='stylesheet'>
    <style>
        body { font-family: 'Roboto', Arial, sans-serif; background: #f7f9fa; margin: 0; padding: 0; }
        .container { max-width: 700px; min-width: 350px; margin: 3em auto; background: #fff; border-radius: 16px; box-shadow: 0 4px 24px rgba(0,0,0,0.10); padding: 2.5em 2.5em; }
        h1 { text-align: center; color: #1a237e; margin-bottom: 2em; font-size: 2.2em; }
        .section { background: #f5f7fa; border-radius: 10px; box-shadow: 0 1px 6px rgba(0,0,0,0.06); padding: 2em 1.5em; margin-bottom: 2em; }
        .section-header { font-size: 1.2em; font-weight: 700; color: #1976d2; margin-bottom: 1.2em; letter-spacing: 0.01em; }
        .form-row { display: flex; flex-wrap: wrap; gap: 1.5em; margin-bottom: 1.2em; }
        .form-group { flex: 1 1 120px; min-width: 120px; }
        label { display: block; color: #333; font-weight: 500; margin-bottom: 0.4em; }
        input[type=number] { width: 100%; padding: 0.5em; border: 1px solid #bdbdbd; border-radius: 4px; font-size: 1em; }
        .btn { width: 100%; padding: 0.9em 0; background: #1976d2; color: #fff; border: none; border-radius: 6px; font-size: 1.1em; font-weight: 700; cursor: pointer; transition: background 0.2s; margin-top: 1em; }
        .btn:hover { background: #0d47a1; }
        .btn-danger { background: #d32f2f; }
        .btn-danger:hover { background: #b71c1c; }
        .status-box { background: #e3f2fd; color: #1565c0; border-radius: 7px; padding: 1.2em; margin-top: 2em; font-size: 1.08em; font-weight: 500; display: flex; align-items: center; gap: 0.9em; box-shadow: 0 1px 4px rgba(21,101,192,0.07); }
        .status-dot { width: 16px; height: 16px; border-radius: 50%; display: inline-block; }
        .status-running { background: #43a047; }
        .status-stopped { background: #d32f2f; }
        .status-building { background: #ffa000; }
        .status-unknown { background: #bdbdbd; }
        .container-details { background: #f5f5f5; color: #333; border-radius: 7px; padding: 1.2em; margin-top: 1.2em; font-size: 1em; overflow-x: auto; word-break: break-all; white-space: pre-wrap; box-shadow: 0 1px 4px rgba(0,0,0,0.06); }
        .footer { text-align: center; margin-top: 2.5em; color: #888; font-size: 1em; }
        .success { color: #388e3c; }
        .error { color: #d32f2f; }
        .flash { margin-top: 1em; text-align: center; font-weight: 500; }
        .jupyter-btn { display: inline-flex; align-items: center; gap: 0.7em; background: linear-gradient(90deg, #f37726 0%, #ffb74d 100%); border: none; border-radius: 7px; padding: 0.8em 2em; font-size: 1.1em; font-weight: 700; color: #fff; text-decoration: none; box-shadow: 0 2px 8px rgba(243,119,38,0.15); transition: background 0.2s, box-shadow 0.2s, transform 0.1s; margin-top: 1.5em; letter-spacing: 0.02em; }
        .jupyter-btn:hover { background: linear-gradient(90deg, #ff9800 0%, #f37726 100%); box-shadow: 0 4px 16px rgba(243,119,38,0.22); transform: translateY(-2px) scale(1.03); }
        .jupyter-logo { width: 32px; height: 32px; vertical-align: middle; background: #fff; border-radius: 50%; box-shadow: 0 1px 4px rgba(0,0,0,0.08); }
        @media (max-width: 600px) {
            .container { padding: 1.2em 0.5em; }
            .form-row { flex-direction: column; gap: 0.7em; }
            .btn, .btn-danger { font-size: 1em; }
        }
    </style>
</head>
<body>
    <div class='container'>
        <h1>ML Sandbox Launcher</h1>
        {% with messages = get_flashed_messages(with_categories=true) %}
          {% if messages %}
            {% for category, message in messages %}
              <div class='flash {{ category }}'>{{ message }}</div>
            {% endfor %}
          {% endif %}
        {% endwith %}
        <div class='section'>
            <div class='section-header'>Launch New Sandbox</div>
            <form method='post' action='/launch' aria-label='Launch ML Sandbox'>
                <div class='form-row'>
                    <div class='form-group'>
                        <label for='cpu'>CPU cores</label>
                        <input id='cpu' type='number' name='cpu' min='1' max='8' step='0.1' value='{{cpu}}'>
                    </div>
                    <div class='form-group'>
                        <label for='ram'>RAM (GB)</label>
                        <input id='ram' type='number' name='ram' min='1' max='32' step='0.1' value='{{ram}}'>
                    </div>
                    <div class='form-group'>
                        <label for='timeout'>Time Limit (minutes)</label>
                        <input id='timeout' type='number' name='timeout' min='0' max='1440' step='1' value='{{timeout}}' placeholder='0 (no limit)'>
                    </div>
                </div>
                <button class='btn' type='submit'>Launch Sandbox</button>
            </form>
        </div>
        <div class='section'>
            <div class='section-header'>Stop Running Sandbox</div>
            <form method='post' action='/stop' aria-label='Stop ML Sandbox'>
                <button class='btn btn-danger' type='submit'>Stop Sandbox</button>
            </form>
        </div>
        <div class='section'>
            <div class='section-header'>Status</div>
            <div class='status-box'>
                <span class='status-dot {{ status_class }}'></span>
                <span><strong>Status:</strong> {{status}}</span>
            </div>
            {% if container_details %}
            <div class='container-details'>
                <strong>Container Details:</strong><br>
                <pre style='background:none; border:none; padding:0; margin:0; color:#333; overflow-x:auto; word-break:break-all; white-space:pre-wrap;'>{{container_details}}</pre>
            </div>
            {% endif %}
        </div>
        <div style='margin-top:1.5em; text-align:center;'>
            <a class='jupyter-btn' href='http://localhost:8888' target='_blank'>
                <img class='jupyter-logo' src='/static/jupyterlab-logo.svg' alt='JupyterLab Logo' />
                Open JupyterLab
            </a>
        </div>
        <div class='footer'>
            &copy; 2025 ML Sandbox &mdash; Powered by Docker &amp; JupyterLab
        </div>
    </div>
</body>
</html>
"""

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

@app.route("/", methods=["GET"])
def index():
    status, status_class, container_details = get_status_and_details()
    return render_template_string(TEMPLATE, cpu=1.0, ram=3.5, timeout=0, status=status, status_class=status_class, container_details=container_details)

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

if __name__ == "__main__":
    debug_mode = os.getenv("FLASK_DEBUG", "False").lower() in ("true", "1", "t")
    app.run(port=5000, debug=debug_mode)
