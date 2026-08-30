from backend.app import app
import os, socket


def local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

if __name__ == "__main__":
    host = os.environ.get("RUNPROOF_HOST", "0.0.0.0")
    port = int(os.environ.get("RUNPROOF_PORT", "8000"))
    print("\n==========================================")
    print("              RUNPROOF")
    print("==========================================")
    print(f"This laptop : http://127.0.0.1:{port}")
    print(f"Same Wi-Fi  : http://{local_ip()}:{port}")
    print("Keep this terminal open while RunProof is running.")
    print("==========================================\n")
    app.run(host=host, port=port, debug=False)
