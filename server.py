import os
from flask import Flask, request, jsonify

app = Flask(__name__)
ALLOWED_HWIDS = set()

@app.route('/check', methods=['POST'])
def check_hwid():
    data = request.json
    hwid = data.get('hwid')
    if hwid in ALLOWED_HWIDS:
        return jsonify({"status": "ok"})
    return jsonify({"status": "denied"})

@app.route('/add', methods=['POST'])
def add_hwid():
    data = request.json
    ALLOWED_HWIDS.add(data.get('hwid'))
    return jsonify({"status": "ok"})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5001))
    app.run(host='0.0.0.0', port=port)
