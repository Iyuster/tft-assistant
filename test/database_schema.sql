-- Schema para PostgreSQL
-- Base de datos para almacenar partidas de TFT

CREATE TABLE matches (
    match_id VARCHAR(50) PRIMARY KEY,
    game_datetime TIMESTAMP,
    game_length FLOAT,
    tft_set_number INT,
    patch VARCHAR(20),
    region VARCHAR(10)
);

CREATE TABLE participants (
    id SERIAL PRIMARY KEY,
    match_id VARCHAR(50) REFERENCES matches(match_id),
    puuid VARCHAR(100),
    placement INT,
    level INT,
    gold_left INT,
    players_eliminated INT,
    total_damage_to_players INT,
    time_eliminated FLOAT
);

CREATE TABLE units (
    id SERIAL PRIMARY KEY,
    participant_id INT REFERENCES participants(id),
    character_id VARCHAR(50),
    tier INT,
    item_names TEXT[],  -- Array de items
    rarity INT
);

CREATE TABLE traits (
    id SERIAL PRIMARY KEY,
    participant_id INT REFERENCES participants(id),
    trait_name VARCHAR(50),
    num_units INT,
    tier_current INT,
    tier_total INT
);

CREATE TABLE augments (
    id SERIAL PRIMARY KEY,
    participant_id INT REFERENCES participants(id),
    augment_name VARCHAR(100)
);

-- Índices para queries rápidas
CREATE INDEX idx_matches_date ON matches(game_datetime);
CREATE INDEX idx_participants_placement ON participants(placement);
CREATE INDEX idx_participants_match ON participants(match_id);
