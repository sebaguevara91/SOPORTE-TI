FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código del proyecto
COPY . .

# Puerto por defecto (sobreescribible con variable PORT)
ENV PORT=8000
EXPOSE 8000

# Iniciar servidor
CMD ["python", "backend/server.py"]
