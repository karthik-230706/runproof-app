from backend.app import create_app
from backend.config import Config

app = create_app()

if __name__ == '__main__':
    cfg = Config.load()
    app.run(host=cfg.host, port=cfg.port, debug=cfg.debug)
