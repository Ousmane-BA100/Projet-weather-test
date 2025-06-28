#!/bin/sh
echo "🕒 Vérification de la connexion à Redis..."
while ! nc -z redis 6379; do
  echo "⏳ En attente de Redis (redis:6379)..."
  sleep 2
done

echo "✅ Redis est prêt !"
echo "🔍 Vérification des variables d'environnement..."
echo "REDIS_HOST=${REDIS_HOST}"
echo "REDIS_PORT=${REDIS_PORT}"

echo "🚀 Démarrage de l'application..."
exec uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload