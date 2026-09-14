# -*- coding: utf-8 -*-
"""
Configuración de Corredores Viales Mexicanos
Define corredores, estados y palabras clave para monitoreo de tráfico
"""

CORREDORES_VIALES = {
    "PANAMERICANA_NORTE": {
        "nombre": "🛣️ Panamericana Norte",
        "emoji": "🔴",
        "estados": ["Chihuahua", "Durango", "Zacatecas", "Guanajuato", "Querétaro"],
        "cuentas_x": ["CNPC_MX", "GN_Trafico"],
        "palabras_clave": ["chihuahua", "durango", "zacatecas", "guanajuato", "querétaro", "panamericana norte"],
        "distancia_km": 2100,
        "descripcion": "Eje principal norte: Frontera a CDMX"
    },
    
    "TRANSVERSAL_CENTRAL": {
        "nombre": "🛣️ Transversal Central",
        "emoji": "🟡",
        "estados": ["Jalisco", "Michoacán", "Guanajuato", "México", "Puebla"],
        "cuentas_x": ["CNPC_MX", "SCT_mx"],
        "palabras_clave": ["guadalajara", "michoacán", "méxico", "puebla", "toluca", "transversal central"],
        "distancia_km": 1500,
        "descripcion": "Eje transversal: Guadalajara a Puebla"
    },
    
    "COSTA_PACIFICO": {
        "nombre": "🌊 Costa Pacífico",
        "emoji": "🔵",
        "estados": ["Sinaloa", "Nayarit", "Jalisco", "Colima", "Guerrero"],
        "cuentas_x": ["CNPC_MX", "GN_Trafico"],
        "palabras_clave": ["sinaloa", "nayarit", "colima", "guerrero", "acapulco", "mazatlán", "pacifico"],
        "distancia_km": 2000,
        "descripcion": "Litoral del Pacífico: Sinaloa a Guerrero"
    },
    
    "GOLFO_CARIBE": {
        "nombre": "🌊 Golfo-Caribe",
        "emoji": "🟣",
        "estados": ["Veracruz", "Tabasco", "Campeche", "Quintana Roo"],
        "cuentas_x": ["CNPC_MX", "SCT_mx"],
        "palabras_clave": ["veracruz", "tabasco", "campeche", "quintana roo", "cancún", "cozumel", "golfo"],
        "distancia_km": 1900,
        "descripcion": "Litoral del Golfo: Veracruz a Quintana Roo"
    },
    
    "NORESTE": {
        "nombre": "🛣️ Noreste",
        "emoji": "🟢",
        "estados": ["Nuevo León", "Coahuila", "Tamaulipas"],
        "cuentas_x": ["GN_Trafico", "CNPC_MX"],
        "palabras_clave": ["nuevo león", "coahuila", "tamaulipas", "monterrey", "noreste"],
        "distancia_km": 1200,
        "descripcion": "Zona Noreste: Monterrey y frontera"
    },
    
    "NORTE": {
        "nombre": "🛣️ Eje Norte",
        "emoji": "🟠",
        "estados": ["Baja California", "Sonora", "Chihuahua"],
        "cuentas_x": ["GN_Trafico", "CNPC_MX"],
        "palabras_clave": ["baja california", "sonora", "frontera", "tijuana", "nogales"],
        "distancia_km": 1600,
        "descripcion": "Zona Norte: Frontera US"
    }
}

# Mapa de botones de Telegram (keyboard)
BOTONES_CORREDORES = [
    [("🛣️ Panamericana Norte", "PANAMERICANA_NORTE")],
    [("🛣️ Transversal Central", "TRANSVERSAL_CENTRAL")],
    [("🌊 Costa Pacífico", "COSTA_PACIFICO")],
    [("🌊 Golfo-Caribe", "GOLFO_CARIBE")],
    [("🛣️ Noreste", "NORESTE")],
    [("🛣️ Eje Norte", "NORTE")],
]

def get_corredor_by_id(corredor_id):
    """Obtiene información de un corredor por ID"""
    return CORREDORES_VIALES.get(corredor_id)

def get_all_corredores():
    """Retorna todos los corredores"""
    return CORREDORES_VIALES

def get_corredor_nombre(corredor_id):
    """Obtiene solo el nombre del corredor"""
    corredor = get_corredor_by_id(corredor_id)
    return corredor["nombre"] if corredor else "Corredor desconocido"
