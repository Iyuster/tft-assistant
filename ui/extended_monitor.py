import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import streamlit as st
from dotenv import load_dotenv
from datetime import datetime
import pandas as pd

from data_collection.summoner import fetch_summoner_by_riot_id, fetch_summoner_details_by_puuid
from data_collection.match_history import fetch_match_ids, fetch_match_details
from data_collection.ranked_stats import fetch_ranked_stats
from data_collection.tft_static_data import get_champion_info, get_trait_info, get_item_info
from data_processing.parser import parse_match
from data_processing.stats import compute_stats
from data_processing.formatters import (
    format_placement, format_champion_stats, format_ability_description,
    format_trait_description, format_item_description, get_trait_style_emoji,
    format_match_summary
)
from config import APP_TITLE, MAX_MATCHES, DEFAULT_REGION, DEFAULT_ROUTING, REGIONS
from database.db_manager import db_manager
from meta_analysis.meta_report import get_top_comps, get_meta_summary, format_comp_for_display

# Load environment variables
load_dotenv()
api_key = os.getenv('RIOT_API_KEY')

# Page config
st.set_page_config(
    page_title="TFT Assistant",
    page_icon="🎮",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Initialize session state
if 'dark_theme' not in st.session_state:
    st.session_state.dark_theme = False


# ============================================================
# THEME CSS FUNCTIONS
# ============================================================
def render_dark_theme_css():
    """Render dark theme CSS"""
    st.markdown("""
    <style>
        .stApp { background-color: #0e1117; }
        [data-testid="collapsedControl"] { display: none; }
        
        .main-header { text-align: center; padding: 1.5rem 0 1rem 0; }
        .main-title {
            font-size: 3.5rem; font-weight: 800;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;
            margin-bottom: 0.5rem; text-align: center;
            filter: drop-shadow(2px 2px 4px rgba(0,0,0,0.1));
        }
        .subtitle { text-align: center; color: #aaa; font-size: 1.1rem; margin-bottom: 1.5rem; font-weight: 500; }
        
        .stat-card {
            background: linear-gradient(135deg, #667eea25 0%, #764ba225 100%);
            border-radius: 15px; padding: 1.5rem; text-align: center;
            border: 1px solid #667eea50; transition: transform 0.2s;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }
        .stat-card:hover { transform: translateY(-8px); box-shadow: 0 12px 30px rgba(102, 126, 234, 0.4); }
        .stat-number {
            font-size: 2.5rem; font-weight: bold;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        }
        .stat-label { color: #aaa; font-size: 0.95rem; margin-top: 0.5rem; font-weight: 600; }
        
        .comp-card {
            background: #1e1e1e; border-radius: 12px; padding: 1.2rem; margin: 0.5rem 0;
            border-left: 5px solid #667eea; box-shadow: 0 4px 12px rgba(0,0,0,0.5);
        }
        .comp-card h4 { color: #667eea !important; }
        
        .search-container {
            background: linear-gradient(135deg, #667eea15 0%, #764ba215 100%);
            border-radius: 20px; padding: 2rem; margin: 1.5rem auto;
            max-width: 900px; border: 2px solid #667eea40; box-shadow: 0 8px 25px rgba(0,0,0,0.12);
        }
    </style>
    """, unsafe_allow_html=True)


def render_light_theme_css():
    """Render light theme CSS"""
    st.markdown("""
    <style>
        .stApp { background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%); }
        [data-testid="collapsedControl"] { display: none; }
        
        .main-header { text-align: center; padding: 1.5rem 0 1rem 0; }
        .main-title {
            font-size: 3.5rem; font-weight: 800;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;
            margin-bottom: 0.5rem; text-align: center;
            filter: drop-shadow(2px 2px 4px rgba(0,0,0,0.1));
        }
        .subtitle { text-align: center; color: #2d3748; font-size: 1.1rem; margin-bottom: 1.5rem; font-weight: 500; }
        
        .stat-card {
            background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
            border-radius: 15px; padding: 1.5rem; text-align: center;
            border: 2px solid rgba(102, 126, 234, 0.2);
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }
        .stat-card:hover { transform: translateY(-8px); box-shadow: 0 12px 30px rgba(102, 126, 234, 0.25); }
        .stat-number {
            font-size: 2.5rem; font-weight: bold;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        }
        .stat-label { color: #4a5568; font-size: 0.95rem; margin-top: 0.5rem; font-weight: 600; }
        
        .comp-card {
            background: linear-gradient(135deg, #ffffff 0%, #f7fafc 100%);
            border-radius: 12px; padding: 1.2rem; margin: 0.5rem 0;
            border-left: 5px solid #667eea; box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        }
        .comp-card h4 { color: #1a202c !important; }
        
        .search-container {
            background: linear-gradient(135deg, #ffffff 0%, #f7fafc 100%);
            border-radius: 20px; padding: 2rem; margin: 1.5rem auto;
            max-width: 900px; border: 2px solid rgba(102, 126, 234, 0.2);
            box-shadow: 0 8px 25px rgba(0,0,0,0.12);
        }
        
        /* Force dark text in light mode */
        .stApp *, h1, h2, h3, h4, h5, h6, p, span, div, label { color: #1a202c !important; }
        input, textarea { color: #1a202c !important; }
    </style>
    """, unsafe_allow_html=True)


# ============================================================
# SUMMONER PROFILE VIEW
# ============================================================
def render_summoner_profile(summoner_name, summoner_tag, summoner_region, routing, num_matches):
    """Render the summoner profile view"""
    # Back button
    col_back, col_theme = st.columns([9, 1])
    with col_back:
        if st.button("🔙 Volver al Dashboard", type="secondary"):
            st.query_params.clear()
            st.rerun()
    with col_theme:
        if st.button("🌙" if not st.session_state.dark_theme else "☀️", key="theme_toggle"):
            st.session_state.dark_theme = not st.session_state.dark_theme
            st.rerun()
    
    st.divider()
    
    # Fetch summoner data
    with st.spinner(f"🔍 Cargando perfil de {summoner_name}#{summoner_tag}..."):
        summoner_data = fetch_summoner_by_riot_id(api_key, summoner_region, routing, summoner_name, summoner_tag)
        
        if not summoner_data:
            st.error(f"❌ No se pudo encontrar a {summoner_name}#{summoner_tag}")
            if st.button("Volver a buscar"):
                st.query_params.clear()
                st.rerun()
            st.stop()
        
        puuid = summoner_data.get('puuid')
        if not puuid:
            st.error("❌ No se pudo obtener el PUUID del summoner.")
            st.stop()
            
        # Header
        st.title(f"📊 Perfil de {summoner_name}#{summoner_tag}")
        st.caption(f"Región: {summoner_region.upper()}")
        
        # Try to get Summoner ID for official stats
        summoner_details = fetch_summoner_details_by_puuid(api_key, summoner_region, puuid)
        summoner_id = None
        if summoner_details:
            summoner_id = summoner_details.get('id')
            
        # If no ID, try fallback from match history (last resort for ID)
        if not summoner_id:
             try:
                latest_matches = fetch_match_ids(api_key, routing, puuid, count=1)
                if latest_matches:
                    match_detail = fetch_match_details(api_key, routing, latest_matches[0])
                    if match_detail and 'info' in match_detail:
                        for p in match_detail['info']['participants']:
                            if p.get('puuid') == puuid:
                                summoner_id = p.get('summonerId')
                                break
             except:
                 pass

        # DECISION: Official Ranked Stats vs Calculated Stats
        if summoner_id:
            # Show Official Ranked Stats
            st.markdown("### 🏆 Estadísticas Ranked (Oficial)")
            ranked_data = fetch_ranked_stats(api_key, summoner_region, summoner_id)
            if ranked_data:
                found_tft = False
                for entry in ranked_data:
                    if entry.get('queueType') == 'RANKED_TFT':
                        found_tft = True
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.metric("Tier", f"{entry.get('tier', 'N/A')} {entry.get('rank', '')}")
                        with col2:
                            st.metric("LP", entry.get('leaguePoints', 0))
                        with col3:
                            wins = entry.get('wins', 0)
                            losses = entry.get('losses', 0)
                            total = wins + losses
                            winrate = (wins/total*100) if total > 0 else 0
                            st.metric("Winrate", f"{winrate:.1f}%")
                        with col4:
                            st.metric("Partidas", f"{wins}W / {losses}L")
                if not found_tft:
                    st.info("Este summoner no tiene partidas clasificatorias en TFT este set.")
            else:
                st.info("No se encontraron datos de ranked.")
        else:
            # Show Calculated Stats (Fallback)
            st.markdown("### 📈 Estadísticas de Rendimiento")
            
            with st.spinner("🔄 Analizando historial..."):
                match_ids = fetch_match_ids(api_key, routing, puuid, count=num_matches)
                match_records = []
                parsed_matches = []
                
                if match_ids:
                    for match_id in match_ids:
                        match_detail = fetch_match_details(api_key, routing, match_id)
                        if match_detail:
                            parsed = parse_match(match_detail, puuid)
                            if parsed:
                                match_records.append(parsed)
                                parsed_matches.append((match_id, parsed))
                
                if match_records:
                    stats = compute_stats(match_records)
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Partidas", len(match_records))
                    with col2:
                        st.metric("Avg Place", f"{stats.get('avg_placement', 0):.2f}")
                    with col3:
                        st.metric("Top 4", f"{stats.get('top_4_rate', 0)*100:.1f}%")
                    with col4:
                        st.metric("Win Rate", f"{stats.get('top_1_rate', 0)*100:.1f}%")
                else:
                    st.info("No hay datos suficientes.")

        # Match List Display
        st.divider()
        st.markdown("### 📜 Historial Detallado")
        
        # Re-use parsed_matches if we calculated stats, otherwise fetch them
        if not 'parsed_matches' in locals():
             match_ids = fetch_match_ids(api_key, routing, puuid, count=num_matches)
             parsed_matches = []
             if match_ids:
                for match_id in match_ids:
                    match_detail = fetch_match_details(api_key, routing, match_id)
                    if match_detail:
                        parsed = parse_match(match_detail, puuid)
                        if parsed:
                            parsed_matches.append((match_id, parsed))

        if parsed_matches:
            for idx, (match_id, parsed) in enumerate(parsed_matches):
                with st.expander(f"Partida #{idx+1} - {format_match_summary(parsed)}", expanded=(idx==0)):
                    col1, col2 = st.columns([1, 2])
                    
                    with col1:
                        st.markdown("#### 📊 Resumen")
                        st.write(f"**Placement:** {format_placement(parsed['placement'])}")
                        st.write(f"**Level:** {parsed.get('level', 'N/A')}")
                        st.write(f"**Gold Left:** {parsed.get('gold_left', 0)}")
                        st.write(f"**Damage:** {parsed.get('total_damage_to_players', 0)}")
                    
                    with col2:
                        st.markdown("#### ⚡ Traits")
                        traits = parsed.get('traits', [])
                        if traits:
                            for trait in sorted(traits, key=lambda x: x.get('num_units', 0), reverse=True):
                                emoji = get_trait_style_emoji(trait)
                                st.write(f"{emoji} **{trait.get('name', 'Unknown')}** ({trait.get('num_units', 0)} units)")
                        else:
                            st.write("No traits data")
                    
                    st.markdown("#### 🎮 Units")
                    units = parsed.get('units', [])
                    if units:
                        units_cols = st.columns(min(len(units), 5))
                        for i, unit in enumerate(units):
                            with units_cols[i % 5]:
                                stars = "⭐" * unit.get('tier', 1)
                                st.write(f"{stars}")
                                st.write(f"**{unit.get('character_id', 'Unknown')}**")
                                items = unit.get('itemNames', [])
                                if items:
                                    for item in items[:3]:
                                        st.caption(f"🔹 {item}")
                    else:
                        st.write("No units data")
        else:
            st.warning("No se encontraron partidas para mostrar.")


# ============================================================
# META REPORT VIEW
# ============================================================
def render_meta_report():
    """Render the full meta report view"""
    # Back button and theme toggle
    col_back, col_theme = st.columns([9, 1])
    with col_back:
        if st.button("🔙 Volver al Dashboard", type="secondary"):
            st.query_params.clear()
            st.rerun()
    with col_theme:
        if st.button("🌙" if not st.session_state.dark_theme else "☀️", key="theme_toggle"):
            st.session_state.dark_theme = not st.session_state.dark_theme
            st.rerun()
    
    st.divider()
    st.header("📊 Reporte Completo del Meta")
    
    # Filters
    col_filter1, col_filter2, col_filter3 = st.columns(3)
    with col_filter1:
        min_games_filter = st.slider("Mínimo de partidas", 10, 200, 50, 10)
    with col_filter2:
        order_by_filter = st.selectbox(
            "Ordenar por",
            options=['top4_rate', 'top1_rate', 'play_count', 'avg_placement'],
            format_func=lambda x: {'top4_rate': 'Top 4 Rate', 'top1_rate': 'Top 1 Rate', 'play_count': 'Play Rate', 'avg_placement': 'Avg Placement'}[x]
        )
    with col_filter3:
        limit_filter = st.number_input("Número de comps", min_value=5, max_value=50, value=20)
    
    # Fetch data
    try:
        top_comps_full = get_top_comps(limit=int(limit_filter), min_games=min_games_filter, order_by=order_by_filter)
        
        if top_comps_full:
            table_data = []
            for idx, comp in enumerate(top_comps_full, 1):
                formatted = format_comp_for_display(comp)
                table_data.append({
                    '#': idx,
                    'Composición': formatted['comp_name'],
                    'Partidas': formatted['games'],
                    'Top 4%': formatted['top4_rate'],
                    'Top 1%': formatted['top1_rate'],
                    'Avg Place': formatted['avg_placement']
                })
            
            df = pd.DataFrame(table_data)
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("No se encontraron composiciones con los filtros seleccionados.")
    except Exception as e:
        st.error(f"Error al cargar el reporte: {str(e)}")


# ============================================================
# DASHBOARD VIEW
# ============================================================
def render_dashboard():
    """Render the main dashboard view"""
    # Theme toggle
    col_header, col_toggle = st.columns([9, 1])
    with col_toggle:
        if st.button("🌙" if not st.session_state.dark_theme else "☀️", key="theme_toggle"):
            st.session_state.dark_theme = not st.session_state.dark_theme
            st.rerun()
    
    # Render appropriate theme
    if st.session_state.dark_theme:
        render_dark_theme_css()
    else:
        render_light_theme_css()
    
    # Header
    st.markdown('<div class="main-header">', unsafe_allow_html=True)
    st.markdown('<div class="main-title">🎮 TFT Meta Assistant</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Analiza el Meta y tu Rendimiento en Teamfight Tactics</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Get meta summary
    try:
        meta_summary = get_meta_summary()
        has_meta_data = meta_summary['total_matches'] > 0
    except:
        has_meta_data = False
        meta_summary = {'total_matches': 0, 'total_players': 0, 'viable_comps': 0, 'newest_match': None}
    
    # Stats cards
    if has_meta_data:
        st.markdown("### 📊 Estadísticas del Meta Actual")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f'<div class="stat-card"><div class="stat-number">{meta_summary["total_matches"]:,}</div><div class="stat-label">Partidas Analizadas</div></div>', unsafe_allow_html=True)
        with col2:
            st.markdown(f'<div class="stat-card"><div class="stat-number">{meta_summary["total_players"]}</div><div class="stat-label">Jugadores GM+ Tracked</div></div>', unsafe_allow_html=True)
        with col3:
            st.markdown(f'<div class="stat-card"><div class="stat-number">{meta_summary["viable_comps"]}</div><div class="stat-label">Comps Viables</div></div>', unsafe_allow_html=True)
        with col4:
            last_update = meta_summary['newest_match'].strftime('%d/%m/%Y') if meta_summary['newest_match'] else "N/A"
            st.markdown(f'<div class="stat-card"><div class="stat-number">🔄</div><div class="stat-label">Última actualización<br>{last_update}</div></div>', unsafe_allow_html=True)
    
    # Search bar
    st.markdown('<div class="search-container">', unsafe_allow_html=True)
    st.markdown("### 🔍 Buscar Summoner")
    
    region = st.selectbox("Región", options=list(REGIONS.keys()), index=0, format_func=lambda x: f"{x.upper()} - {REGIONS[x]}")
    
    # Auto-detect routing
    if region in ['euw1', 'eune1', 'tr1', 'ru']:
        routing = 'europe'
    elif region in ['na1', 'br1', 'la1', 'la2']:
        routing = 'americas'
    elif region in ['kr', 'jp1']:
        routing = 'asia'
    else:
        routing = 'sea'
    
    col_name, col_tag = st.columns(2)
    with col_name:
        game_name = st.text_input("Game Name", placeholder="Iyuster")
    with col_tag:
        tag_line = st.text_input("Tagline", placeholder="TETON")
    
    num_matches = st.slider("Número de partidas a analizar", min_value=5, max_value=20, value=10)
    search_button = st.button("🔍 Buscar Summoner", use_container_width=True, type="primary")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Search handler
    if search_button and game_name and tag_line:
        st.query_params.update({
            'summoner': game_name,
            'tag': tag_line,
            'region': region,
            'routing': routing,
            'matches': num_matches
        })
        st.rerun()
    
    # Top 3 compositions
    if has_meta_data:
        st.markdown("### 🔥 Top 3 Composiciones del Meta")
        
        try:
            top_comps = get_top_comps(limit=3, min_games=30, order_by='top4_rate')
            
            if top_comps:
                for idx, comp in enumerate(top_comps, 1):
                    formatted = format_comp_for_display(comp)
                    col_rank, col_content = st.columns([1, 9])
                    
                    with col_rank:
                        colors = {1: "#FFD700, #FFA500", 2: "#C0C0C0, #A0A0A0", 3: "#CD7F32, #B8860B"}
                        st.markdown(f'<div style="background: linear-gradient(135deg, {colors[idx]}); color: white; border-radius: 50%; width: 45px; height: 45px; display: inline-flex; align-items: center; justify-content: center; font-weight: 800; font-size: 1.3rem;">{idx}</div>', unsafe_allow_html=True)
                    
                    with col_content:
                        st.markdown(f'''<div class="comp-card">
                            <h4 style="margin: 0 0 0.5rem 0;">{formatted["comp_name"]}</h4>
                            <div style="display: flex; gap: 2rem;">
                                <div><strong>Partidas:</strong> {formatted["games"]}</div>
                                <div><strong>Top 4:</strong> <span style="color: #4CAF50;">{formatted["top4_rate"]}</span></div>
                                <div><strong>Top 1:</strong> <span style="color: #FFD700;">{formatted["top1_rate"]}</span></div>
                                <div><strong>Avg:</strong> {formatted["avg_placement"]}</div>
                            </div>
                        </div>''', unsafe_allow_html=True)
        except Exception as e:
            st.info("No hay suficientes datos para mostrar composiciones todavía.")
        
        # View full report button
        st.markdown("<br>", unsafe_allow_html=True)
        col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 1])
        with col_btn2:
            if st.button("📊 Ver Reporte Completo del Meta", use_container_width=True, type="secondary"):
                st.query_params.update({'view': 'meta_report'})
                st.rerun()


# ============================================================
# MAIN ROUTING
# ============================================================
query_params = st.query_params
viewing_summoner = 'summoner' in query_params
viewing_meta = query_params.get('view') == 'meta_report'

# Apply theme CSS globally based on session state
if st.session_state.dark_theme:
    render_dark_theme_css()
else:
    render_light_theme_css()

if viewing_summoner:
    # Summoner profile view
    summoner_name = query_params.get('summoner', '')
    summoner_tag = query_params.get('tag', '')
    summoner_region = query_params.get('region', 'euw1')
    routing = query_params.get('routing', 'europe')
    num_matches_param = int(query_params.get('matches', 10))
    
    render_summoner_profile(summoner_name, summoner_tag, summoner_region, routing, num_matches_param)

elif viewing_meta:
    # Meta report view
    render_meta_report()

else:
    # Dashboard view
    render_dashboard()
