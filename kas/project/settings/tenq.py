import json
import os

TENQ = {
    "host": os.environ["TENQ_HOST"],
    "port": int(os.environ.get("TENQ_PORT") or 22),
    "username": os.environ["TENQ_USER"],
    "password": os.environ["TENQ_PASSWORD"],
    "known_hosts": json.loads(os.environ.get("TENQ_KNOWN_HOSTS", "[]")),
    "dirs": {
        "10q_production": os.environ["TENQ_PROD_PATH"],
        "10q_development": os.environ["TENQ_TEST_PATH"],
    },
    "destinations": {
        "production": [
            "10q_production",
            "10q_development",
        ],  # Our prod server can use both prod and dev on the 10q server
        "development": [
            "10q_development",
            "10q_mocking",
        ],  # Our dev server can only use dev on the 10q server
        "staging": ["10q_development"],
    },
    "project_id": os.environ["TENQ_PROJECT_ID"],
}
