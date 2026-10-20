-- ============================================
-- ASSA Event Manager — PostgreSQL Schema
-- ============================================

-- Drop existing tables (in correct FK order)
DROP TABLE IF EXISTS feedback CASCADE;
DROP TABLE IF EXISTS bookings CASCADE;
DROP TABLE IF EXISTS events CASCADE;
DROP TABLE IF EXISTS users CASCADE;

-- ─── USERS ────────────────────────────────
CREATE TABLE users (
    uid          VARCHAR(36)  PRIMARY KEY,
    name         VARCHAR(100) NOT NULL,
    email        VARCHAR(150) NOT NULL UNIQUE,
    password_hash TEXT        NOT NULL,
    role         VARCHAR(20)  NOT NULL DEFAULT 'attendee'
                              CHECK (role IN ('admin', 'organizer', 'attendee')),
    created_at   TIMESTAMP    NOT NULL DEFAULT NOW()
);

-- ─── EVENTS ───────────────────────────────
CREATE TABLE events (
    event_id      SERIAL       PRIMARY KEY,
    organizer_uid VARCHAR(36)  NOT NULL REFERENCES users(uid) ON DELETE CASCADE,
    title         VARCHAR(200) NOT NULL,
    description   TEXT,
    date          TIMESTAMP    NOT NULL,
    location      VARCHAR(300) NOT NULL,
    price         NUMERIC(10,2) DEFAULT 0.00,
    category      VARCHAR(100) NOT NULL,
    capacity      INTEGER      DEFAULT 100,
    created_at    TIMESTAMP    NOT NULL DEFAULT NOW()
);

-- ─── BOOKINGS ─────────────────────────────
CREATE TABLE bookings (
    booking_id   SERIAL      PRIMARY KEY,
    uid          VARCHAR(36) NOT NULL REFERENCES users(uid) ON DELETE CASCADE,
    event_id     INTEGER     NOT NULL REFERENCES events(event_id) ON DELETE CASCADE,
    status       VARCHAR(20) NOT NULL DEFAULT 'pending'
                             CHECK (status IN ('paid', 'pending', 'cancelled')),
    booked_at    TIMESTAMP   NOT NULL DEFAULT NOW(),
    ticket_code  VARCHAR(50) NOT NULL UNIQUE,
    UNIQUE(uid, event_id)
);

-- ─── FEEDBACK ─────────────────────────────
CREATE TABLE feedback (
    feedback_id SERIAL      PRIMARY KEY,
    uid         VARCHAR(36) NOT NULL REFERENCES users(uid) ON DELETE CASCADE,
    event_id    INTEGER     NOT NULL REFERENCES events(event_id) ON DELETE CASCADE,
    rating      INTEGER     NOT NULL CHECK (rating BETWEEN 1 AND 5),
    comment     TEXT,
    sentiment   VARCHAR(20) DEFAULT 'neutral'
                            CHECK (sentiment IN ('positive', 'neutral', 'negative')),
    is_spam     BOOLEAN     DEFAULT FALSE,
    created_at  TIMESTAMP   NOT NULL DEFAULT NOW(),
    UNIQUE(uid, event_id)
);

-- ─── INDEXES ──────────────────────────────
CREATE INDEX idx_events_category   ON events(category);
CREATE INDEX idx_events_date       ON events(date);
CREATE INDEX idx_bookings_uid      ON bookings(uid);
CREATE INDEX idx_bookings_event_id ON bookings(event_id);
CREATE INDEX idx_feedback_event_id ON feedback(event_id);

-- No default administrator credentials are seeded. Create administrator users through a secure setup process.
