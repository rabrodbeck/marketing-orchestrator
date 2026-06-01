import os
import psycopg2
from dotenv import load_dotenv

# Load credentials from .env
load_dotenv()

DB_HOST = os.getenv("SUPABASE_DB_HOST") 
DB_NAME = os.getenv("SUPABASE_DB_NAME")
DB_USER = os.getenv("SUPABASE_DB_USER")
DB_PASS = os.getenv("SUPABASE_DB_PASS") 
DB_PORT = os.getenv("SUPABASE_DB_PORT")

def setup_supabase_database():
    print(f"Connecting to Supabase PostgresSQL at: {DB_HOST}...")

    # Establish connection using SSL mode
    conn = psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASS,
        port=DB_PORT,
        sslmode="require"
    )
    cursor = conn.cursor()

    # 1. Create tables
    print("Creating tables on Supabase...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS properties (
                   id varchar(50) PRIMARY KEY,
                   name varchar(255) NOT NULL,
                   totalUnits INTEGER NOT NULL,
                   occupiedUnits INTEGER NOT NULL
                   )
                   """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS marketing_spend (
                   propertyId VARCHAR(50) NOT NULL,
                   channel varchar(100) NOT NULL,
                   monthlySpend INTEGER NOT NULL,
                   FOREIGN KEY(propertyId) REFERENCES properties(id)
                   )
                   """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS lease_expirations (
                   id VARCHAR(50) PRIMARY KEY,
                   propertyId VARCHAR(50) NOT NULL,
                   unitType VARCHAR(100) NOT NULL,
                   expirationDate VARCHAR(50) NOT NULL,
                   monthlyRent INTEGER NOT NULL,
                   FOREIGN KEY(propertyId) references properties(id)
                   )
                   """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS occupancy_targets (
                   propertyId VARCHAR(50) PRIMARY KEY,
                   targetRate REAL NOT NULL,
                   FOREIGN KEY(propertyId) references properties(id)
                   )
                   """)
    
    # 2. Seed Data
    print("Seeding database tables...")

    cursor.execute("TRUNCATE TABLE properties CASCADE")
    cursor.executemany("INSERT INTO properties VALUES (%s, %s, %s, %s)", [
        ("prop-101", "Oakridge Luxury Apartments", 200, 194),
        ("prop-102", "Riverfront Micro-Lofts", 100, 95),
        ("prop-103", "Highland Heights Townhomes", 150, 120),
        ("prop-104", "Summit Ridge Apartments", 300, 291),
        ("prop-105", "Bella Vista Condos", 80, 78),
        ("prop-106", "Pinnacle Plaza Lofts", 250, 245)
    ])
    cursor.execute("TRUNCATE TABLE marketing_spend CASCADE")
    cursor.executemany("INSERT INTO marketing_spend VALUES (%s, %s, %s)", [
        ("prop-101", "Google Ads", 5400),
        ("prop-102", "ILS Listing", 3200),
        ("prop-103", "Google Ads", 6200),
        ("prop-104", "Google Ads", 6000),
        ("prop-105", "Meta Ads", 1200),
        ("prop-106", "Meta Ads", 4500)
    ])
    cursor.execute("TRUNCATE TABLE lease_expirations CASCADE")
    cursor.executemany("INSERT INTO lease_expirations VALUES (%s, %s, %s, %s, %s)", [
        ("lease-1", "prop-101", "2BR Luxury", "2026-06-15", 2800),
        ("lease-2", "prop-101", "1BR Classic", "2026-07-01", 2100),
        ("lease-3", "prop-102", "Studio Loft", "2026-06-30", 1800),
        ("lease-4", "prop-103", "3BR Townhome", "2026-06-10", 3200),
        ("lease-5", "prop-103", "2BR Townhome", "2026-07-15", 2600),
        ("lease-6", "prop-104", "1BR Standard", "2026-06-25", 1950),
        ("lease-7", "prop-104", "2BR Deluxe", "2026-08-01", 2500),
        ("lease-8", "prop-106", "2BR Penthouse", "2026-06-20", 4800)
    ])
    cursor.execute("TRUNCATE TABLE occupancy_targets CASCADE")
    cursor.executemany("INSERT INTO occupancy_targets VALUES (%s, %s)", [
        ("prop-101", 0.95),
        ("prop-102", 0.90),
        ("prop-103", 0.92),
        ("prop-104", 0.95),
        ("prop-105", 0.94),
        ("prop-106", 0.95)
    ])

    conn.commit()
    cursor.close()
    conn.close()
    print("Supabase PostgresSQL Database successfully seeded!")

if __name__ == "__main__":
    setup_supabase_database()
