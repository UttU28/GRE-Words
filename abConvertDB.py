import json
import sqlite3
import os
import time
from datetime import datetime

# Path to the JSON file and SQLite database
JSON_FILE = os.path.join("resources", "words_cleaned.json")
DB_FILE = os.path.join("resources", "gre_words.db")

def create_database():
    """Create the SQLite database with the required tables"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Create words table with video tracking fields
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS words (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        word TEXT NOT NULL UNIQUE,
        meaning TEXT NOT NULL,
        clips_found INTEGER DEFAULT 0,
        video_created BOOLEAN DEFAULT 0,
        video_uploaded BOOLEAN DEFAULT 0,
        upload_time TEXT
    )
    ''')
    
    # Create clips table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS clips (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        word_id INTEGER NOT NULL,
        clip_index INTEGER NOT NULL,
        video_url TEXT NOT NULL,
        subtitle TEXT,
        video_info TEXT,
        video_start_height INTEGER,
        FOREIGN KEY (word_id) REFERENCES words(id),
        UNIQUE(word_id, clip_index)
    )
    ''')
    
    # Create indexes
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_word ON words(word)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_word_id ON clips(word_id)')
    
    conn.commit()
    return conn

def load_json_data():
    """Load data from the JSON file"""
    try:
        with open(JSON_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except Exception as e:
        print(f"Error loading JSON data: {e}")
        return None

def populate_database(conn, data):
    """Populate the database with data from the JSON file"""
    cursor = conn.cursor()
    
    words_count = 0
    clips_count = 0
    
    try:
        # Process each word
        for word, word_data in data.items():
            # Insert word into words table
            cursor.execute('''
            INSERT INTO words (word, meaning, clips_found)
            VALUES (?, ?, ?)
            ''', (
                word,
                word_data.get('meaning', ''),
                word_data.get('clipsFound', 0)
            ))
            
            word_id = cursor.lastrowid
            words_count += 1
            
            # Process clips for this word
            if 'clipData' in word_data and word_data['clipData']:
                for clip_index, clip_info in word_data['clipData'].items():
                    video_start_height = clip_info.get('videoStartHeight', None)
                    
                    cursor.execute('''
                    INSERT INTO clips (word_id, clip_index, video_url, subtitle, video_info, video_start_height)
                    VALUES (?, ?, ?, ?, ?, ?)
                    ''', (
                        word_id,
                        int(clip_index),
                        clip_info.get('videoURL', ''),
                        clip_info.get('subtitle', ''),
                        clip_info.get('videoInfo', ''),
                        video_start_height
                    ))
                    
                    clips_count += 1
            
            # Commit after each word to avoid losing all data if an error occurs
            conn.commit()
            
    except Exception as e:
        print(f"Error populating database: {e}")
        conn.rollback()
        return False
    
    print(f"Database populated successfully.")
    print(f"Imported {words_count} words and {clips_count} clips.")
    return True

def main():
    """Main function to convert JSON to SQLite"""
    start_time = time.time()
    
    print(f"Converting JSON data from {JSON_FILE} to SQLite database {DB_FILE}")
    
    # Check if JSON file exists
    if not os.path.exists(JSON_FILE):
        print(f"Error: JSON file {JSON_FILE} not found")
        return
    
    # Create database
    conn = create_database()
    
    # Load JSON data
    data = load_json_data()
    if data is None:
        conn.close()
        return
    
    # Populate database
    success = populate_database(conn, data)
    
    # Close connection
    conn.close()
    
    # Print results
    end_time = time.time()
    execution_time = end_time - start_time
    
    if success:
        print(f"Conversion completed in {execution_time:.2f} seconds")
    else:
        print("Conversion failed")

if __name__ == "__main__":
    main() 