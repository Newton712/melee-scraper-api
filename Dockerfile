# Utilise une image Python avec apt
FROM python:3.10-slim

# Installer les dépendances système, Chromium et son driver
RUN apt-get update && apt-get install -y \
    chromium \
    chromium-driver \
    fonts-liberation \
    libnss3 \
    libxss1 \
    libasound2 \
    libatk-bridge2.0-0 \
    libgtk-3-0 \
    wget curl gnupg unzip && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Définir la variable d’environnement pour Chrome
ENV CHROME_BIN=/usr/bin/chromium
ENV PATH=$PATH:/usr/bin

# Définir le dossier de travail
WORKDIR /app

# Copier les fichiers
COPY . .

# Installer les dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

# Lancer FastAPI avec uvicorn
CMD ["uvicorn", "scraper_api:app", "--host", "0.0.0.0", "--port", "8080"]
