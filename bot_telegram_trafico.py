# -*- coding: utf-8 -*-
"""
Bot Telegram - Monitor de Tráfico Vial México
Alertas automáticas cada 3 horas + Consultas interactivas
Autor: Edgar Martinez
Versión: 1.0
"""

import os
import logging
import json
from datetime import datetime
from typing import Dict, List
from dotenv import load_dotenv
from apscheduler.schedulers.background import BackgroundScheduler

from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters

from trafico_monitor import MonitorTraficoX
from corredores_config import CORREDORES_VIALES, BOTONES_CORREDORES, get_corredor_by_id, get_corredor_nombre

# ==================== CONFIGURACIÓN ====================
load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TWITTER_BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN")

if not TELEGRAM_BOT_TOKEN or not TWITTER_BEARER_TOKEN:
    raise ValueError("❌ Faltan credenciales en .env")

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [%(levelname)s] - %(message)s'
)
logger = logging.getLogger(__name__)

# Base de datos de usuarios suscritos
USUARIOS_SUSCRITOS_FILE = "usuarios_suscritos.json"

# ==================== CARGAR/GUARDAR USUARIOS ====================
def cargar_usuarios() -> Dict:
    """Carga usuarios suscritos de archivo"""
    if os.path.exists(USUARIOS_SUSCRITOS_FILE):
        try:
            with open(USUARIOS_SUSCRITOS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    return {}

def guardar_usuarios(usuarios: Dict):
    """Guarda usuarios a archivo"""
    with open(USUARIOS_SUSCRITOS_FILE, 'w', encoding='utf-8') as f:
        json.dump(usuarios, f, ensure_ascii=False, indent=2)

# ==================== INICIALIZAR ====================
monitor = MonitorTraficoX(TWITTER_BEARER_TOKEN)
usuarios_suscritos = cargar_usuarios()
scheduler = BackgroundScheduler()

# ==================== MANEJADORES DE COMANDOS ====================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /start - Bienvenida"""
    usuario_id = str(update.effective_user.id)
    
    mensaje = """
🚨 *MONITOR DE TRÁFICO VIAL MÉXICO* 🚨

¡Hola! Soy tu asistente de tráfico vial.

Puedo ayudarte con:
✅ Estado actual de corredores viales
✅ Alertas automáticas cada 3 horas
✅ Consultas personalizadas por región

*Comandos disponibles:*
/estado - Ver estado actual de un corredor
/suscribir - Recibir alertas cada 3 horas
/desuscribir - Dejar de recibir alertas
/ayuda - Ver esta información
/corredores - Listar todos los corredores
"""
    
    await update.message.reply_text(mensaje, parse_mode='Markdown')
    
    # Inicia usuario si no existe
    if usuario_id not in usuarios_suscritos:
        usuarios_suscritos[usuario_id] = {
            "nombre": update.effective_user.first_name,
            "corredores": [],
            "activo": True
        }
        guardar_usuarios(usuarios_suscritos)

async def comando_ayuda(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /ayuda"""
    mensaje = """
📖 *GUÍA DE USO*

*Cómo funciona:*
1. Elige un corredor vial
2. Recibe estado actual del tráfico
3. Opcionalmente, suscríbete a alertas automáticas cada 3 horas

*Corredores disponibles:*
🛣️ Panamericana Norte - Chihuahua a Querétaro
🛣️ Transversal Central - Guadalajara a Puebla  
🌊 Costa Pacífico - Sinaloa a Guerrero
🌊 Golfo-Caribe - Veracruz a Quintana Roo
🛣️ Noreste - Nuevo León a Tamaulipas
🛣️ Eje Norte - Frontera US

*Comandos:*
/estado - Consultar corredor
/corredores - Ver lista completa
/suscribir - Recibir alertas
/desuscribir - Cancelar alertas
/ayuda - Esta información
"""
    
    await update.message.reply_text(mensaje, parse_mode='Markdown')

async def comando_corredores(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /corredores - Listar todos"""
    mensaje = "🗺️ *CORREDORES DISPONIBLES*\n\n"
    
    for corredor_id, datos in CORREDORES_VIALES.items():
        mensaje += f"{datos['nombre']}\n"
        mensaje += f"  📍 Estados: {', '.join(datos['estados'][:3])}...\n"
        mensaje += f"  🚗 Distancia: {datos['distancia_km']} km\n\n"
    
    await update.message.reply_text(mensaje, parse_mode='Markdown')

async def comando_estado(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /estado - Consultar estado de corredor"""
    mensaje = "¿Cuál corredor quieres consultar?\n\n"
    
    keyboard = []
    for botones_fila in BOTONES_CORREDORES:
        fila = []
        for texto, callback_data in botones_fila:
            fila.append(InlineKeyboardButton(texto, callback_data=f"estado_{callback_data}"))
        keyboard.append(fila)
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(mensaje, reply_markup=reply_markup)

async def comando_suscribir(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /suscribir - Suscribirse a alertas"""
    usuario_id = str(update.effective_user.id)
    
    if usuario_id not in usuarios_suscritos:
        usuarios_suscritos[usuario_id] = {
            "nombre": update.effective_user.first_name,
            "corredores": [],
            "activo": True
        }
    
    mensaje = "¿A cuál corredor deseas recibir alertas cada 3 horas?\n\n"
    
    keyboard = []
    for botones_fila in BOTONES_CORREDORES:
        fila = []
        for texto, callback_data in botones_fila:
            fila.append(InlineKeyboardButton(f"📬 {texto}", callback_data=f"suscribir_{callback_data}"))
        keyboard.append(fila)
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(mensaje, reply_markup=reply_markup)

async def comando_desuscribir(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /desuscribir"""
    usuario_id = str(update.effective_user.id)
    
    if usuario_id in usuarios_suscritos:
        usuarios_suscritos[usuario_id]["activo"] = False
        guardar_usuarios(usuarios_suscritos)
        
        await update.message.reply_text(
            "✋ Te has desuscrito de todas las alertas.\n\n"
            "Escribe /suscribir para reactivar.",
            parse_mode='Markdown'
        )
    else:
        await update.message.reply_text("No estabas suscrito a ninguna alerta.")

# ==================== MANEJADORES DE CALLBACKS ====================

async def callback_estado(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Callback - Estado de corredor"""
    query = update.callback_query
    corredor_id = query.data.replace("estado_", "")
    
    try:
        resumen = monitor.obtener_resumen_corredor(corredor_id)
        
        mensaje = f"""
*{resumen['corredor_nombre']}*

{resumen['recomendacion']}

📊 *Resumen de alertas:*
🔴 Críticas: {resumen['criticas']}
🟡 Moderadas: {resumen['moderadas']}
🟢 Leves: {resumen['leves']}

📍 *Estados cubiertos:*
{', '.join(resumen['estados'])}

*Últimas alertas:*
"""
        
        if resumen['detalles']:
            for alerta in resumen['detalles']:
                mensaje += f"\n• {alerta['texto'][:100]}...\n  _by @{alerta['usuario']}_"
        else:
            mensaje += "\n✅ Sin alertas recientes"
        
        mensaje += f"\n\n⏰ Actualizado: {datetime.now().strftime('%H:%M:%S')}"
        
        await query.edit_message_text(
            text=mensaje,
            parse_mode='Markdown'
        )
        
    except Exception as e:
        logger.error(f"Error en callback_estado: {str(e)}")
        await query.edit_message_text(
            text=f"❌ Error: {str(e)}"
        )

async def callback_suscribir(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Callback - Suscribirse a corredor"""
    query = update.callback_query
    corredor_id = query.data.replace("suscribir_", "")
    usuario_id = str(query.from_user.id)
    
    try:
        if usuario_id not in usuarios_suscritos:
            usuarios_suscritos[usuario_id] = {
                "nombre": query.from_user.first_name,
                "corredores": [],
                "activo": True
            }
        
        if corredor_id not in usuarios_suscritos[usuario_id]["corredores"]:
            usuarios_suscritos[usuario_id]["corredores"].append(corredor_id)
            usuarios_suscritos[usuario_id]["activo"] = True
            guardar_usuarios(usuarios_suscritos)
            
            corredor_nombre = get_corredor_nombre(corredor_id)
            await query.edit_message_text(
                text=f"✅ Te has suscrito a alertas de {corredor_nombre}\n\n"
                     f"Recibirás reportes cada 3 horas.",
                parse_mode='Markdown'
            )
        else:
            await query.edit_message_text(
                text="Ya estabas suscrito a este corredor."
            )
        
    except Exception as e:
        logger.error(f"Error en callback_suscribir: {str(e)}")
        await query.edit_message_text(text=f"❌ Error: {str(e)}")

# ==================== TAREAS PROGRAMADAS ====================

async def enviar_alertas_programadas(context: ContextTypes.DEFAULT_TYPE):
    """Ejecuta cada 3 horas - Envía alertas a usuarios suscritos"""
    logger.info("⏰ Ejecutando envío de alertas programadas...")
    
    for usuario_id, datos in usuarios_suscritos.items():
        if not datos["activo"]:
            continue
        
        for corredor_id in datos.get("corredores", []):
            try:
                resumen = monitor.obtener_resumen_corredor(corredor_id)
                
                # Solo envía si hay alertas
                if resumen['alertas_totales'] > 0:
                    mensaje = f"""
🚨 *ALERTA DE TRÁFICO - {resumen['corredor_nombre']}*

{resumen['recomendacion']}

📊 Alertas: {resumen['criticas']} críticas, {resumen['moderadas']} moderadas

_Actualización: {datetime.now().strftime('%H:%M')} hrs_
"""
                    
                    try:
                        await context.bot.send_message(
                            chat_id=usuario_id,
                            text=mensaje,
                            parse_mode='Markdown'
                        )
                    except Exception as e:
                        logger.error(f"No se pudo enviar a {usuario_id}: {str(e)}")
                
            except Exception as e:
                logger.error(f"Error procesando alerta para {corredor_id}: {str(e)}")

async def mensaje_texto(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Maneja mensajes de texto no procesados"""
    texto = update.message.text.lower()
    
    if "estado" in texto or "¿cómo está" in texto:
        await comando_estado(update, context)
    elif "corredores" in texto or "qué hay" in texto:
        await comando_corredores(update, context)
    elif "suscribir" in texto or "alertas" in texto:
        await comando_suscribir(update, context)
    elif "ayuda" in texto or "help" in texto:
        await comando_ayuda(update, context)
    else:
        await update.message.reply_text(
            "No entendí tu mensaje 😕\n\n"
            "Escribe /ayuda para ver comandos disponibles.",
            parse_mode='Markdown'
        )

# ==================== MAIN ====================

def main():
    """Inicia el bot"""
    logger.info("🤖 Iniciando Monitor de Tráfico Telegram...")
    
    # Crear aplicación
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    # Registrar comandos
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("ayuda", comando_ayuda))
    app.add_handler(CommandHandler("corredores", comando_corredores))
    app.add_handler(CommandHandler("estado", comando_estado))
    app.add_handler(CommandHandler("suscribir", comando_suscribir))
    app.add_handler(CommandHandler("desuscribir", comando_desuscribir))
    
    # Registrar callbacks
    app.add_handler(CallbackQueryHandler(callback_estado, pattern="^estado_"))
    app.add_handler(CallbackQueryHandler(callback_suscribir, pattern="^suscribir_"))
    
    # Registrar handler de mensajes de texto
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, mensaje_texto))
    
    # Configurar scheduler para alertas cada 3 horas
    job_config = {
        "func": enviar_alertas_programadas,
        "trigger": "interval",
        "hours": 3,
        "id": "alertas_trafico",
        "name": "Envío de alertas cada 3 horas",
        "replace_existing": True,
        "misfire_grace_time": 300
    }
    
    # Pasar context como argumento
    app.job_queue.run_repeating(
        callback=job_config["func"],
        interval=10800,  # 3 horas en segundos
        first=10,  # Ejecuta en 10 segundos después de iniciar (para pruebas)
        name=job_config["name"]
    )
    
    logger.info("✅ Scheduler configurado: alertas cada 3 horas")
    logger.info("✅ Bot iniciado. Escucha de mensajes...")
    
    # Inicia el bot
    app.run_polling()

if __name__ == '__main__':
    main()
