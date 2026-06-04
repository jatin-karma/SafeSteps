import json
import os
import re
from datetime import datetime, timezone

import requests
from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request
from flask_cors import CORS

try:
    import firebase_admin
    from firebase_admin import credentials, firestore
except Exception:
    firebase_admin = None
    credentials = None
    firestore = None

try:
    import google.generativeai as genai
except Exception:
    genai = None


load_dotenv()

app = Flask(__name__)
CORS(app)

FEATHERLESS_BASE_URL = "https://api.featherless.ai/v1"
FEATHERLESS_API_KEY = os.getenv("FEATHERLESS_API_KEY") or os.getenv("FEATHER_API_KEY", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

LOCAL_INCIDENTS = []


def init_firestore():
    if firebase_admin is None:
        return None

    if firebase_admin._apps:
        return firestore.client()

    cred_path = os.getenv("FIREBASE_SERVICE_ACCOUNT") or os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    try:
        if cred_path and os.path.exists(cred_path):
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred)
        else:
            firebase_admin.initialize_app()
        return firestore.client()
    except Exception as exc:
        print(f"Firestore disabled: {exc}")
        return None


db = init_firestore()


def now_iso():
    return datetime.now(timezone.utc).isoformat()


def strip_json_fences(text):
    if not text:
        return ""
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"\s*```$", "", cleaned)
    start = cleaned.find("{")
    end = cleaned.rfind("}")
    if start != -1 and end != -1 and end > start:
        return cleaned[start : end + 1]
    return cleaned


def safe_json_parse(text, fallback):
    try:
        return json.loads(strip_json_fences(text))
    except Exception:
        return fallback


def featherless_chat(model, prompt):
    if not FEATHERLESS_API_KEY:
        raise RuntimeError("Missing Featherless API key")

    headers = {
        "Authorization": f"Bearer {FEATHERLESS_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": "Respond with JSON only."},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.4,
    }
    response = requests.post(
        f"{FEATHERLESS_BASE_URL}/chat/completions",
        headers=headers,
        json=payload,
        timeout=30,
    )
    response.raise_for_status()
    data = response.json()
    return data["choices"][0]["message"]["content"]


def store_incident(payload):
    incident = {
        "lat": payload.get("lat"),
        "lng": payload.get("lng"),
        "category": payload.get("category"),
        "severity": payload.get("severity"),
        "time_risk": payload.get("time_risk"),
        "short_label": payload.get("short_label"),
        "advice": payload.get("advice"),
        "description": payload.get("description"),
        "timestamp": payload.get("timestamp") or now_iso(),
        "time": payload.get("time"),
        "date": payload.get("date"),
        "source": payload.get("source", "api"),
    }

    if db:
        db.collection("incidents").add(incident)
    else:
        LOCAL_INCIDENTS.append(incident)

    return incident


def get_all_incidents():
    if db:
        docs = db.collection("incidents").stream()
        return [doc.to_dict() for doc in docs]
    return list(LOCAL_INCIDENTS)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/map")
def map_page():
    return render_template("map.html")


@app.route("/report")
def report():
    return render_template("report.html")


@app.route("/route")
def route_page():
    return render_template("route.html")


@app.route("/digest")
def digest():
    return render_template("digest.html")


@app.route("/api/classify-incident", methods=["POST"])
def classify_incident():
    payload = request.get_json(silent=True) or {}
    description = payload.get("description", "")
    time_context = payload.get("time", "")

    prompt = (
        "You are a women's safety incident classifier.\n"
        "Analyze this report and respond ONLY in JSON with no extra text:\n"
        f"Report: {description}\n"
        f"Time: {time_context}\n"
        "Return: { category, severity (1-10), time_risk, short_label, advice }"
    )

    fallback = {
        "category": "other",
        "severity": 5,
        "time_risk": "always",
        "short_label": "General concern",
        "advice": "Stay in well-lit areas and share your location.",
    }

    try:
        content = featherless_chat("mistralai/Mistral-7B-Instruct-v0.3", prompt)
        result = safe_json_parse(content, fallback)
    except Exception as exc:
        print(f"Classification error: {exc}")
        result = fallback

    incident = {
        "lat": payload.get("lat"),
        "lng": payload.get("lng"),
        "description": description,
        "time": payload.get("time"),
        "date": payload.get("date"),
        "timestamp": now_iso(),
        "category": result.get("category"),
        "severity": result.get("severity"),
        "time_risk": result.get("time_risk"),
        "short_label": result.get("short_label"),
        "advice": result.get("advice"),
        "source": "classify",
    }

    store_incident(incident)
    return jsonify(result)


@app.route("/api/narrate-route", methods=["POST"])
def narrate_route():
    payload = request.get_json(silent=True) or {}
    start = payload.get("start", "")
    end = payload.get("end", "")
    incidents = payload.get("incidents", [])

    incident_list = json.dumps(incidents, ensure_ascii=False)
    prompt = (
        "You are a women's safety advisor.\n"
        f"Student traveling from {start} to {end}.\n"
        f"Incidents along route: {incident_list}\n"
        "Write a 3-4 sentence safety briefing.\n"
        "Respond ONLY in JSON: { narration, risk_score (1-10), tip }"
    )

    fallback = {
        "narration": "This route is generally safe, but stay alert near quieter streets."
        " Keep to well-lit paths and avoid isolated shortcuts at night.",
        "risk_score": 4,
        "tip": "Share your live location with a friend before you leave.",
    }

    try:
        content = featherless_chat("meta-llama/Llama-3.1-8B-Instruct", prompt)
        result = safe_json_parse(content, fallback)
    except Exception as exc:
        print(f"Narration error: {exc}")
        result = fallback

    return jsonify(result)


@app.route("/api/weekly-digest", methods=["POST"])
def weekly_digest():
    payload = request.get_json(silent=True) or {}
    incidents = payload.get("incidents", [])

    summary = json.dumps(incidents, ensure_ascii=False)
    prompt = (
        "You are a campus safety coordinator.\n"
        f"This week's incidents: {summary}\n"
        "Write a 3-4 sentence community digest.\n"
        "Respond ONLY in JSON: { digest, hotspot, tip, total, night_count }"
    )

    fallback = {
        "digest": "Reports were concentrated near parking areas and quieter lanes this week."
        " Students are encouraged to travel in pairs after dark.",
        "hotspot": "Main Gate",
        "tip": "Use well-lit paths and keep someone informed of your route.",
        "total": len(incidents),
        "night_count": sum(1 for item in incidents if str(item.get("time_risk")) in ("night_only", "evening_night")),
    }

    if not genai or not GEMINI_API_KEY:
        return jsonify(fallback)

    try:
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)
        result = safe_json_parse(response.text, fallback)
    except Exception as exc:
        print(f"Digest error: {exc}")
        result = fallback

    return jsonify(result)


@app.route("/api/incidents", methods=["GET"])
def list_incidents():
    return jsonify(get_all_incidents())


@app.route("/api/submit-incident", methods=["POST"])
def submit_incident():
    payload = request.get_json(silent=True) or {}
    payload["timestamp"] = payload.get("timestamp") or now_iso()
    payload["source"] = payload.get("source", "submit")
    incident = store_incident(payload)
    return jsonify({"status": "ok", "incident": incident})


@app.route("/api/firebase-config", methods=["GET"])
def firebase_config():
    return jsonify({
        "apiKey": os.getenv("FIREBASE_API_KEY", ""),
        "authDomain": os.getenv("FIREBASE_AUTH_DOMAIN", ""),
        "projectId": os.getenv("FIREBASE_PROJECT_ID", ""),
        "storageBucket": os.getenv("FIREBASE_STORAGE_BUCKET", ""),
        "messagingSenderId": os.getenv("FIREBASE_MESSAGING_SENDER_ID", ""),
        "appId": os.getenv("FIREBASE_APP_ID", ""),
        "measurementId": os.getenv("FIREBASE_MEASUREMENT_ID", "")
    })


if __name__ == "__main__":
    app.run(debug=True)