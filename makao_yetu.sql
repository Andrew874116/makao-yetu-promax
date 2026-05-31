-- ============================================================
--  MAKAO YETU DATABASE  |  makao_yetu.sql
--  Run this file in phpMyAdmin or MySQL CLI:
--  mysql -u root -p < makao_yetu.sql
-- ============================================================

CREATE DATABASE IF NOT EXISTS makao_yetu
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE makao_yetu;

-- ─── TABLE 1: USERS ──────────────────────────────────────────
CREATE TABLE IF NOT EXISTS users (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    username    VARCHAR(80)  NOT NULL,
    email       VARCHAR(120) NOT NULL UNIQUE,
    password    VARCHAR(256) NOT NULL,
    phone       VARCHAR(20)  NOT NULL,
    role        ENUM('user','agent','admin') DEFAULT 'user',
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- ─── TABLE 2: PROPERTIES ─────────────────────────────────────
CREATE TABLE IF NOT EXISTS properties (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    title       VARCHAR(150)  NOT NULL,
    location    VARCHAR(120)  NOT NULL,
    price       DECIMAL(15,2) NOT NULL,
    prop_type   ENUM('rent','sale','land') DEFAULT 'rent',
    bedrooms    INT DEFAULT 1,
    bathrooms   INT DEFAULT 1,
    description TEXT,
    image       VARCHAR(255),
    user_id     INT NOT NULL,
    is_available TINYINT(1) DEFAULT 1,
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- ─── TABLE 3: BOOKINGS / TRANSACTIONS ────────────────────────
CREATE TABLE IF NOT EXISTS bookings (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    user_id         INT NOT NULL,
    property_id     INT NOT NULL,
    amount          DECIMAL(15,2) NOT NULL,
    phone           VARCHAR(20),
    payment_method  ENUM('mpesa','card','cash') DEFAULT 'mpesa',
    mpesa_ref       VARCHAR(30),
    status          ENUM('pending','confirmed','cancelled') DEFAULT 'pending',
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id)     REFERENCES users(id)      ON DELETE CASCADE,
    FOREIGN KEY (property_id) REFERENCES properties(id) ON DELETE CASCADE
);

-- ─── SEED DATA ────────────────────────────────────────────────
-- Demo agent user  (password: agent123)
INSERT INTO users (username, email, password, phone, role) VALUES
('Kamau Agent', 'kamau@makao.co.ke',
 'pbkdf2:sha256:600000$demo$5b722b307fce6c944905d132693e5573823b6a0e5bbb47e2e1e98e1e1e1e1e1',
 '0712345678', 'agent');

-- Demo properties
INSERT INTO properties (title, location, price, prop_type, bedrooms, bathrooms, description, user_id) VALUES
('Cosy Bedsitter', 'Rongai, Nairobi', 8500.00, 'rent', 1, 1,
 'A modern bedsitter with all amenities in a secure gated estate. Walking distance from Rongai stage.', 1),

('1-Bedroom Apartment', 'Westlands, Nairobi', 22000.00, 'rent', 1, 1,
 'Spacious 1-bedroom in the heart of Westlands. Parking, 24hr security, borehole water included.', 1),

('2-Bedroom House', 'Kitengela', 35000.00, 'rent', 2, 2,
 'Family house in a quiet Kitengela estate with a small garden and ample parking.', 1),

('3-Bedroom Apartment', 'Ruiru', 45000.00, 'rent', 3, 2,
 'Modern 3-bedroom apartment with fibre internet, backup generator and swimming pool access.', 1),

('5-Bedroom House', 'Konza City', 12500000.00, 'sale', 5, 4,
 'Stunning 5-bedroom family home in Konza City with a large compound, servant quarters and borehole.', 1),

('7-Bedroom Mansion', 'Mwembetayari', 28000000.00, 'sale', 7, 5,
 'Luxury mansion with a swimming pool, gym, and landscaped garden. Price negotiable.', 1),

('3-Bedroom Mansionate', 'Kileleshwa, Nairobi', 18500000.00, 'sale', 3, 3,
 'Prime Kileleshwa property. Tarmac access, electric fence, DSQ included.', 1),

('Prime Plot – 1/8 Acre', 'Athi River', 1200000.00, 'land', 0, 0,
 'Ready title deed. Near Athi River EPZ. Ideal for residential construction.', 1);
