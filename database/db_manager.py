"""
Database Manager - CRUD operations and database initialization
"""
from sqlalchemy import create_engine, desc, and_, func, Integer
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime, timedelta
from typing import List, Optional, Dict
import os
import sys

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from database.models import Base, Player, Match, Participant, Composition, MetaStat
from config import DATABASE_URL


class DatabaseManager:
    """Gestor de base de datos para TFT Meta Tracker"""
    
    def __init__(self, db_url: str = DATABASE_URL):
        self.engine = create_engine(db_url, echo=False)
        self.SessionLocal = sessionmaker(bind=self.engine)
    
    def init_db(self):
        """Crear todas las tablas en la base de datos"""
        Base.metadata.create_all(self.engine)
        print("✓ Base de datos inicializada correctamente")
    
    def get_session(self) -> Session:
        """Obtener una sesión de base de datos"""
        return self.SessionLocal()
    
    # ========== PLAYER OPERATIONS ==========
    
    def add_player(self, puuid: str, game_name: str, tag_line: str, 
                   tier: str, rank: str, lp: int, region: str) -> Player:
        """Añadir o actualizar un jugador"""
        session = self.get_session()
        try:
            # Check if player exists
            player = session.query(Player).filter_by(puuid=puuid).first()
            
            if player:
                # Update existing player
                player.game_name = game_name
                player.tag_line = tag_line
                player.tier = tier
                player.rank = rank
                player.lp = lp
                player.region = region
                player.last_updated = datetime.utcnow()
            else:
                # Create new player
                player = Player(
                    puuid=puuid,
                    game_name=game_name,
                    tag_line=tag_line,
                    tier=tier,
                    rank=rank,
                    lp=lp,
                    region=region
                )
                session.add(player)
            
            session.commit()
            session.refresh(player)
            return player
        finally:
            session.close()
    
    def get_player(self, puuid: str) -> Optional[Player]:
        """Obtener un jugador por PUUID"""
        session = self.get_session()
        try:
            return session.query(Player).filter_by(puuid=puuid).first()
        finally:
            session.close()
    
    def get_all_players(self, region: Optional[str] = None) -> List[Player]:
        """Obtener todos los jugadores, opcionalmente filtrados por región"""
        session = self.get_session()
        try:
            query = session.query(Player)
            if region:
                query = query.filter_by(region=region)
            return query.all()
        finally:
            session.close()
    
    # ========== MATCH OPERATIONS ==========
    
    def add_match(self, match_data: Dict) -> Optional[Match]:
        """Añadir una partida completa con participantes y composiciones"""
        session = self.get_session()
        try:
            # Check if match already exists
            existing = session.query(Match).filter_by(match_id=match_data['match_id']).first()
            if existing:
                return existing  # Already in database
            
            # Convert timestamp to datetime
            game_datetime = datetime.fromtimestamp(match_data['game_datetime'] / 1000)
            
            # Create match
            match = Match(
                match_id=match_data['match_id'],
                game_datetime=game_datetime,
                game_length=match_data.get('game_length', 0),
                tft_set_number=match_data.get('tft_set_number', 0),
                patch=match_data.get('patch', 'unknown'),
                region=match_data.get('region', 'unknown')
            )
            session.add(match)
            session.flush()  # Get match.id
            
            # Add participants and compositions
            for p_data in match_data.get('participants', []):
                # Get or find player
                player = session.query(Player).filter_by(puuid=p_data['puuid']).first()
                
                participant = Participant(
                    match_id=match.id,
                    player_id=player.id if player else None,
                    puuid=p_data['puuid'],
                    placement=p_data['placement'],
                    level=p_data.get('level', 0),
                    gold_left=p_data.get('gold_left', 0),
                    total_damage_to_players=p_data.get('total_damage_to_players', 0),
                    players_eliminated=p_data.get('players_eliminated', 0),
                    time_eliminated=p_data.get('time_eliminated', 0.0)
                )
                session.add(participant)
                session.flush()  # Get participant.id
                
                # Add composition
                comp_signature = self._generate_comp_signature(p_data.get('traits', []))
                
                composition = Composition(
                    participant_id=participant.id,
                    traits=p_data.get('traits', []),
                    units=p_data.get('units', []),
                    augments=p_data.get('augments', []),
                    comp_signature=comp_signature
                )
                session.add(composition)
            
            session.commit()
            session.refresh(match)
            return match
        except Exception as e:
            session.rollback()
            print(f"Error adding match: {e}")
            return None
        finally:
            session.close()
    
    def match_exists(self, match_id: str) -> bool:
        """Check if a match already exists in the database"""
        session = self.get_session()
        try:
            return session.query(Match).filter_by(match_id=match_id).first() is not None
        finally:
            session.close()
    
    def get_recent_matches(self, limit: int = 100, region: Optional[str] = None) -> List[Match]:
        """Obtener las partidas más recientes"""
        session = self.get_session()
        try:
            query = session.query(Match).order_by(desc(Match.game_datetime))
            if region:
                query = query.filter_by(region=region)
            return query.limit(limit).all()
        finally:
            session.close()
    
    def get_match_count(self) -> int:
        """Get total number of matches in database"""
        session = self.get_session()
        try:
            return session.query(Match).count()
        finally:
            session.close()
    
    # ========== COMPOSITION OPERATIONS ==========
    
    def _generate_comp_signature(self, traits: List[Dict]) -> str:
        """
        Generate a unique signature for a composition based on main traits
        Only includes traits with 3+ units (active traits)
        """
        if not traits:
            return "unknown"
        
        # Filter active traits (3+ units) and sort by number of units
        active_traits = [
            t for t in traits 
            if isinstance(t, dict) and t.get('num_units', 0) >= 3
        ]
        
        if not active_traits:
            return "unknown"
        
        # Sort by num_units descending, then by name for consistency
        sorted_traits = sorted(
            active_traits,
            key=lambda t: (-t.get('num_units', 0), t.get('name', ''))
        )
        
        # Take top 3 traits
        top_traits = sorted_traits[:3]
        
        # Create signature: "TraitName(count)+TraitName(count)+..."
        signature_parts = [
            f"{t.get('name', 'unknown')}({t.get('num_units', 0)})"
            for t in top_traits
        ]
        
        return "+".join(signature_parts)
    
    def get_compositions_by_signature(self, comp_signature: str) -> List[Composition]:
        """Get all compositions matching a signature"""
        session = self.get_session()
        try:
            return session.query(Composition).filter_by(comp_signature=comp_signature).all()
        finally:
            session.close()
    
    # ========== META STATS OPERATIONS ==========
    
    def calculate_meta_stats(self, min_games: int = 50, patch: Optional[str] = None, 
                            region: Optional[str] = None) -> List[MetaStat]:
        """
        Calculate meta statistics for all compositions
        Groups by comp_signature and calculates aggregate stats
        """
        session = self.get_session()
        try:
            # Build query
            query = session.query(
                Composition.comp_signature,
                func.count(Composition.id).label('play_count'),
                func.avg(Participant.placement).label('avg_placement'),
                func.sum(func.cast(Participant.placement <= 4, Integer)).label('top4_count'),
                func.sum(func.cast(Participant.placement == 1, Integer)).label('top1_count')
            ).join(Participant).join(Match)
            
            # Apply filters
            if patch:
                query = query.filter(Match.patch == patch)
            if region:
                query = query.filter(Match.region == region)
            
            # Group and filter
            query = query.group_by(Composition.comp_signature)\
                         .having(func.count(Composition.id) >= min_games)
            
            results = query.all()
            
            # Create or update MetaStat entries
            meta_stats = []
            for row in results:
                comp_sig, play_count, avg_place, top4_count, top1_count = row
                
                if comp_sig == "unknown":
                    continue
                
                top4_rate = (top4_count / play_count) if play_count > 0 else 0
                top1_rate = (top1_count / play_count) if play_count > 0 else 0
                
                # Get or create meta stat
                meta_stat = session.query(MetaStat).filter_by(
                    comp_signature=comp_sig,
                    patch=patch or "all",
                    region=region or "ALL"
                ).first()
                
                if not meta_stat:
                    meta_stat = MetaStat(
                        comp_signature=comp_sig,
                        patch=patch or "all",
                        region=region or "ALL"
                    )
                    session.add(meta_stat)
                
                # Update stats
                meta_stat.play_count = play_count
                meta_stat.avg_placement = avg_place
                meta_stat.top4_rate = top4_rate
                meta_stat.top1_rate = top1_rate
                meta_stat.last_calculated = datetime.utcnow()
                
                meta_stats.append(meta_stat)
            
            session.commit()
            return meta_stats
        finally:
            session.close()
    
    def get_top_comps(self, limit: int = 20, min_games: int = 50, 
                     patch: Optional[str] = None, region: Optional[str] = None,
                     order_by: str = 'top4_rate') -> List[MetaStat]:
        """Get top compositions ordered by specified metric"""
        session = self.get_session()
        try:
            query = session.query(MetaStat)\
                           .filter(MetaStat.play_count >= min_games)
            
            if patch:
                query = query.filter_by(patch=patch)
            if region:
                query = query.filter_by(region=region)
            
            # Order by metric
            if order_by == 'top4_rate':
                query = query.order_by(desc(MetaStat.top4_rate))
            elif order_by == 'top1_rate':
                query = query.order_by(desc(MetaStat.top1_rate))
            elif order_by == 'play_count':
                query = query.order_by(desc(MetaStat.play_count))
            elif order_by == 'avg_placement':
                query = query.order_by(MetaStat.avg_placement)  # Lower is better
            
            return query.limit(limit).all()
        finally:
            session.close()
    
    # ========== UTILITY OPERATIONS ==========
    
    def clear_old_data(self, days: int = 30):
        """Delete data older than specified days"""
        session = self.get_session()
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            deleted = session.query(Match)\
                            .filter(Match.game_datetime < cutoff_date)\
                            .delete()
            session.commit()
            print(f"✓ Deleted {deleted} matches older than {days} days")
        finally:
            session.close()
    
    def get_database_stats(self) -> Dict:
        """Get statistics about the database"""
        session = self.get_session()
        try:
            return {
                'total_players': session.query(Player).count(),
                'total_matches': session.query(Match).count(),
                'total_compositions': session.query(Composition).count(),
                'total_meta_stats': session.query(MetaStat).count(),
                'oldest_match': session.query(func.min(Match.game_datetime)).scalar(),
                'newest_match': session.query(func.max(Match.game_datetime)).scalar(),
            }
        finally:
            session.close()


# Global instance
db_manager = DatabaseManager()


if __name__ == "__main__":
    # Initialize database if run directly
    print("Initializing database...")
    db_manager.init_db()
    print("Database ready!")
