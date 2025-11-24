"""
Database models for TFT Meta Tracker
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON, Text, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()


class Player(Base):
    """Jugadores GM+ que estamos trackeando"""
    __tablename__ = 'players'
    
    id = Column(Integer, primary_key=True)
    puuid = Column(String(78), unique=True, nullable=False, index=True)
    game_name = Column(String(100))
    tag_line = Column(String(20))
    tier = Column(String(20))  # CHALLENGER, GRANDMASTER
    rank = Column(String(10))  # I, II, III, IV
    lp = Column(Integer, default=0)
    region = Column(String(10), nullable=False)
    last_updated = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    participants = relationship("Participant", back_populates="player")
    
    def __repr__(self):
        return f"<Player {self.game_name}#{self.tag_line} ({self.tier})>"


class Match(Base):
    """Partidas recopiladas"""
    __tablename__ = 'matches'
    
    id = Column(Integer, primary_key=True)
    match_id = Column(String(50), unique=True, nullable=False, index=True)
    game_datetime = Column(DateTime, nullable=False, index=True)
    game_length = Column(Float)  # Segundos
    tft_set_number = Column(Integer)
    patch = Column(String(20))  # e.g., "13.24"
    region = Column(String(10))
    
    # Relationship
    participants = relationship("Participant", back_populates="match")
    
    __table_args__ = (
        Index('idx_match_datetime_region', 'game_datetime', 'region'),
    )
    
    def __repr__(self):
        return f"<Match {self.match_id} on {self.patch}>"


class Participant(Base):
    """Participante en una partida (link entre player y match)"""
    __tablename__ = 'participants'
    
    id = Column(Integer, primary_key=True)
    match_id = Column(Integer, ForeignKey('matches.id'), nullable=False, index=True)
    player_id = Column(Integer, ForeignKey('players.id'), nullable=True, index=True)  # Puede ser null si no tracked
    puuid = Column(String(78), nullable=False)  # Para jugadores no tracked
    
    # Game stats
    placement = Column(Integer, nullable=False)
    level = Column(Integer)
    gold_left = Column(Integer)
    total_damage_to_players = Column(Integer)
    players_eliminated = Column(Integer)
    time_eliminated = Column(Float)
    
    # Relationships
    match = relationship("Match", back_populates="participants")
    player = relationship("Player", back_populates="participants")
    composition = relationship("Composition", back_populates="participant", uselist=False)
    
    __table_args__ = (
        Index('idx_participant_placement', 'placement'),
    )
    
    def __repr__(self):
        return f"<Participant placement={self.placement}>"


class Composition(Base):
    """Composición jugada por un participante"""
    __tablename__ = 'compositions'
    
    id = Column(Integer, primary_key=True)
    participant_id = Column(Integer, ForeignKey('participants.id'), nullable=False, unique=True)
    
    # Composition data (stored as JSON)
    traits = Column(JSON)  # List of trait objects
    units = Column(JSON)   # List of unit objects
    augments = Column(JSON)  # List of augment names
    
    # Composition signature for grouping similar comps
    comp_signature = Column(String(200), index=True)
    
    # Relationship
    participant = relationship("Participant", back_populates="composition")
    
    def __repr__(self):
        return f"<Composition {self.comp_signature}>"


class MetaStat(Base):
    """Estadísticas agregadas de composiciones (meta)"""
    __tablename__ = 'meta_stats'
    
    id = Column(Integer, primary_key=True)
    comp_signature = Column(String(200), unique=True, nullable=False, index=True)
    
    # Descriptive info
    primary_traits = Column(JSON)  # Main traits that define this comp
    common_units = Column(JSON)    # Most common units in this comp
    common_augments = Column(JSON)  # Most common augments
    
    # Statistics
    play_count = Column(Integer, default=0)
    avg_placement = Column(Float)
    top4_rate = Column(Float)  # % of games that placed top 4
    top1_rate = Column(Float)  # % of games that won
    
    # Metadata
    patch = Column(String(20))  # Patch these stats are for
    region = Column(String(10))  # Region filter (or 'ALL')
    last_calculated = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_meta_top4_rate', 'top4_rate'),
        Index('idx_meta_play_count', 'play_count'),
    )
    
    def __repr__(self):
        return f"<MetaStat {self.comp_signature} (top4: {self.top4_rate:.1%})>"
