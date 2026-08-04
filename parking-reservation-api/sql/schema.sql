-- Parking Garage Reservation API schema
CREATE TABLE IF NOT EXISTS users (
    user_id       VARCHAR(100) PRIMARY KEY,
    email         VARCHAR(255) UNIQUE NOT NULL,
    full_name     VARCHAR(255) NOT NULL,
    phone         VARCHAR(20),
    password_hash VARCHAR(255) NOT NULL DEFAULT '',
    created_at    TIMESTAMP DEFAULT NOW(),
    is_active     BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_created_at ON users(created_at);

CREATE TABLE IF NOT EXISTS garages (
    garage_id       VARCHAR(100) PRIMARY KEY,
    name            VARCHAR(255) NOT NULL,
    address         VARCHAR(255) NOT NULL,
    spots_total     INTEGER NOT NULL DEFAULT 1,
    spots_available INTEGER NOT NULL DEFAULT 1,
    created_at      TIMESTAMP DEFAULT NOW(),
    CONSTRAINT check_spots_available_non_negative CHECK (spots_available >= 0),
    CONSTRAINT check_spots_total_non_negative CHECK (spots_total >= 0)
);

CREATE TABLE IF NOT EXISTS reservations (
    id               VARCHAR(36) PRIMARY KEY,
    user_id          VARCHAR(100) NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    garage_id        VARCHAR(100) NOT NULL REFERENCES garages(garage_id) ON DELETE CASCADE,
    license_plate    VARCHAR(20),
    idempotency_key  TEXT,
    status           VARCHAR(50) NOT NULL DEFAULT 'active',
    reserved_at      TIMESTAMP DEFAULT NOW(),
    released_at      TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_reservations_user_id ON reservations(user_id);
CREATE INDEX IF NOT EXISTS idx_reservations_garage_id ON reservations(garage_id);
CREATE INDEX IF NOT EXISTS idx_reservations_status ON reservations(status);
CREATE INDEX IF NOT EXISTS idx_reservations_idempotency_key ON reservations(idempotency_key);
