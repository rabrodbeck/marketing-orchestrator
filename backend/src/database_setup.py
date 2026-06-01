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

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS automated_actions (
                   id VARCHAR(50) PRIMARY KEY,
                   propertyId VARCHAR(50) NOT NULL,
                   insight TEXT NOT NULL,
                   recommendation TEXT NOT NULL,
                   proposedValue INTEGER NOT NULL,
                   status VARCHAR(50) NOT NULL,
                   version INTEGER NOT NULL,
                   createdAt VARCHAR(50) NOT NULL,
                   FOREIGN KEY(propertyId) references properties(id)
                   )
                   """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS actions_audit_log (
                   id VARCHAR(50) PRIMARY KEY,
                   actionId VARCHAR(50) NOT NULL,
                   propertyId VARCHAR(50) NOT NULL,
                   eventType VARCHAR(50) NOT NULL,
                   message TEXT NOT NULL,
                   timestamp VARCHAR(50) NOT NULL
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

    cursor.execute("TRUNCATE TABLE automated_actions CASCADE")
    cursor.executemany("INSERT INTO automated_actions VALUES (%s, %s, %s, %s, %s, %s, %s, %s)", [
        ("act-bbx08d2ci", "prop-101", "Oakridge Luxury Apartments matches high stability constraints at 97% occupancy, but marketing spend remains unthrottled at $5400/mo.", "Scale back channel budget by 50% to $2700/mo to safeguard operational margins.", 2700, "SUCCESS", 2, "2026-05-22T17:41:04.362Z"),
        ("act-7uwddl868", "prop-102", "Riverfront Micro-Lofts matches high stability constraints at 95% occupancy, but marketing spend remains unthrottled at $3200/mo.", "Scale back channel budget by 50% to $1600/mo to safeguard operational margins.", 1600, "PENDING", 1, "2026-05-22T17:41:04.363Z"),
        ("act-1nhc2ukfz", "prop-101", "Oakridge Luxury Apartments matches high stability constraints at 97% occupancy, but marketing spend remains unthrottled at $5400/mo.", "Scale back channel budget by 50% to $2700/mo to safeguard operational margins.", 2700, "SUCCESS", 2, "2026-05-29T16:17:40.687Z"),
        ("act-hvzn9u6jn", "prop-104", "Summit Ridge Apartments matches high stability constraints at 97% occupancy, but marketing spend remains unthrottled at $6000/mo.", "Scale back channel budget by 50% to $3000/mo to safeguard operational margins.", 3000, "PENDING", 1, "2026-05-29T16:18:32.127Z"),
        ("act-a61d1ku81", "prop-106", "Pinnacle Plaza Lofts matches high stability constraints at 98% occupancy, but marketing spend remains unthrottled at $4500/mo.", "Scale back channel budget by 50% to $2250/mo to safeguard operational margins.", 2250, "PENDING", 1, "2026-05-29T16:18:32.128Z"),
        ("act-970884", "prop-101", "Oakridge Luxury Apartments matches high stability constraints at 97% occupancy, but marketing spend remains unthrottled at $5400/mo.", "Scale back channel budget by 50% to $2700/mo to safeguard operational margins.", 2700, "SUCCESS", 2, "2026-06-01T16:21:30.146340Z")
    ])

    cursor.execute("TRUNCATE TABLE actions_audit_log CASCADE")

    conn.commit()
    cursor.close()
    conn.close()
    print("Supabase PostgresSQL Database successfully seeded with action tables!")

if __name__ == "__main__":
    setup_supabase_database()