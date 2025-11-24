# 🎮 TFT Meta Assistant

Analiza el Meta y tu Rendimiento en Teamfight Tactics

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io)

## ✨ Características

### 🔍 Búsqueda de Summoners
- Busca cualquier jugador por Game Name + Tag
- Visualiza estadísticas ranked oficiales (Tier, LP, Winrate)
- Historial detallado de partidas
- Análisis de composiciones, traits y unidades

### 📊 Meta Dashboard (Requiere datos)
- Estadísticas del meta actual
- Top composiciones más jugadas
- Análisis de tendencias y winrates
- Filtros avanzados por región y patch

## 🚀 Deployment en Streamlit Cloud

### Configuración Rápida

1. **Fork/Clone este repositorio**

2. **Crea una app en [Streamlit Cloud](https://share.streamlit.io)**
   - Main file path: `streamlit_app.py`

3. **Configura los Secrets** (Settings → Secrets):
   ```toml
   RIOT_API_KEY = "RGAPI-tu-api-key-aquí"
   ```

4. **Obtén tu API Key**:
   - Ve a [developer.riotgames.com](https://developer.riotgames.com/)
   - Inicia sesión y copia tu Development API Key

¡Listo! Tu app estará funcionando en minutos.

> **Nota**: La funcionalidad de búsqueda de summoners funciona inmediatamente. Las estadísticas del meta requieren poblar la base de datos (ver sección de Desarrollo Local).

## 💻 Desarrollo Local

### Requisitos
- Python 3.8+
- Riot Games API Key

### Instalación

```bash
# Clonar el repositorio
git clone https://github.com/tu-usuario/tft_ai_assistant.git
cd tft_ai_assistant

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
cp .env.example .env
# Edita .env y añade tu RIOT_API_KEY

# Inicializar la base de datos
python -m database.db_manager

# Ejecutar la aplicación
streamlit run streamlit_app.py
```

### Recolección de Datos del Meta (Opcional)

Para poblar las estadísticas del meta:

```bash
# Recolectar datos de jugadores GM+
python scripts/collect_data.py
```

## 📁 Estructura del Proyecto

```
tft_ai_assistant/
├── streamlit_app.py          # Entry point para Streamlit Cloud
├── requirements.txt           # Dependencias
├── config.py                  # Configuración centralizada
├── .env.example              # Template de variables de entorno
│
├── ui/                       # Interfaz de usuario
│   ├── extended_monitor.py   # Aplicación principal
│   └── streamlit_app.py      # Entry point alternativo
│
├── api/                      # API endpoints (futuro)
├── data_collection/          # Módulos de recolección de datos
│   ├── summoner.py
│   ├── match_history.py
│   ├── ranked_stats.py
│   └── tft_static_data.py
│
├── data_processing/          # Procesamiento y formateo
│   ├── parser.py
│   ├── stats.py
│   └── formatters.py
│
├── database/                 # Gestión de base de datos
│   ├── models.py
│   └── db_manager.py
│
├── meta_analysis/            # Análisis del meta
│   └── meta_report.py
│
└── scripts/                  # Scripts de utilidad
    └── collect_data.py
```

## 🎨 Características de la UI

- 🌙 **Modo Oscuro por Defecto** - Diseño moderno y elegante
- 📱 **Responsive** - Funciona en desktop y móvil
- ⚡ **Rápido** - Carga optimizada de datos
- 🎯 **Intuitivo** - Navegación simple y clara

## 🔧 Tecnologías

- **Frontend**: Streamlit
- **Backend**: Python 3.8+
- **Database**: SQLite (local) / PostgreSQL (producción)
- **API**: Riot Games API
- **ORM**: SQLAlchemy

## 📝 Variables de Entorno

| Variable | Descripción | Requerido |
|----------|-------------|-----------|
| `RIOT_API_KEY` | Tu Riot Games API Key | ✅ Sí |
| `DATABASE_URL` | URL de base de datos (default: SQLite local) | ❌ No |

## 🐛 Troubleshooting

### La app no carga
- Verifica que `RIOT_API_KEY` esté configurada en los Secrets
- La Development API Key expira cada 24 horas

### No aparecen estadísticas del meta
- Esto es normal en deployment inicial
- La búsqueda de summoners funciona independientemente
- Para poblar el meta, ejecuta `python scripts/collect_data.py` localmente

### Error de módulos
- Asegúrate de usar `streamlit_app.py` como entry point
- Verifica que todas las carpetas estén en el repositorio

## 📄 Licencia

MIT License - Ver [LICENSE](LICENSE) para más detalles

## 🤝 Contribuciones

Las contribuciones son bienvenidas! Por favor:

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📧 Contacto

Para preguntas o sugerencias, abre un issue en GitHub.

---

**Hecho con ❤️ para la comunidad de TFT**
