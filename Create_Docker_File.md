# 🐳 Dockerizing the Conversational DB Agent

This guide walks you through creating a `Dockerfile` and containerizing your Streamlit-based Conversational Database Agent app for easy deployment.

---

## 📁 Project Structure (Before Dockerization)

Ensure your directory looks like this:


```
├── app.py                      # Streamlit frontend app
├── main.py                     # Core agent logic and tools
├── .env                        # MongoDB URI KEY and LLM API KEY
├── requirements.txt            # Python dependencies
├── sample_questions.json       # Pre-defined sample questions for few shot learning
├── README.md                   # Project documentation (you are here)
├── Dockerfile                  # (we will create this)
```
---


---

## 🪛 Step-by-Step Dockerization

### ✅ Step 1: Create a `Dockerfile`

In the root directory, create a file named `Dockerfile` with the following content:

```Dockerfile
# Use official Python image as base
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory inside container
WORKDIR /app

# Copy project files to container
COPY . /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Expose the port Streamlit uses
EXPOSE 8501

# Run the Streamlit app
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.enableCORS=false"]
```
---
### ✅ Step 2: Create `.dockerignore`
To avoid copying unnecessary files into the Docker image, add a .dockerignore file:
- __pycache__/
- *.pyc
- *.pyo
- *.pyd
- env/
- venv/
- .env
- *.db

---
### ✅ Step 3: Build the Docker Image

Open your terminal, navigate to the project directory, and run:
```
docker build -t conversational-db-agent .
```
---
### ✅ Step 4: Run the Docker Container
After successful image creation, run your container:
```
docker run -p 8501:8501 conversational-db-agent
```
- Then open your browser at http://localhost:8501 to view the app.
---
### 🌍 Optional: Run with .env Support
If you need to pass environment variables (e.g., MongoDB URI or Google API keys), you can run:
```
docker run --env-file .env -p 8501:8501 conversational-db-agent
```
---
### 🧼 Cleanup
To stop and remove the container:
```
docker ps         # to get container ID
docker stop <id>  # stop container
docker rm <id>    # remove container
```
---
### Final Notes
- Make sure .env or secrets are not hardcoded inside your Dockerfile.

- You can use Docker Compose if you plan to connect with MongoDB running as a separate container.

- Ensure requirements.txt is up to date before building.
---