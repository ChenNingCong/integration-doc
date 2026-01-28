from flask import Flask, render_template, jsonify, request
import socket
import os
import deployment  # Assuming your original code is in deployment.py

app = Flask(__name__)

# Map services to their ports for status checking
SERVICES = {
    "Frontend": {"port": 3000, "launcher": deployment.setup_frontend, "folder": "forum-frontend"},
    "Gateway": {"port": 8080, "launcher": deployment.setup_gateway, "folder": "forum-gateway"},
    "Auth Service": {"port": 8001, "launcher": deployment.setup_auth_service, "folder": "forum-auth-service"},
    "User Service": {"port": 8002, "launcher": deployment.setup_user_service, "folder": "forum-user-service"},
    "PostReply Service": {"port": 8003, "launcher": deployment.setup_post_reply_service, "folder": "forum-post-reply-service"},
    "Message Service": {"port": 8004, "launcher": deployment.setup_message_service, "folder": "forum-message-service"},
    "History Service": {"port": 8005, "launcher": deployment.setup_history_service, "folder": "forum-history-service"},
    "File Service": {"port": 8006, "launcher": deployment.setup_file_service, "folder": "forum-file-service"},
    "Email Service": {"port": 8007, "launcher": deployment.setup_email_service, "folder": "forum-email-service"},
}

def check_port(port):
    # get a get request to localhost:port
    import requests
    try:
        response = requests.get(f'http://localhost:{port}', timeout=0.5)
        return True
    except requests.RequestException:
        return False

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/status')
def status():
    results = {}
    for name, info in SERVICES.items():
        results[name] = {"status": "Online" if check_port(info['port']) else "Offline", "port": info['port']}
    return jsonify(results)

@app.route('/api/sync', methods=['POST'])
def sync_repos():
    deployment.sync()
    return jsonify({"message": "Sync completed"})

@app.route('/api/kill-all', methods=['POST'])
def kill_all():
    deployment.kill_node_processes()
    return jsonify({"message": "All specified ports cleared"})

@app.route('/api/kill-service/<service_name>', methods=['POST'])
def kill_service(service_name):
    if service_name in SERVICES:
        deployment.kill_one_node_processes(SERVICES[service_name]["port"])
        return jsonify({"message": f"Killed {service_name} service."})
    return jsonify({"error": "Service not found"}), 404

def cleanup_logs(service_folder):
    import shutil
    shutil.rmtree(os.path.join("logs", service_folder), ignore_errors=True)

@app.route('/api/launch-all', methods=['POST'])
def launch_all_services():
    kill_all()
    for service_name, info in SERVICES.items():
        cleanup_logs(info.get("folder", ""))
        info["launcher"]()
    return jsonify({"message": "Launching all services..."})

@app.route('/api/launch/<service_name>', methods=['POST'])
def launch_service(service_name):
    if service_name in SERVICES:
        cleanup_logs(SERVICES[service_name].get("folder", ""))
        SERVICES[service_name]["launcher"]()
        return jsonify({"message": f"Launching {service_name}..."})
    return jsonify({"error": "Service not found"}), 404

if __name__ == "__main__":
    app.run(host="localhost", port=5000, debug=False)