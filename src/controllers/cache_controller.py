# src/controllers/cache_controller.py
from fastapi import APIRouter, HTTPException, status
from src.config.redis import get_redis
import json
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/cache/{key}")
async def set_cache(key: str, value: dict):
    """Définir une valeur dans le cache"""
    try:
        redis = await get_redis()
        logger.info(f"Tentative d'écriture dans Redis pour la clé: cache:{key}")
        value_str = json.dumps(value)
        logger.info(f"Valeur sérialisée: {value_str}")
        await redis.set(f"cache:{key}", value_str)
        logger.info("Écriture réussie dans Redis")
        return {"status": "success", "key": key}
    except Exception as e:
        logger.error(f"Erreur lors de l'écriture dans Redis: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de l'écriture dans le cache: {str(e)}"
        )

@router.get("/cache/{key}")
async def get_cache(key: str):
    """Récupérer une valeur du cache"""
    try:
        logger.info(f"Tentative de lecture depuis Redis pour la clé: cache:{key}")
        redis = await get_redis()
        value = await redis.get(f"cache:{key}")
        
        if value is None:
            logger.warning(f"Clé non trouvée dans Redis: cache:{key}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Clé non trouvée dans le cache"
            )
        
        logger.info(f"Valeur lue depuis Redis: {value}")
        
        try:
            # Essayer de désérialiser la valeur
            result = json.loads(value)
            logger.info("Valeur désérialisée avec succès")
            return result
        except json.JSONDecodeError:
            logger.warning("La valeur n'est pas un JSON valide, retour brut")
            return value
            
    except HTTPException:
        logger.warning("Erreur HTTP transmise", exc_info=True)
        raise
    except Exception as e:
        logger.error(f"Erreur lors de la lecture du cache: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la lecture du cache: {str(e)}"
        )