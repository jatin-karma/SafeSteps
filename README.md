# 🛡️ SafeSteps

SafeSteps is a modern, AI-powered web platform designed to enhance women's and community safety. It helps users avoid unsafe areas, anonymously report incidents, view live crowdsourced heatmaps, and obtain AI-curated safety advice and weekly digests.

---

## 🚀 Key Features

- **Live Heatmap**: Interactive map visualizing safety levels, powered by time-of-day filtering.
- **Anonymous Reporting**: Simple, step-by-step reporting flow with integrated AI categorization and custom safety advice.
- **AI Safety Briefings**: Smart route narrations and weekly digests compiling safety highlights.
- **One-Tap SOS**: Direct emergency sharing of real-time GPS location via WhatsApp.

---

## 🛠️ Tech Stack

### Backend
- **Python / Flask**: Core application structure and API endpoint routing.
- **Firebase Admin SDK (Firestore)**: NoSQL database storage for incident logs.
- **python-dotenv**: Environment configuration manager.

### Frontend
- **HTML5 & Vanilla CSS**: Premium, responsive glassmorphism/dark UI styling using modern typography.
- **JavaScript (ES6+)**: Frontend application logic and real-time API integrations.
- **Leaflet.js & Leaflet.heat**: Mapping engine and heatmap rendering.
- **FontAwesome**: High-quality vector iconography.

### AI Capabilities
- **Featherless API**: 
  - `mistralai/Mistral-7B-Instruct-v0.3`: Classifies reports into safety categories, determines severity (1-10), and extracts advice.
  - `meta-llama/Llama-3.1-8B-Instruct`: Generates smart route briefs and safety tips.
- **Google Gemini API**:
  - `gemini-1.5-flash`: Formulates automated weekly community safety digests and identifies hotspots.

---

## ⚙️ Setup & Installation

### Prerequisites
- Python 3.10+
- A Google Gemini API Key
- A Featherless.ai API Key
- A Firebase Project (Firestore enabled)

### 1. Clone the Repository
```bash
git clone https://github.com/jatin-karma/SafeSteps.git
cd SafeSteps
```

### 2. Configure Virtual Environment
Create and activate a Python virtual environment:

**On Windows (Command Prompt/PowerShell):**
```powershell
python -m venv .venv
.\.venv\Scripts\activate
```

**On macOS/Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies
Install all required libraries using the pinned versions in `requirements.txt`:
```bash
pip install -r requirements.txt
```

### 4. Setup Environment Variables
Create a file named `.env` in the root directory and configure the following keys:
```env
FEATHERLESS_API_KEY=your_featherless_api_key
GEMINI_API_KEY=your_gemini_api_key

# Optional (If using Firebase Firestore database. Otherwise, it defaults to local memory storage):
FIREBASE_SERVICE_ACCOUNT=path/to/firebase-credentials.json
# Or add individual Firebase web configuration variables for frontend:
FIREBASE_API_KEY=your_firebase_api_key
FIREBASE_AUTH_DOMAIN=your_auth_domain
FIREBASE_PROJECT_ID=your_project_id
FIREBASE_STORAGE_BUCKET=your_storage_bucket
FIREBASE_MESSAGING_SENDER_ID=your_sender_id
FIREBASE_APP_ID=your_app_id
```

### 5. Run the Application
Start the Flask development server:
```bash
python app.py
```
Open [http://127.0.0.1:5000](http://127.0.0.1:5000) in your web browser.
