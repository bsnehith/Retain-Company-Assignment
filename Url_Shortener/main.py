import random
import string
from flask import Flask, request, jsonify, redirect, abort, render_template
from validators import url as is_valid_url
from app.storage import URLStorage

app = Flask(__name__)
storage = URLStorage()

def generate_short_code(length=6):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        long_url = request.form.get("url")
        if not is_valid_url(long_url):
            return render_template("form.html", error="Invalid URL")

        short_code = generate_short_code()
        while storage.get_url(short_code):
            short_code = generate_short_code()

        storage.add_url(long_url, short_code)
        short_url = request.host_url + short_code
        return render_template("form.html", short_url=short_url)

    return render_template("form.html")

@app.route("/api/shorten", methods=["POST"])
def shorten_url():
    data = request.get_json()
    if not data or "url" not in data:
        return jsonify({"error": "Missing 'url' in request"}), 400

    long_url = data["url"]
    if not is_valid_url(long_url):
        return jsonify({"error": "Invalid URL"}), 400

    short_code = generate_short_code()
    while storage.get_url(short_code):
        short_code = generate_short_code()

    storage.add_url(long_url, short_code)

    return jsonify({
        "short_code": short_code,
        "short_url": request.host_url + short_code
    }), 201

@app.route("/<short_code>", methods=["GET"])
def redirect_to_original(short_code):
    record = storage.get_url(short_code)
    if not record:
        abort(404, "Short URL not found")

    storage.increment_click(short_code)
    return redirect(record["url"])

@app.route("/api/stats/<short_code>", methods=["GET"])
def get_stats(short_code):
    record = storage.get_url(short_code)
    if not record:
        abort(404, "Short code not found")

    return jsonify({
        "url": record["url"],
        "clicks": record["clicks"],
        "created_at": record["created_at"]
    })

if __name__ == "__main__":
    app.run(debug=True)
