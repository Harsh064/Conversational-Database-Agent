# 🧠 Conversational DB Agent

Chat with your **MongoDB** database using **natural language queries**! 

    - This AI-powered agent understands user queries from natural language

    - Convert user queries into MongoDB queries to extract requiered data from database

    - Use Agenetic Reasoning to returns insightful results.

---

## 🚀 Features

- 💬 Chat interface using `Streamlit`
- 🧠 Intent matching via semantic similarity search using `FAISS`.
- 🔌 Connects to MongoDB collections (`accounts`, `transactions`, `customers` from `sample_analytics` database)
- 🤖 Agent-based architecture using `LangChain`
- 📚 Sample question dataset for guided queries
- 🔎 Tools for structured DB retrieval: get customer tiers, accounts, transactions, etc.

---

## 📁 Project Structure

```
├── app.py                      # Streamlit frontend app
├── main.py                     # Core agent logic and tools
├── .env                        # MongoDB URI and credentials
├── requirements.txt            # Python dependencies
├── sample_questions.json       # Pre-defined sample questions for few shot learning
├── README.md                   # Project documentation (you are here)
```

---

## 🧰 Tools & Technologies

| Tool/Library           | Purpose                                |
|------------------------|----------------------------------------|
| `streamlit`            | UI framework for chat interface        |
| `langchain`            | LLM orchestration & agent framework    |
| `faiss-cpu`            | Vector search for intent similarity    |
| `pymongo`              | MongoDB connectivity                   |
| `google-generativeai` | LLM backend (e.g., Gemini)             |
| `langchain-community` | Integrations and utility tools         |
| `dotenv`               | Manage secrets and env variables       |

---

## ⚙️ Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/conversational-db-agent.git
cd conversational-db-agent
```

### 2. Install Dependencies

We recommend using a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

pip install -r requirements.txt
```

### 3. Configure Environment Variables

Create a `.env` file in the root directory:

```bash
MONGO_URI="your-mongodb-uri"
GOOGLE_API_KEY="your-generative-ai-key"
```

### 4. Run the App

```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`.

---

## 💡 Sample Questions

Sample questions are loaded from `sample_questions.json` to help agent to analyze different types of user’s  query intent. Examples:

- "Show me transactions greater than 1000 for account 328304."
- "List customer tiers and their benefits."
- "Retrieve all customers with '@gmail.com' email."

---

## 🧠 Example Tool Usage

```python
Tool(
    name="GetCustomersWithEmailDomain",
    func=lambda x: str(get_customers_with_email_domain(x)),
    description="List customers with a specific email domain"
)
```

This tool retrieves customers by email domain using a MongoDB projection like:

```python
db.customers.find(
    {"email": {"$regex": "@gmail.com$"}},
    {"username": 1, "email": 1, "_id": 0}
)
```

---

## 📌 Notes

- All MongoDB functions should follow the projection pattern:
  - `1` to **include** a field
  - `0` to **exclude** a field like `_id`
- Uses FAISS for top-`k` semantic search over intents

---


