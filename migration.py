#!/usr/bin/env python3
"""
Complete manual migration script.
Creates database, schema, and loads data from JSON.
"""

import os
import json
import sqlite3
from pathlib import Path

def create_database():
    """Create database and schema."""
    db_path = "problems.db"
    
    # Remove existing database if you want a fresh start
    if os.path.exists(db_path):
        response = input(f"Database {db_path} already exists. Delete and recreate? (y/n): ")
        if response.lower() == 'y':
            os.remove(db_path)
            print(f"✅ Deleted existing {db_path}")
        else:
            print("Using existing database")
    
    # Create connection
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create table
    print("Creating problems table...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS problems (
            id TEXT PRIMARY KEY,
            text TEXT NOT NULL,
            topic TEXT NOT NULL,
            difficulty INTEGER NOT NULL CHECK (difficulty >= 1 AND difficulty <= 5),
            estimated_time_to_solve_minutes INTEGER NOT NULL CHECK (estimated_time_to_solve_minutes > 0)
        )
    """)
    
    # Create indexes
    print("Creating indexes...")
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_topic_difficulty 
        ON problems(topic, difficulty)
    """)
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_topic 
        ON problems(topic)
    """)
    
    conn.commit()
    print("✅ Database schema created")
    
    return conn, cursor

def load_problems(conn, cursor, json_file):
    """Load problems from JSON file."""
    if not os.path.exists(json_file):
        print(f"❌ Error: JSON file not found: {json_file}")
        return 0, 0
    
    print(f"Loading problems from {json_file}...")
    
    with open(json_file, 'r', encoding='utf-8') as f:
        problems_data = json.load(f)
    
    loaded = 0
    skipped = 0
    
    for problem_data in problems_data:
        try:
            # Validate required fields
            required = ['id', 'text', 'topic', 'difficulty', 'estimated_time_to_solve_minutes']
            if not all(field in problem_data for field in required):
                skipped += 1
                continue
            
            # Validate difficulty
            if not (1 <= problem_data['difficulty'] <= 5):
                skipped += 1
                continue
            
            # Check if exists
            cursor.execute("SELECT id FROM problems WHERE id = ?", (problem_data['id'],))
            if cursor.fetchone():
                skipped += 1
                continue
            
            # Insert
            cursor.execute(
                """INSERT INTO problems (id, text, topic, difficulty, estimated_time_to_solve_minutes)
                   VALUES (?, ?, ?, ?, ?)""",
                (
                    problem_data['id'],
                    problem_data['text'],
                    problem_data['topic'],
                    problem_data['difficulty'],
                    problem_data['estimated_time_to_solve_minutes']
                )
            )
            loaded += 1
            
            if loaded % 100 == 0:
                print(f"  Loaded {loaded} problems...")
                
        except Exception as e:
            print(f"  Warning: Skipped problem {problem_data.get('id', 'unknown')}: {e}")
            skipped += 1
            continue
    
    conn.commit()
    return loaded, skipped

def verify_database(conn):
    """Verify database contents."""
    cursor = conn.cursor()
    
    # Count total
    cursor.execute("SELECT COUNT(*) FROM problems")
    total = cursor.fetchone()[0]
    
    # Count by topic
    cursor.execute("""
        SELECT topic, COUNT(*) as count 
        FROM problems 
        GROUP BY topic 
        ORDER BY count DESC
    """)
    topics = cursor.fetchall()
    
    # Count by difficulty
    cursor.execute("""
        SELECT difficulty, COUNT(*) as count 
        FROM problems 
        GROUP BY difficulty 
        ORDER BY difficulty
    """)
    difficulties = cursor.fetchall()
    
    print("\n" + "=" * 60)
    print("Database Verification")
    print("=" * 60)
    print(f"Total problems: {total}")
    print("\nBy Topic:")
    for topic, count in topics:
        print(f"  {topic}: {count}")
    print("\nBy Difficulty:")
    for difficulty, count in difficulties:
        print(f"  Level {difficulty}: {count}")
    print("=" * 60)

def main():
    """Main migration function."""
    print("=" * 60)
    print("Manual Database Migration Script")
    print("=" * 60)
    
    # Create database
    conn, cursor = create_database()
    
    # Load problems
    json_file = "ProblemSet (2) (3).json"
    loaded, skipped = load_problems(conn, cursor, json_file)
    
    print(f"\n✅ Migration complete!")
    print(f"   Loaded: {loaded} problems")
    print(f"   Skipped: {skipped} problems")
    
    # Verify
    verify_database(conn)
    
    # Close connection
    conn.close()
    print(f"\n✅ Database saved: problems.db")

if __name__ == "__main__":
    main()

