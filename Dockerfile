FROM python:3.10-slim

# Installer Chrome et dépendances
RUN apt-get update && apt-get install -y \
    chromium chromium-driver \
    fonts-liberation libnss3 libxss1 libasound2 libatk-bridge2.0-0 libgtk-3-0 \
    wget curl gnupg unzip

ENV CHROME_BIN=/usr/bin/chromium
ENV PATH="${PATH}:/usr/bin"

# Installer dépendances Python
WORKDIR /app
COPY . .
RUN pip install --no-cache-dir -r requirements.txt

# Lancer FastAPI
CMD ["uvicorn", "scraper_api:app", "--host", "0.0.0.0", "--port", "8080"]
