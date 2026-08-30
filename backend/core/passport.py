from datetime import datetime, timezone
import hashlib
import hmac
import json
import os

def create_passport(project_name, analysis, verification):
    payload = {
        "project": project_name,
        "issued_at": datetime.now(timezone.utc).isoformat(),
        "score": analysis["score"]["score"],
        "status": analysis["score"]["label"],
        "project_type": analysis["project_type"]["type"],
        "runtime": analysis["runtime"],
        "verification": verification,
        "version": "1.0"
    }
    key = os.environ.get("RUNPROOF_SECRET_KEY","development-only-key").encode()
    body = json.dumps(payload, sort_keys=True, separators=(",",":")).encode()
    payload["signature"] = hmac.new(key, body, hashlib.sha256).hexdigest()
    return payload