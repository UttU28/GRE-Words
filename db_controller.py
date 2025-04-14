import os
import sqlite3
import random
import time
from datetime import datetime
from config import ensureDirsExist

DB_FILE = os.path.join("resources", "greWords.db")

class DBController:
    def __init__(self, dbPath=DB_FILE):
        """Initialize database controller with database path"""
        self.dbPath = dbPath
        ensureDirsExist()
        self._createConnection()
    
    def _createConnection(self):
        """Create a database connection"""
        self.conn = sqlite3.connect(self.dbPath)
        # Enable foreign keys
        self.conn.execute("PRAGMA foreign_keys = ON")
        # Return Row objects rather than tuples
        self.conn.row_factory = sqlite3.Row
    
    def close(self):
        """Close the database connection"""
        if hasattr(self, 'conn'):
            self.conn.close()
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, excType, excVal, excTb):
        """Context manager exit"""
        self.close()
    
    # Word-related functions
    def getWord(self, word):
        """Get a word's data by word string"""
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT * FROM words WHERE word = ?", 
            (word,)
        )
        return cursor.fetchone()
    
    def getWordById(self, wordId):
        """Get a word's data by ID"""
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT * FROM words WHERE id = ?", 
            (wordId,)
        )
        return cursor.fetchone()
    
    def getRandomWord(self):
        """Select a random word that hasn't been processed yet"""
        cursor = self.conn.cursor()
        cursor.execute(
            """
            SELECT * FROM words 
            WHERE clips_found > 4 
            AND video_created = 0
            ORDER BY RANDOM() 
            LIMIT 1
            """
        )
        return cursor.fetchone()
    
    def markWordAsProcessed(self, wordId):
        """Mark a word as processed (video created)"""
        
        cursor = self.conn.cursor()
        cursor.execute(
            """
            UPDATE words
            SET video_created = 1
            WHERE id = ?
            """,
            (wordId,)
        )
        self.conn.commit()
        return cursor.rowcount > 0
    
    def getWordMeaning(self, wordId):
        """Get the meaning of a word by ID"""
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT meaning FROM words WHERE id = ?",
            (wordId,)
        )
        result = cursor.fetchone()
        return result['meaning'] if result else None
    
    # Clips-related functions
    def getClipsForWord(self, wordId):
        """Get all clips for a specific word"""
        cursor = self.conn.cursor()
        cursor.execute(
            """
            SELECT * FROM clips
            WHERE word_id = ?
            ORDER BY clip_index
            """,
            (wordId,)
        )
        return cursor.fetchall()
    
    def getClipCount(self, wordId):
        """Get the number of clips for a word"""
        cursor = self.conn.cursor()
        cursor.execute(
            """
            SELECT COUNT(*) as count FROM clips
            WHERE word_id = ?
            """,
            (wordId,)
        )
        result = cursor.fetchone()
        return result['count'] if result else 0
    
    def updateClipVideoStartHeight(self, clipId, videoStartHeight):
        """Update the video start height for a clip"""
        cursor = self.conn.cursor()
        cursor.execute(
            """
            UPDATE clips
            SET video_start_height = ?
            WHERE id = ?
            """,
            (videoStartHeight, clipId)
        )
        self.conn.commit()
        return cursor.rowcount > 0
    
    def updateClipVideoStartHeightByIndex(self, wordId, clipIndex, videoStartHeight):
        """Update the video start height for a clip by word_id and clip_index"""
        cursor = self.conn.cursor()
        cursor.execute(
            """
            UPDATE clips
            SET video_start_height = ?
            WHERE word_id = ? AND clip_index = ?
            """,
            (videoStartHeight, wordId, clipIndex)
        )
        self.conn.commit()
        return cursor.rowcount > 0
    
    # Helper functions for script compatibility
    def getWordDataDict(self, word):
        """Get a word's data in a dictionary format similar to the original JSON structure"""
        wordRow = self.getWord(word)
        if not wordRow:
            return None
        
        wordId = wordRow['id']
        clips = self.getClipsForWord(wordId)
        
        # Convert to dictionary format similar to the old JSON structure
        clipData = {}
        for clip in clips:
            clipData[str(clip['clip_index'])] = {
                'videoURL': clip['video_url'],
                'subtitle': clip['subtitle'],
                'videoInfo': clip['video_info'],
                'videoStartHeight': clip['video_start_height']
            }
        
        return {
            'word': wordRow['word'],
            'meaning': wordRow['meaning'],
            'clipsFound': wordRow['clips_found'],
            'wordUsed': bool(wordRow['video_created']),
            'videoUploaded': bool(wordRow['video_uploaded']),
            'completedDate': wordRow['upload_time'],
            'clipData': clipData
        }

# Create a global instance for easy importing
db = DBController() 