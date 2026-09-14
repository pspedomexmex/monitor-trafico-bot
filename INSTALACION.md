# 🚀 MONITOR DE TRÁFICO VIAL - GUÍA DE INSTALACIÓN

## 📋 REQUISITOS

- Python 3.8+
- Pip (gestor de paquetes Python)
- Telegram Bot Token (del bot creado)
- Twitter/X Bearer Token (de X API v2)

---

## ✅ PASO 1: CLONAR/DESCARGAR ARCHIVOS

```bash
# Crea carpeta del proyecto
mkdir monitor-trafico
cd monitor-trafico

# Los 4 archivos Python que necesitas están en esta carpeta:
# - bot_telegram_trafico.py (PRINCIPAL)
# - trafico_monitor.py
# - corredores_config.py
# - requirements.txt
# - .env.template
```

---

## ✅ PASO 2: INSTALAR DEPENDENCIAS

```bash
# Actualiza pip
pip install --upgrade pip

# Instala las librerías requeridas
pip install -r requirements.txt
```

**O manualmente:**
```bash
pip install python-telegram-bot==20.3
pip install requests==2.31.0
pip install python-dotenv==1.0.0
pip install apscheduler==3.10.4
```

---

## ✅ PASO 3: CONFIGURAR CREDENCIALES

### 3a. Copiar template a .env

```bash
cp .env.template .env
```

### 3b. Llenar archivo .env con tus credenciales

Abre `.env` con tu editor favorito y rellena:

```bash
# Telegram Bot Token (el que obtuviste de @BotFather)
TELEGRAM_BOT_TOKEN=8606808661:AAEf7SYCbBIpl2WLgrnMSncdtxwFEaK5uts

# Twitter Bearer Token (de developer.twitter.com)
TWITTER_BEARER_TOKEN=AAAAAAAAAAAAAAAAAAAAAAAAAA0og%2FgEAAAA3pNRF2rILpJsP6DHS...
```

**⚠️ SEGURIDAD:**
- ❌ NUNCA compartas el archivo `.env`
- ❌ NO lo subas a GitHub
- ✅ Guárdalo en lugar seguro
- ✅ Agrega a `.gitignore` si usas Git

---

## ✅ PASO 4: EJECUTAR EL BOT

```bash
# Inicia el bot
python bot_telegram_trafico.py
```

**Deberías ver:**
```
2026-09-13 21:35:00 - [INFO] - 🤖 Iniciando Monitor de Tráfico Telegram...
2026-09-13 21:35:02 - [INFO] - ✅ Scheduler configurado: alertas cada 3 horas
2026-09-13 21:35:02 - [INFO] - ✅ Bot iniciado. Escucha de mensajes...
```

---

## 📱 USAR EL BOT

### Abre Telegram y busca: **@MonitorTraficoVepo_bot**

### COMANDOS DISPONIBLES

```
/start          - Bienvenida e información
/ayuda          - Guía de uso completa
/corredores     - Listar todos los corredores viales
/estado         - Consultar estado de un corredor (interactivo)
/suscribir      - Suscribirse a alertas cada 3 horas
/desuscribir    - Cancelar alertas
```

### FLUJO DE USO

1. **Envía /start** para recibir bienvenida
2. **Envía /estado** para ver opciones de corredores
3. **Selecciona corredor** con botones interactivos
4. **Recibes reporte actual** con:
   - Estado general (Verde/Amarillo/Rojo)
   - Número de alertas
   - Últimas incidencias
   - Recomendación de viaje

5. **(Opcional) Suscríbete** con /suscribir
   - Recibes alertas automáticas cada 3 horas
   - Solo si hay tráfico nuevo en esos corredores

---

## 🔄 CÓMO FUNCIONAN LAS ALERTAS

### Cada 3 horas automáticamente:
```
El bot busca en Twitter/X:
  ├─ Cuentas de autoridades: @CNPC_MX, @GN_Trafico, @SCT_mx
  ├─ Por corredor y estado
  └─ Por palabras clave: "accidente", "cierre", "volcadura", etc.
  
Si encuentra alertas NUEVAS:
  ├─ Las filtra por severidad
  ├─ Te envía mensaje con resumen
  └─ Menciona últimas incidencias
```

### Análisis de severidad:
```
🔴 CRÍTICO    - Volcaduras, choques fatales, cierres totales
🟠 MODERADO   - Afectaciones, carriles cerrados, congestión
🟡 LEVE       - Incidentes menores
🟢 NORMAL     - Sin alertas recientes
```

---

## 🛠️ SOLUCIÓN DE PROBLEMAS

### ❌ Error: "Faltan credenciales en .env"

**Solución:**
```bash
# Verifica que .env exista y tenga tokens
cat .env

# Si no existe:
cp .env.template .env

# Luego edita y rellena los valores
```

### ❌ Error: "Conexión rechazada" con Telegram

**Solución:**
```bash
# Verifica token
echo $TELEGRAM_BOT_TOKEN

# Si está vacío, recarga .env y prueba nuevamente
```

### ❌ Error: "Twitter API: Unauthorized"

**Solución:**
```bash
# Verifica que Bearer Token sea correcto
# Regenera token en: https://developer.twitter.com/
# Reemplaza en .env
```

### ❌ Bot no envía alertas automáticas

**Solución:**
1. Verifica que el bot esté corriendo: `python bot_telegram_trafico.py`
2. Comprueba conexión a internet
3. Revisa logs para errores
4. Espera la próxima ejecución (3 horas después del inicio)

---

## 📊 ESTRUCTURA DE ARCHIVOS

```
monitor-trafico/
├── bot_telegram_trafico.py      ← MAIN (ejecutar este)
├── trafico_monitor.py           ← Lógica de monitoreo X
├── corredores_config.py         ← Configuración de corredores
├── requirements.txt             ← Dependencias
├── .env                         ← Credenciales (NO compartir)
├── .env.template               ← Template
├── alertas_trafico_cache.json  ← Cache de tweets (auto-generado)
├── usuarios_suscritos.json     ← Lista de usuarios (auto-generado)
└── INSTALACION.md              ← Este archivo
```

---

## 🚀 PRÓXIMOS PASOS

### 1. Mantener el bot en línea 24/7

**Opción A: VPS/Servidor**
```bash
# En servidor en la nube (AWS, DigitalOcean, etc)
# Ejecuta: python bot_telegram_trafico.py

# Mantenlo activo con screen o systemd:
screen -S trafico python bot_telegram_trafico.py
```

**Opción B: Local (para desarrollo)**
```bash
# Solo mantén tu computadora encendida
python bot_telegram_trafico.py
```

### 2. Escalar a WhatsApp

Una vez que funcione perfecto en Telegram, es fácil crear una versión para WhatsApp usando el código base.

### 3. Agregar más corredores

Edita `corredores_config.py` y agrega tus propios corredores con:
- Nombres de estados
- Cuentas de X a monitorear
- Palabras clave específicas

---

## 📞 SOPORTE

Si algo no funciona:

1. **Verifica logs**: Revisa los mensajes de error en consola
2. **Comprueba credenciales**: `.env` tiene tokens correctos
3. **Reinicia**: `Ctrl+C` y vuelve a ejecutar
4. **Revisa internet**: Asegúrate de tener conexión

---

## ✨ ¡LISTO!

**El bot está listo. Ahora:**
```
1. Abre Telegram
2. Busca: @MonitorTraficoVepo_bot
3. Envía: /start
4. ¡Disfruta monitoreo de tráfico automático!
```

🚗 Conducción segura en carreteras mexicanas 🛣️
