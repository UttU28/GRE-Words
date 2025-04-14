import json
import sqlite3
import os
import time
from datetime import datetime

JSON_FILE = os.path.join("resources", "words_cleaned.json")
DB_FILE = os.path.join("resources", "greWords.db")

def createDatabase():
    """Create the SQLite database with the required tables"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
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
    
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_word ON words(word)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_word_id ON clips(word_id)')
    
    conn.commit()
    return conn

def loadJsonData():
    """Load data from the JSON file"""
    try:
        with open(JSON_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except Exception as e:
        print(f"Error loading JSON data: {e}")
        return None

def populateDatabase(conn, data):
    """Populate the database with data from the JSON file"""
    cursor = conn.cursor()
    
    wordsCount = 0
    clipsCount = 0
    
    try:
        for word, wordData in data.items():
            cursor.execute('''
            INSERT INTO words (word, meaning, clips_found)
            VALUES (?, ?, ?)
            ''', (
                word,
                wordData.get('meaning', ''),
                wordData.get('clipsFound', 0)
            ))
            
            wordId = cursor.lastrowid
            wordsCount += 1
            
            if 'clipData' in wordData and wordData['clipData']:
                for clipIndex, clipInfo in wordData['clipData'].items():
                    videoStartHeight = clipInfo.get('videoStartHeight', None)
                    
                    cursor.execute('''
                    INSERT INTO clips (word_id, clip_index, video_url, subtitle, video_info, video_start_height)
                    VALUES (?, ?, ?, ?, ?, ?)
                    ''', (
                        wordId,
                        int(clipIndex),
                        clipInfo.get('videoURL', ''),
                        clipInfo.get('subtitle', ''),
                        clipInfo.get('videoInfo', ''),
                        videoStartHeight
                    ))
                    
                    clipsCount += 1
            
            conn.commit()
            
    except Exception as e:
        print(f"Error populating database: {e}")
        conn.rollback()
        return False
    
    print(f"Database populated successfully.")
    print(f"Imported {wordsCount} words and {clipsCount} clips.")
    return True

def main():
    """Main function to convert JSON to SQLite"""
    startTime = time.time()
    
    print(f"Converting JSON data from {JSON_FILE} to SQLite database {DB_FILE}")
    
    if not os.path.exists(JSON_FILE):
        print(f"Error: JSON file {JSON_FILE} not found")
        return
    
    conn = createDatabase()
    
    data = loadJsonData()
    if data is None:
        conn.close()
        return
    
    success = populateDatabase(conn, data)
    
    conn.close()
    
    endTime = time.time()
    executionTime = endTime - startTime
    
    if success:
        print(f"Conversion completed in {executionTime:.2f} seconds")
    else:
        print("Conversion failed")

if __name__ == "__main__":
    main() 