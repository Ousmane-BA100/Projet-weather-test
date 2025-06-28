import time  # Ajoutez cette ligne
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import httpx
import os
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from fastapi import HTTPException, status
import asyncio
from ..config.redis import get_redis

# Modèles de données
class Temperature(BaseModel):
    current: float
    feels_like: float

class WeatherData(BaseModel):
    city: str
    temperature: Temperature
    humidity: float
    wind_speed: float  # en km/h
    wind_direction: float  # en degrés
    weather_description: str
    source: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

# Charger les variables d'environnement
load_dotenv(override=True)

from ..config.redis import get_redis

class WeatherService:
    def __init__(self):
        self.open_meteo_url = os.getenv("OPENMETEO_URL", "https://api.open-meteo.com/v1")
        self.timeout = 10.0
        self.cache_duration = 600  # 10 minutes

    # Puis dans la classe WeatherService :
    async def get_cached_weather(self, city: str) -> WeatherData:
        """Récupère les données météo avec cache Redis"""
        cache = await get_redis()
        cache_key = f"weather:{city.lower()}"
        cached_data = await cache.get(cache_key)
        
        if cached_data:
            return WeatherData(**cached_data)
            
        weather_data = await self.get_merged_weather(city)
        await cache.set(cache_key, weather_data.dict(), ex=self.cache_duration)
        return weather_data

    async def clear_cache(self) -> None:
        """Vide le cache Redis"""
        cache = await get_redis()
        try:
            await cache.flushdb()
        finally:
            await cache.aclose()  # Ferme proprement la connexion
    
    async def _get_coordinates(self, city: str) -> Dict[str, float]:
        """Convertit un nom de ville en coordonnées géographiques"""
        # Pour simplifier, nous utilisons des coordonnées fixes
        # En production, utilisez un service de géocodage comme Nominatim
        coordinates = {
            "paris": {"lat": 48.8566, "lon": 2.3522},
            "london": {"lat": 51.5074, "lon": -0.1278},
            "new york": {"lat": 40.7128, "lon": -74.0060},
            "tokyo": {"lat": 35.6762, "lon": 139.6503},
        }
        
        city_lower = city.lower()
        if city_lower not in coordinates:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Coordonnées non trouvées pour la ville: {city}"
            )
        return coordinates[city_lower]

    
        """Récupère les données météorologiques actuelles pour une ville donnée"""
        try:
            # Obtenir les coordonnées de la ville
            coords = await self._get_coordinates(city)
            
            # Paramètres de la requête
            params = {
                "latitude": coords["lat"],
                "longitude": coords["lon"],
                "current": "temperature_2m,relative_humidity_2m,wind_speed_10m,wind_direction_10m,weather_code",
                "timezone": "auto"
            }
            
            # Faire la requête à l'API Open-Meteo
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.open_meteo_url}/forecast",
                    params=params
                )
                response.raise_for_status()
                data = response.json()
                
            current = data.get("current", {})
            
            # Convertir le code météo en description lisible
            weather_codes = {
                0: "Ciel dégagé",
                1: "Principalement clair",
                2: "Partiellement nuageux",
                3: "Couvert",
                45: "Brouillard",
                48: "Brouillard givrant",
                51: "Bruine légère",
                53: "Bruine modérée",
                55: "Bruine dense",
                56: "Bruine verglaçante légère",
                57: "Bruine verglaçante dense",
                61: "Pluie légère",
                63: "Pluie modérée",
                65: "Pluie forte",
                66: "Pluie verglaçante légère",
                67: "Pluie verglaçante forte",
                71: "Chute de neige légère",
                73: "Chute de neige modérée",
                75: "Chute de neige forte",
                77: "Grains de neige",
                80: "Averses de pluie légères",
                81: "Averses de pluie modérées",
                82: "Averses de pluie violentes",
                85: "Averses de neige légères",
                86: "Averses de neige fortes",
                95: "Orage modéré ou fort",
                96: "Orage avec grêle légère",
                99: "Orage avec grêle forte"
            }
            
            weather_code = current.get("weather_code", 0)
            description = weather_codes.get(weather_code, "Inconnu")
            
            return WeatherData(
                city=city.capitalize(),
                temperature=Temperature(
                    current=current.get("temperature_2m", 0),
                    feels_like=current.get("temperature_2m", 0)  # Open-Meteo ne fournit pas cette donnée
                ),
                humidity=current.get("relative_humidity_2m", 0),
                wind_speed=current.get("wind_speed_10m", 0),
                wind_direction=current.get("wind_direction_10m", 0),
                weather_description=description,
                source="open-meteo"
            )
                
        except httpx.HTTPStatusError as e:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Erreur lors de l'appel à l'API météo: {str(e)}"
            )
        except httpx.RequestError as e:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Impossible de se connecter au service météo: {str(e)}"
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erreur inattendue: {str(e)}"
            )

    async def _get_weather_from_openmeteo(self, city: str) -> Optional[WeatherData]:
        """Récupère les données météo depuis Open-Meteo"""
        try:
            # Obtenir les coordonnées de la ville
            coords = await self._get_coordinates(city)
            
            # Paramètres de la requête
            params = {
                "latitude": coords["lat"],
                "longitude": coords["lon"],
                "current": "temperature_2m,relative_humidity_2m,wind_speed_10m,wind_direction_10m,weather_code",
                "timezone": "auto"
            }
            
            # Faire la requête à l'API Open-Meteo
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.open_meteo_url}/forecast",
                    params=params
                )
                response.raise_for_status()
                data = response.json()
                
            current = data.get("current", {})
            
            # Convertir le code météo en description lisible
            weather_codes = {
                0: "Ciel dégagé",
                1: "Principalement clair",
                2: "Partiellement nuageux",
                3: "Couvert",
                45: "Brouillard",
                48: "Brouillard givrant",
                51: "Bruine légère",
                53: "Bruine modérée",
                55: "Bruine dense",
                56: "Bruine verglaçante légère",
                57: "Bruine verglaçante dense",
                61: "Pluie légère",
                63: "Pluie modérée",
                65: "Pluie forte",
                66: "Pluie verglaçante légère",
                67: "Pluie verglaçante forte",
                71: "Chute de neige légère",
                73: "Chute de neige modérée",
                75: "Chute de neige forte",
                77: "Grains de neige",
                80: "Averses de pluie légères",
                81: "Averses de pluie modérées",
                82: "Averses de pluie violentes",
                85: "Averses de neige légères",
                86: "Averses de neige fortes",
                95: "Orage modéré ou fort",
                96: "Orage avec grêle légère",
                99: "Orage avec grêle forte"
            }
            
            weather_code = current.get("weather_code", 0)
            description = weather_codes.get(weather_code, "Inconnu")
            
            return WeatherData(
                city=city.capitalize(),
                temperature=Temperature(
                    current=current.get("temperature_2m", 0),
                    feels_like=current.get("temperature_2m", 0)
                ),
                humidity=current.get("relative_humidity_2m", 0),
                wind_speed=current.get("wind_speed_10m", 0),
                wind_direction=current.get("wind_direction_10m", 0),
                weather_description=description,
                source="open-meteo"
            )
                
        except Exception as e:
            print(f"Erreur OpenMeteo: {str(e)}")
            return None

    async def _get_weather_from_openweather(self, city: str) -> Optional[WeatherData]:
        """Récupère les données météo depuis OpenWeatherMap"""
        api_key = os.getenv("OPENWEATHER_API_KEY")
        if not api_key or api_key == "votre_cle_openweather":
            print("Erreur: Clé API OpenWeatherMap manquante ou non configurée")
            return None
        
        try:
            # 1. Géocodage de la ville
            geo_url = "http://api.openweathermap.org/geo/1.0/direct"
            async with httpx.AsyncClient() as client:
                geo_response = await client.get(
                    geo_url,
                    params={"q": city, "limit": 1, "appid": api_key}
                )
                geo_response.raise_for_status()
                location = geo_response.json()[0]
                
                # 2. Récupération des données météo
                weather_url = "https://api.openweathermap.org/data/2.5/weather"
                weather_response = await client.get(
                    weather_url,
                    params={
                        "lat": location["lat"],
                        "lon": location["lon"],
                        "units": "metric",
                        "lang": "fr",
                        "appid": api_key
                    }
                )
                weather_response.raise_for_status()
                data = weather_response.json()
                
                return WeatherData(
                    city=city.capitalize(),
                    temperature=Temperature(
                        current=data["main"]["temp"],
                        feels_like=data["main"]["feels_like"]
                    ),
                    humidity=data["main"]["humidity"],
                    wind_speed=data["wind"]["speed"] * 3.6,  # Conversion en km/h
                    wind_direction=data["wind"].get("deg", 0),
                    weather_description=data["weather"][0]["description"].capitalize(),
                    source="openweathermap"
                )
                
        except Exception as e:
            print(f"Erreur OpenWeatherMap: {str(e)}")
            return None
    async def _get_weather_from_weatherapi(self, city: str) -> Optional[WeatherData]:
        """Récupère les données météo depuis WeatherAPI.com"""
        api_key = os.getenv("WEATHERAPI_KEY")
        if not api_key:
            raise ValueError("Clé API WeatherAPI manquante")
        
        try:
            url = "http://api.weatherapi.com/v1/current.json"
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    url,
                    params={
                        "key": api_key,
                        "q": city,
                        "aqi": "no",
                        "lang": "fr"
                    }
                )
                response.raise_for_status()
                data = response.json()
                
                current = data["current"]
                
                return WeatherData(
                    city=data["location"]["name"],
                    temperature=Temperature(
                        current=current["temp_c"],
                        feels_like=current["feelslike_c"]
                    ),
                    humidity=current["humidity"],
                    wind_speed=current["wind_kph"],
                    wind_direction=current["wind_degree"],
                    weather_description=current["condition"]["text"],
                    source="weatherapi"
                )
                
        except Exception as e:
            print(f"Erreur WeatherAPI: {str(e)}")
            return None

    async def get_current_weather(self, city: str) -> WeatherData:
        """Récupère les données météo agrégées depuis toutes les sources disponibles"""
        try:
            # Récupérer les données de toutes les sources en parallèle
            tasks = [
                self._get_weather_from_openweather(city),
                self._get_weather_from_weatherapi(city),
                self._get_weather_from_openmeteo(city)
            ]
            
            # Exécuter toutes les tâches en parallèle
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Filtrer les résultats valides (ceux qui ne sont pas des exceptions)
            valid_results = [
                result for result in results 
                if isinstance(result, WeatherData) and result is not None
            ]
            
            if not valid_results:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="Aucune source de données météo n'est disponible"
                )
                
            # Fusionner les résultats
            return self._merge_weather_data(valid_results)
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erreur lors de la récupération des données météo: {str(e)}"
            )


    async def test_apis(self):
        """Teste la connexion aux différentes APIs"""
        print("Test des APIs en cours...")
        
        # Test OpenWeatherMap
        try:
            print("\nTest OpenWeatherMap...")
            ow_data = await self._get_weather_from_openweather("Paris")
            print(f"✓ OpenWeatherMap: {ow_data.temperature.current}°C")
        except Exception as e:
            print(f"✗ OpenWeatherMap: {str(e)}")
        
        # Test WeatherAPI
        try:
            print("\nTest WeatherAPI...")
            wa_data = await self._get_weather_from_weatherapi("Paris")
            print(f"✓ WeatherAPI: {wa_data.temperature.current}°C")
        except Exception as e:
            print(f"✗ WeatherAPI: {str(e)}")
        
        # Test OpenMeteo
        try:
            print("\nTest OpenMeteo...")
            om_data = await self._get_weather_from_openmeteo("Paris")
            print(f"✓ OpenMeteo: {om_data.temperature.current}°C")
        except Exception as e:
            print(f"✗ OpenMeteo: {str(e)}")
    
    def _merge_weather_data(self, weather_data_list: List[WeatherData]) -> WeatherData:
        """Fusionne les données météo de différentes sources"""
        if not weather_data_list:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Aucune donnée météo disponible"
            )

        # Calcul des moyennes
        avg_temp = sum(d.temperature.current for d in weather_data_list) / len(weather_data_list)
        avg_feels_like = sum(d.temperature.feels_like for d in weather_data_list) / len(weather_data_list)
        avg_humidity = sum(d.humidity for d in weather_data_list) / len(weather_data_list)
        avg_wind_speed = sum(d.wind_speed for d in weather_data_list) / len(weather_data_list)
        avg_wind_direction = sum(d.wind_direction for d in weather_data_list) / len(weather_data_list)

        # On garde la description de la première source (ou on pourrait en choisir une autre logique)
        description = weather_data_list[0].weather_description

        return WeatherData(
            city=weather_data_list[0].city,
            temperature=Temperature(
                current=round(avg_temp, 1),
                feels_like=round(avg_feels_like, 1)
            ),
            humidity=round(avg_humidity, 1),
            wind_speed=round(avg_wind_speed, 1),
            wind_direction=round(avg_wind_direction),
            weather_description=description,
            source="aggregated",
            timestamp=datetime.utcnow()
        )
    
