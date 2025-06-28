from locust import HttpUser, task, between
import random

class WeatherUser(HttpUser):
    # Temps d'attente entre les requêtes (1-3 secondes)
    wait_time = between(1, 3)
    
    # Liste des villes pour varier les requêtes
    cities = ["Paris", "Lyon", "Marseille", "Toulouse", "Bordeaux"]

    @task(3)  # Plus fréquent : lecture de la météo
    def get_weather(self):
        city = random.choice(self.cities)
        with self.client.get(f"/api/weather/{city}", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Erreur {response.status_code}")

    @task(1)  # Moins fréquent : écriture dans le cache
    def set_cache(self):
        key = f"test-{random.randint(1,1000)}"
        self.client.post(
            f"/api/cache/{key}",
            json={"data": "test", "value": random.random()}
        )

    @task(2)  # Fréquence moyenne : lecture du cache
    def get_cached_data(self):
        key = f"test-{random.randint(1,100)}"
        self.client.get(f"/api/cache/{key}")

    # Optionnel : appelé au démarrage de chaque utilisateur virtuel
    def on_start(self):
        # Par exemple, s'authentifier ici si nécessaire
        pass