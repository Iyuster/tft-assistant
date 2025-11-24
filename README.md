# 🎮 TFT Assistant - Summoner Dashboard

Una aplicación completa para analizar tu rendimiento en **Teamfight Tactics** de Riot Games. Visualiza estadísticas de tu summoner, consulta tu ranking, analiza tu historial de partidas y obtén información detallada sobre campeones, traits, habilidades y más.

![TFT Assistant](https://img.shields.io/badge/TFT-Assistant-blueviolet?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.8+-blue?style=for-the-badge&logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-1.0+-red?style=for-the-badge&logo=streamlit)

## ✨ Características

- 📊 **Estadísticas del Summoner**: Visualiza nivel, región, PUUID y más
- 🏆 **Ranked Stats**: Consulta tu tier, rank, LP, y ratio de victorias
- 📜 **Historial de Partidas**: Analiza tus últimas 20 partidas con detalles completos
- ⚔️ **Información de Campeones**: 
  - Stats base y escalado por nivel de estrellas
  - Descripción detallada de habilidades
  - Información de costos y traits
- ✨ **Información de Traits**:
  - Descripciones completas
  - Breakpoints de activación (Bronze/Silver/Gold/Chromatic)
  - Efectos por cada nivel
- 🎯 **Composiciones**: Visualiza tus comps más jugadas y augments
- 📈 **Métricas Avanzadas**: Top 4 rate, placement promedio, daño total, y más

## 🚀 Instalación

### Requisitos Previos

- Python 3.8 o superior
- Pip (gestor de paquetes de Python)
- Una API Key de Riot Games (ver más abajo)

### Pasos de Instalación

1. **Clona el repositorio** (o descarga el código):

```bash
git clone <URL_DEL_REPOSITORIO>
cd tft_ai_assistant
```

2. **Instala las dependencias**:

```bash
pip install -r requirement.txt
```

Las dependencias incluyen:
- `streamlit` - Framework para la interfaz web
- `requests` - Para llamadas a la API de Riot
- `pandas` - Procesamiento y análisis de datos
- `python-dotenv` - Manejo de variables de entorno

3. **Configura tu API Key de Riot Games**:

Crea un archivo `.env` en el directorio raíz del proyecto:

```bash
# Windows (PowerShell)
New-Item .env

# Linux/Mac
touch .env
```

Edita el archivo `.env` y añade tu API key:

```
RIOT_API_KEY=TU_API_KEY_AQUI
```

## 🔑 Obtener una API Key de Riot Games

1. Ve a [Riot Developer Portal](https://developer.riotgames.com/)
2. Inicia sesión con tu cuenta de Riot
3. Ve a la sección "DEVELOPMENT API KEY"
4. Copia tu API key (válida por 24 horas)
5. Pégala en el archivo `.env`

> ⚠️ **Nota**: La Development API Key expira cada 24 horas. Para uso en producción, solicita una Production API Key en el portal de desarrolladores.

## 🎯 Uso

### Ejecutar la Aplicación

1. Abre una terminal en el directorio del proyecto

2. Ejecuta el comando:

```bash
streamlit run ui/extended_monitor.py
```

3. La aplicación se abrirá automáticamente en tu navegador en `http://localhost:8501`

### Buscar un Summoner

1. **Selecciona tu región** en la barra lateral (EUW1, NA1, KR, etc.)
2. **Introduce tu Game Name** (la parte antes del #)
   - Ejemplo: `Iyuster`
3. **Introduce tu Tagline** (la parte después del #)
   - Ejemplo: `TETON`
4. **Ajusta el número de partidas** a analizar (5-20)
5. Haz clic en **🔎 Buscar**

### Ejemplo

Para buscar el summoner `Iyuster#TETON`:
- Game Name: `Iyuster`
- Tagline: `TETON`
- Región: `EUW1`

## 📁 Estructura del Proyecto

```
tft_ai_assistant/
├── .env                     # Variables de entorno (API key)
├── config.py                # Configuración centralizada
├── requirement.txt          # Dependencias de Python
├── README.md               # Este archivo
│
├── api/                    # API endpoints (futuro)
│   ├── __init__.py
│   └── main.py
│
├── data_collection/        # Módulos de recolección de datos
│   ├── __init__.py
│   ├── summoner.py         # Obtener datos del summoner
│   ├── match_history.py    # Histórico de partidas
│   ├── ranked_stats.py     # Estadísticas ranked
│   └── tft_static_data.py  # Datos estáticos (campeones, traits, items)
│
├── data_processing/        # Procesamiento y análisis
│   ├── __init__.py
│   ├── parser.py           # Parser de partidas
│   ├── stats.py            # Cálculo de estadísticas
│   └── formatters.py       # Formateo para UI
│
├── ui/                     # Interfaz de usuario
│   ├── __init__.py
│   └── extended_monitor.py # Aplicación principal Streamlit
│
├── test/                   # Tests y scripts de prueba
│   ├── __init__.py
│   ├── test_riot_api.py    # Test de la API de Riot
│   └── database_schema.sql # Schema de BD (futuro)
│
└── models/                 # Modelos de datos (futuro)
    └── __init__.py
```

## 🔧 Funcionalidades Técnicas

### APIs Utilizadas

1. **Riot Games API**:
   - Account API v1 (obtener PUUID por Riot ID)
   - TFT Summoner v1 (datos del summoner)
   - TFT League v1 (ranked stats)
   - TFT Match v1 (historial de partidas)

2. **Community Dragon API**:
   - Datos estáticos de TFT (campeones, traits, items)
   - Imágenes e iconos
   - Descripciones y stats completas

### Sistema de Caché

La aplicación utiliza un sistema de caché local para:
- Datos estáticos de Community Dragon
- Reducir llamadas innecesarias a la API
- Mejorar el rendimiento de carga

Los datos se guardan en `.cache/` (creado automáticamente).

## 🐛 Solución de Problemas

### Error: API Key Expired

**Problema**: `❌ Error 403: Forbidden`

**Solución**: Tu API key ha expirado. Obtén una nueva en el [Developer Portal](https://developer.riotgames.com/) y actualiza el archivo `.env`.

### Error: Summoner Not Found

**Problema**: `❌ Summoner no encontrado`

**Soluciones**:
1. Verifica que el Game Name y Tagline sean correctos
2. Asegúrate de escribir SOLO el nombre (sin el #)
3. Verifica que la región seleccionada sea la correcta
4. Revisa que tu Riot ID esté actualizado (cambió del antiguo sistema)

### Error: Module Not Found

**Problema**: `ModuleNotFoundError: No module named 'streamlit'`

**Solución**: Instala las dependencias:
```bash
pip install -r requirement.txt
```

### La aplicación se queda cargando

**Problema**: La aplicación se queda en "Loading..." indefinidamente

**Soluciones**:
1. Verifica tu conexión a internet
2. Comprueba que tu API key es válida
3. Intenta con menos partidas (ej: 5 en lugar de 20)
4. Revisa la consola para ver mensajes de error

## 🔮 Futuras Mejoras

- [ ] Sistema de análisis de composiciones meta
- [ ] Recomendaciones de builds basadas en stats
- [ ] Comparación con otros jugadores
- [ ] Gráficos de progresión temporal
- [ ] Base de datos para almacenar histórico
- [ ] API REST para integración con otras apps
- [ ] Calculadora de probabilidades de campeones
- [ ] Análisis de winrate por comp/augment

## 📝 Notas

- La API de desarrollo de Riot tiene límites de rate (20 requests/segundo, 100 requests/2 minutos)
- Los datos estáticos se actualizan con cada nuevo set de TFT
- La aplicación funciona mejor con Chrome/Firefox actualizados
- Se recomienda Python 3.9+ para mejor compatibilidad

## 👨‍💻 Desarrollo

### Testear la API

Ejecuta el script de test para verificar que tu API key funciona:

```bash
python test/test_riot_api.py
```

### Limpiar caché

Si los datos estáticos están desactualizados, elimina la carpeta `.cache/`:

```bash
# Windows
rmdir /s .cache

# Linux/Mac
rm -rf .cache
```

## 📄 Licencia

Este proyecto es para uso educativo y personal. Respeta los [Términos de Servicio de Riot Games](https://www.riotgames.com/en/terms-of-service).

## 🙏 Agradecimientos

- [Riot Games](https://www.riotgames.com/) por la API de TFT
- [Community Dragon](https://communitydragon.org/) por los datos estáticos
- [Streamlit](https://streamlit.io/) por el framework de UI

---

**¿Tienes preguntas o problemas?** Abre un issue o contacta con el desarrollador.

**¡Buena suerte en la Convergence!** 🎮✨
