FROM python:3.11-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1
ENV PORT=8080

COPY agent/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY agent /app/agent
COPY demo-app /app/demo-app

EXPOSE 8080

CMD ["uvicorn", "agent.app.main:app", "--host", "0.0.0.0", "--port", "8080"]
