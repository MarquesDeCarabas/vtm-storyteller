"""
Database Migration Script for VTM Storyteller
Ensures all required columns exist in the characters table
"""

import sqlite3
import os

def migrate_database(db_path='vtm_storyteller.db'):
    """Migrate database to support PDF character uploads"""
    
    print(f"🔄 Starting database migration for: {db_path}")
    
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    # Get existing columns
    c.execute("PRAGMA table_info(characters)")
    existing_columns = {row[1] for row in c.fetchall()}
    print(f"✓ Existing columns: {existing_columns}")
    
    # Define all required columns with their types
    required_columns = {
        'name': 'TEXT',
        'chronicle_id': 'INTEGER',
        'clan': 'TEXT',
        'concept': 'TEXT',
        'attributes': 'TEXT',  # JSON
        'skills': 'TEXT',  # JSON
        'disciplines': 'TEXT',  # JSON
        'backgrounds': 'TEXT',  # JSON
        'health_max': 'INTEGER DEFAULT 3',
        'willpower_max': 'INTEGER DEFAULT 3',
        'humanity': 'INTEGER DEFAULT 7',
        'hunger': 'INTEGER DEFAULT 1',
        'resonance': 'TEXT',
        'blood_potency': 'INTEGER DEFAULT 0',
        'generation': 'INTEGER DEFAULT 13',
        'blood_surge': 'TEXT',
        'power_bonus': 'TEXT',
        'mend_amount': 'TEXT',
        'rouse_reroll': 'TEXT',
        'bane_severity': 'TEXT',
        'clan_bane': 'TEXT',
        'clan_compulsion': 'TEXT',
        'ambition': 'TEXT',
        'desire': 'TEXT',
        'sect': 'TEXT',
        'rank_title': 'TEXT',
        'pdf_path': 'TEXT',
        'pdf_upload_date': 'TIMESTAMP',
        'pdf_hash': 'TEXT'
    }
    
    # Add missing columns
    added_count = 0
    for column_name, column_type in required_columns.items():
        if column_name not in existing_columns:
            try:
                sql = f"ALTER TABLE characters ADD COLUMN {column_name} {column_type}"
                c.execute(sql)
                conn.commit()
                print(f"✓ Added column: {column_name} ({column_type})")
                added_count += 1
            except sqlite3.OperationalError as e:
                print(f"✗ Failed to add column {column_name}: {e}")
    
    if added_count == 0:
        print("✓ All required columns already exist")
    else:
        print(f"✓ Added {added_count} new columns")
    
    # Verify final schema
    c.execute("PRAGMA table_info(characters)")
    final_columns = {row[1] for row in c.fetchall()}
    print(f"✓ Final column count: {len(final_columns)}")
    
    conn.close()
    print("✅ Database migration completed successfully")

if __name__ == '__main__':
    migrate_database()

