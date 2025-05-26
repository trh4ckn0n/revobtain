from flask import Flask, render_template_string, jsonify
import subprocess
import threading
import time

app = Flask(__name__)

listener_thread = None
listener_active = False
listener_output = ""

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <title>trhacknon Reverse Shell Listener</title>
    <style>
        body { background-color: #0d0d0d; color: #00ff99; font-family: monospace; text-align: center; padding: 30px; }
        input, button { padding: 10px; margin: 10px; background: #111; color: #00ff99; border: 1px solid #00ff99; }
        .status { margin-top: 20px; border: 1px dashed #00ff99; padding: 10px; }
    </style>
</head>
<body>
    <h1>trhacknon Reverse Shell Listener</h1>
    <p>Lance un listener TCP (port 4444) et attends un shell distant.</p>
    <button onclick="startListener()">Démarrer le Listener</button>
    <div class="status" id="status">Statut : en attente...</div>
    <script>
        function startListener() {
            fetch("/start_listener")
                .then(response => response.json())
                .then(data => {
                    document.getElementById("status").innerText = "Statut : " + data.status;
                });
        }

        setInterval(() => {
            fetch("/listener_status")
                .then(response => response.json())
                .then(data => {
                    document.getElementById("status").innerText = "Statut : " + data.status;
                });
        }, 3000);
    </script>
</body>
</html>
'''

def run_listener():
    global listener_active, listener_output
    listener_active = True
    try:
        # On écoute en TCP via socat pour éviter les blocages Render
        cmd = ["socat", "TCP4-LISTEN:4444,reuseaddr,fork", "EXEC:/bin/bash"]
        listener_output = "En attente de connexion..."
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # On attend quelques secondes pour simuler l'attente d'un shell
        for i in range(20):
            if proc.poll() is not None:
                listener_output = "Shell terminé ou erreur."
                listener_active = False
                return
            time.sleep(1)

        listener_output = "Shell toujours actif. Probablement connecté."
    except Exception as e:
        listener_output = f"Erreur : {str(e)}"
    finally:
        listener_active = False

@app.route("/")
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route("/start_listener")
def start_listener():
    global listener_thread, listener_active, listener_output
    if not listener_active:
        listener_thread = threading.Thread(target=run_listener)
        listener_thread.start()
        return jsonify({"status": "Listener démarré..."})
    else:
        return jsonify({"status": "Listener déjà en cours..."})

@app.route("/listener_status")
def listener_status():
    return jsonify({"status": listener_output})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
