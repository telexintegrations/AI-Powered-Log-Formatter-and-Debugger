# AI Log Analyzer

## 📌 Overview
**AI Log Analyzer** is an AI-powered log analysis service that categorizes logs, detects errors, and provides AI-generated suggestions for resolving issues. The system integrates with **Telex** for real-time log monitoring and supports **Slack notifications** for critical alerts.

## 🚀 Features
- **Real-time Log Processing**: Captures and analyzes logs as they are received.
- **AI-Powered Error Analysis**: Uses AI models OpenAI GPT-4 to detect errors and suggest fixes.
- **Log Categorization**: Automatically classifies logs into `INFO`, `WARNING`, and `ERROR`.
- **Slack Integration**: Sends alerts to Slack channels for quick issue resolution.
- **Database Storage**: Logs are stored for historical analysis and debugging.

## 🏗️ Architecture
1. **Receives logs** from Telex.
2. **Categorizes logs** into INFO, WARNING, or ERROR.
3. If enabled, **AI analyzes errors** and suggests solutions.
4. Optionally **sends alerts to Slack** for critical logs.
5. **Stores logs in a database** for later review.

## 📡 API Endpoints
### **Log Processing Endpoint**
```http
POST /telex/logs
```
#### **Request Body**
```json
{
  "message": "Database connection failed: timeout error",
  "settings": [
    { "label": "Enable AI Analysis", "value": "Yes" },
    { "label": "Send Alerts to Slack", "value": "Yes" }
  ]
}
```
#### **Response**
```json
{
  "original_message": "Database connection failed: timeout error",
  "category": "ERROR",
  "ai_suggestion": "Try increasing the database connection timeout setting and check network latency.",
  "processed_at": "2025-02-21T12:34:56Z"
}
```

## 🔧 Installation & Setup
### **1️⃣ Clone the Repository**
```bash
git clone https://github.com/telexintegrations/AI-Powered-Log-Formatter-and-Debugger.git
cd AI-Powered-Log-Formatter-and-Debugger
```
### **2️⃣ Create a Virtual Environment & Install Dependencies**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```
### **3️⃣ Set Up Environment Variables**
Create a `.env` file and configure:
```env
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/...
AI_MODEL_TYPE=OpenAI_GPT-4 
DATABASE_URL=postgresql://user:password@localhost/logs_db
```
### **4️⃣ Run the FastAPI Server**
```bash
uvicorn main:app --reload
```

## 📦 Deployment
To deploy on a cloud provider (e.g., **AWS, GCP, DigitalOcean, Render**):
1. **Containerize** the app using Docker.
2. Deploy using a service like **Kubernetes, AWS ECS, or DigitalOcean App Platform**.
3. Set up **CI/CD** for automatic deployments.

## 📊 Telex Integration Setup
1. **Log into Telex** and go to **Integrations > Create New Integration**.
2. Upload the `integration.json` specification (found in the repo).
3. Set `target_url` to your FastAPI endpoint (e.g., `https://AI-service.render.com/telex/logs`).
4. Save and enable the integration.

## 🛠️ Technologies Used
- **FastAPI** - Backend API framework
- **PostgreSQL** - Log storage database
- **OpenAI GPT-4** - AI-powered log analysis
- **Slack API** - Log alert notifications
- **Docker** - Containerization
- **Telex** - Log streaming and event handling

## 👥 Contributors
- **[Breeze Concept](https://github.com/breezeconcept)** - Lead Developer

## 📄 License
This project is licensed under the **MIT License**. See [LICENSE](LICENSE) for more details.

---
💡 **Have suggestions or want to contribute?** Open an issue or submit a pull request!

