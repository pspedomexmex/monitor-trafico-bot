# -*- coding: utf-8 -*-
"""
Monitor de Tráfico - Extrae datos de X (Twitter)
Monitorea corredores viales por palabras clave y cuentas
"""

import requests
import json
import os
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from corredores_config import CORREDORES_VIALES

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MonitorTraficoX:
    """Monitor de tráfico vial usando X API v2"""
    
    def __init__(self, bearer_token: str):
        """
        Inicializa el monitor
        
        Args:
            bearer_token: Token de acceso a X API v2
        """
        self.bearer_token = bearer_token
        self.headers = {"Authorization": f"Bearer {self.bearer_token}"}
        self.api_url = "https://api.twitter.com/2/tweets/search/recent"
        self.cache_file = "alertas_trafico_cache.json"
        self.cache = self._load_cache()
    
    def _load_cache(self) -> Dict:
        """Carga cache de tweets procesados"""
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {"tweets_procesados": {}, "ultimo_update": None}
        return {"tweets_procesados": {}, "ultimo_update": None}
    
    def _save_cache(self):
        """Guarda cache a disco"""
        with open(self.cache_file, 'w', encoding='utf-8') as f:
            json.dump(self.cache, f, ensure_ascii=False, indent=2)
    
    def obtener_tweets_corredor(self, corredor_id: str) -> List[Dict]:
        """
        Obtiene tweets recientes de un corredor
        
        Args:
            corredor_id: ID del corredor (ej: PANAMERICANA_NORTE)
            
        Returns:
            Lista de tweets relevantes
        """
        if corredor_id not in CORREDORES_VIALES:
            logger.warning(f"Corredor {corredor_id} no encontrado")
            return []
        
        corredor = CORREDORES_VIALES[corredor_id]
        
        # Construye query de búsqueda
        palabras = " OR ".join(corredor["palabras_clave"])
        cuentas = " OR ".join([f"from:{c}" for c in corredor["cuentas_x"]])
        
        palabras_accidente = "accidente OR volcadura OR choque OR cierre OR afectación OR emergencia OR congestión"
        
        query = f"({cuentas}) ({palabras}) ({palabras_accidente}) -is:retweet lang:es"
        
        params = {
            "query": query,
            "max_results": 50,
            "tweet.fields": "created_at,author_id,public_metrics",
            "expansions": "author_id",
            "user.fields": "username,name"
        }
        
        try:
            response = requests.get(
                self.api_url,
                headers=self.headers,
                params=params,
                timeout=10
            )
            response.raise_for_status()
            
            data = response.json()
            tweets = data.get("data", [])
            
            # Mapea usuarios si vienen
            usuarios = {}
            includes = data.get("includes", {})
            for usuario in includes.get("users", []):
                usuarios[usuario["id"]] = usuario.get("username", "Unknown")
            
            # Añade nombres de usuario a tweets
            for tweet in tweets:
                tweet["username"] = usuarios.get(tweet.get("author_id"), "Unknown")
            
            logger.info(f"✓ {len(tweets)} tweets encontrados en {corredor['nombre']}")
            return tweets
            
        except requests.exceptions.RequestException as e:
            logger.error(f"✗ Error consultando X para {corredor_id}: {str(e)}")
            return []
    
    def procesar_alertas_corredor(self, corredor_id: str) -> List[Dict]:
        """
        Procesa tweets y genera alertas para un corredor
        
        Args:
            corredor_id: ID del corredor
            
        Returns:
            Lista de alertas nuevas (no duplicadas)
        """
        tweets = self.obtener_tweets_corredor(corredor_id)
        alertas_nuevas = []
        
        for tweet in tweets:
            tweet_id = tweet.get("id")
            
            # Evita duplicados
            if tweet_id in self.cache["tweets_procesados"]:
                continue
            
            # Valida antigüedad (máx 3 horas)
            try:
                fecha = datetime.fromisoformat(
                    tweet.get("created_at", "").replace("Z", "+00:00")
                )
                if datetime.now(fecha.tzinfo) - fecha > timedelta(hours=3):
                    continue
            except:
                continue
            
            # Crea alerta
            alerta = {
                "tweet_id": tweet_id,
                "corredor": corredor_id,
                "texto": tweet.get("text", ""),
                "usuario": tweet.get("username", "Unknown"),
                "fecha": tweet.get("created_at", ""),
                "timestamp_procesado": datetime.now().isoformat()
            }
            
            alertas_nuevas.append(alerta)
            self.cache["tweets_procesados"][tweet_id] = True
        
        self.cache["ultimo_update"] = datetime.now().isoformat()
        self._save_cache()
        
        return alertas_nuevas
    
    def obtener_resumen_corredor(self, corredor_id: str) -> Dict:
        """
        Genera resumen ejecutivo de un corredor
        
        Args:
            corredor_id: ID del corredor
            
        Returns:
            Diccionario con resumen y recomendación
        """
        if corredor_id not in CORREDORES_VIALES:
            return {"error": "Corredor no encontrado"}
        
        corredor = CORREDORES_VIALES[corredor_id]
        alertas = self.procesar_alertas_corredor(corredor_id)
        
        # Analiza severidad
        criticas = sum(1 for a in alertas if any(
            word in a["texto"].lower() for word in ["volcadura", "choque fatal", "múltiples heridos", "cerrado"]
        ))
        moderadas = sum(1 for a in alertas if any(
            word in a["texto"].lower() for word in ["cierre de carril", "afectación", "congestión", "accidente"]
        ))
        leves = len(alertas) - criticas - moderadas
        
        # Genera recomendación
        if criticas > 0:
            recomendacion = "🔴 ALTO RIESGO: Evitar si es posible. Vía crítica con incidentes graves."
            estado = "CRÍTICO"
        elif moderadas > 2:
            recomendacion = "🟠 RIESGO MODERADO: Prepárate para congestión y retrasos."
            estado = "MODERADO"
        elif moderadas > 0:
            recomendacion = "🟡 CAUCIÓN: Puede haber afectaciones menores. Circula con cuidado."
            estado = "LEVE"
        else:
            recomendacion = "🟢 VÍA DESPEJADA: Condiciones normales. Circulación fluida."
            estado = "NORMAL"
        
        return {
            "corredor_id": corredor_id,
            "corredor_nombre": corredor["nombre"],
            "estado": estado,
            "estados": corredor["estados"],
            "alertas_totales": len(alertas),
            "criticas": criticas,
            "moderadas": moderadas,
            "leves": leves,
            "recomendacion": recomendacion,
            "detalles": alertas[-3:] if alertas else [],  # Últimas 3 alertas
            "timestamp": datetime.now().isoformat()
        }
    
    def obtener_todos_corredores(self) -> Dict:
        """Obtiene resumen de TODOS los corredores"""
        resumen = {
            "timestamp": datetime.now().isoformat(),
            "corredores": {}
        }
        
        for corredor_id in CORREDORES_VIALES.keys():
            try:
                resumen["corredores"][corredor_id] = self.obtener_resumen_corredor(corredor_id)
            except Exception as e:
                logger.error(f"Error procesando {corredor_id}: {str(e)}")
        
        return resumen
