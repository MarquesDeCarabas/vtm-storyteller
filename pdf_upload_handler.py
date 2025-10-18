"""
PDF Upload Handler for VTM Character Sheets
Handles PDF upload, parsing, and Chronicle linking
"""

import os
import sqlite3
import json
from datetime import datetime
from werkzeug.utils import secure_filename
from pdf_character_parser import VTMCharacterParser


class PDFUploadHandler:
    """Handles PDF character sheet uploads"""
    
    UPLOAD_FOLDER = 'uploads/characters'
    ALLOWED_EXTENSIONS = {'pdf'}
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    
    def __init__(self, db_path='vtm_storyteller.db'):
        """Initialize handler with database path"""
        self.db_path = db_path
        self._ensure_upload_directory()
        self._ensure_database_schema()
    
    def _ensure_upload_directory(self):
        """Ensure upload directory exists"""
        os.makedirs(self.UPLOAD_FOLDER, exist_ok=True)
    
    def _ensure_database_schema(self):
        """Ensure database has all required columns for PDF characters"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Add columns if they don't exist
        columns_to_add = [
            ('pdf_path', 'TEXT'),
            ('pdf_upload_date', 'TIMESTAMP'),
            ('pdf_hash', 'TEXT'),
            ('blood_potency', 'INTEGER DEFAULT 0'),
            ('generation', 'INTEGER DEFAULT 13'),
            ('humanity', 'INTEGER DEFAULT 7'),
            ('hunger', 'INTEGER DEFAULT 1'),
            ('willpower_max', 'INTEGER DEFAULT 3'),
            ('health_max', 'INTEGER DEFAULT 3'),
            ('resonance', 'TEXT'),
            ('blood_surge', 'TEXT'),
            ('power_bonus', 'TEXT'),
            ('mend_amount', 'TEXT'),
            ('rouse_reroll', 'TEXT'),
            ('bane_severity', 'TEXT'),
            ('clan_bane', 'TEXT'),
            ('clan_compulsion', 'TEXT'),
            ('ambition', 'TEXT'),
            ('desire', 'TEXT'),
            ('sect', 'TEXT'),
            ('rank_title', 'TEXT'),
            ('chronicle_id', 'INTEGER')
        ]
        
        for column_name, column_type in columns_to_add:
            try:
                c.execute(f"ALTER TABLE characters ADD COLUMN {column_name} {column_type}")
                conn.commit()
                print(f"✓ Added column: {column_name}")
            except sqlite3.OperationalError:
                # Column already exists
                pass
        
        conn.close()
    
    def allowed_file(self, filename):
        """Check if file extension is allowed"""
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in self.ALLOWED_EXTENSIONS
    
    def save_uploaded_file(self, file, character_name=None):
        """
        Save uploaded PDF file to disk.
        
        Args:
            file: FileStorage object from Flask request
            character_name: Optional character name for filename
            
        Returns:
            str: Path to saved file
        """
        if not file or not self.allowed_file(file.filename):
            raise ValueError("Invalid file type. Only PDF files are allowed.")
        
        # Generate secure filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        if character_name:
            base_name = secure_filename(character_name)
            filename = f"{base_name}_{timestamp}.pdf"
        else:
            filename = f"character_{timestamp}.pdf"
        
        filepath = os.path.join(self.UPLOAD_FOLDER, filename)
        
        # Save file
        file.save(filepath)
        
        return filepath
    
    def parse_pdf(self, pdf_path):
        """
        Parse PDF and extract character data.
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            dict: Parsed character data
        """
        parser = VTMCharacterParser(pdf_path)
        data = parser.parse()
        
        # Get warnings
        warnings = parser._get_warnings()
        
        return data, warnings
    
    def find_or_create_chronicle(self, chronicle_name):
        """
        Find existing Chronicle (campaign) or create new one.
        
        Args:
            chronicle_name: Name of the Chronicle
            
        Returns:
            int: Chronicle/campaign ID
        """
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Check if Chronicle exists in campaigns table
        c.execute("SELECT id FROM campaigns WHERE name = ?", (chronicle_name,))
        result = c.fetchone()
        
        if result:
            chronicle_id = result[0]
            print(f"✓ Found existing Chronicle: {chronicle_name} (ID: {chronicle_id})")
        else:
            # Create new Chronicle
            c.execute('''INSERT INTO campaigns (name, description, created_at)
                        VALUES (?, ?, ?)''',
                     (chronicle_name, f"Chronicle created from PDF upload", datetime.now()))
            chronicle_id = c.lastrowid
            conn.commit()
            print(f"✓ Created new Chronicle: {chronicle_name} (ID: {chronicle_id})")
        
        conn.close()
        return chronicle_id
    
    def save_character_to_database(self, character_data, pdf_path):
        """
        Save parsed character data to database.
        
        Args:
            character_data: Parsed character data dictionary
            pdf_path: Path to the PDF file
            
        Returns:
            int: Character ID
        """
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Find or create Chronicle
        chronicle_id = self.find_or_create_chronicle(character_data['chronicle'])
        
        # Prepare data for insertion
        attributes_json = json.dumps(character_data['attributes'])
        skills_json = json.dumps(character_data['skills'])
        disciplines_json = json.dumps(character_data['disciplines'])
        backgrounds_json = json.dumps(character_data['backgrounds'])
        
        # Insert character
        c.execute('''
            INSERT INTO characters (
                name, chronicle_id, clan, concept,
                attributes, skills, disciplines, backgrounds,
                health_max, willpower_max, humanity, hunger, resonance,
                blood_potency, generation,
                blood_surge, power_bonus, mend_amount, rouse_reroll, bane_severity,
                clan_bane, clan_compulsion,
                ambition, desire, sect, rank_title,
                pdf_path, pdf_upload_date, pdf_hash
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            character_data['name'],
            chronicle_id,
            character_data['clan'],
            character_data['predator_type'],  # Using predator_type as concept
            attributes_json,
            skills_json,
            disciplines_json,
            backgrounds_json,
            character_data['health_max'],
            character_data['willpower_max'],
            character_data['humanity'],
            character_data['hunger'],
            character_data['resonance'],
            character_data['blood_potency'],
            character_data['generation'],
            character_data['blood_surge'],
            character_data['power_bonus'],
            character_data['mend_amount'],
            character_data['rouse_reroll'],
            character_data['bane_severity'],
            character_data['clan_bane'],
            character_data['clan_compulsion'],
            character_data['ambition'],
            character_data['desire'],
            character_data['sect'],
            character_data['rank_title'],
            pdf_path,
            datetime.now(),
            character_data['pdf_hash']
        ))
        
        character_id = c.lastrowid
        conn.commit()
        conn.close()
        
        print(f"✓ Character saved to database (ID: {character_id})")
        return character_id
    
    def update_character_from_pdf(self, character_id, character_data, pdf_path):
        """
        Update existing character from new PDF upload.
        
        Args:
            character_id: ID of character to update
            character_data: Parsed character data dictionary
            pdf_path: Path to the new PDF file
            
        Returns:
            bool: True if successful
        """
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Prepare data
        attributes_json = json.dumps(character_data['attributes'])
        skills_json = json.dumps(character_data['skills'])
        disciplines_json = json.dumps(character_data['disciplines'])
        backgrounds_json = json.dumps(character_data['backgrounds'])
        
        # Update character
        c.execute('''
            UPDATE characters SET
                clan = ?,
                concept = ?,
                attributes = ?,
                skills = ?,
                disciplines = ?,
                backgrounds = ?,
                health_max = ?,
                willpower_max = ?,
                humanity = ?,
                hunger = ?,
                resonance = ?,
                blood_potency = ?,
                generation = ?,
                blood_surge = ?,
                power_bonus = ?,
                mend_amount = ?,
                rouse_reroll = ?,
                bane_severity = ?,
                clan_bane = ?,
                clan_compulsion = ?,
                ambition = ?,
                desire = ?,
                sect = ?,
                rank_title = ?,
                pdf_path = ?,
                pdf_upload_date = ?,
                pdf_hash = ?
            WHERE id = ?
        ''', (
            character_data['clan'],
            character_data['predator_type'],
            attributes_json,
            skills_json,
            disciplines_json,
            backgrounds_json,
            character_data['health_max'],
            character_data['willpower_max'],
            character_data['humanity'],
            character_data['hunger'],
            character_data['resonance'],
            character_data['blood_potency'],
            character_data['generation'],
            character_data['blood_surge'],
            character_data['power_bonus'],
            character_data['mend_amount'],
            character_data['rouse_reroll'],
            character_data['bane_severity'],
            character_data['clan_bane'],
            character_data['clan_compulsion'],
            character_data['ambition'],
            character_data['desire'],
            character_data['sect'],
            character_data['rank_title'],
            pdf_path,
            datetime.now(),
            character_data['pdf_hash'],
            character_id
        ))
        
        conn.commit()
        conn.close()
        
        print(f"✓ Character updated (ID: {character_id})")
        return True
    
    def handle_upload(self, file, character_id=None):
        """
        Handle complete PDF upload workflow.
        
        Args:
            file: FileStorage object from Flask request
            character_id: Optional ID of existing character to update
            
        Returns:
            dict: Result with character_id, data, and any errors
        """
        try:
            # Save file
            pdf_path = self.save_uploaded_file(file)
            print(f"✓ PDF saved: {pdf_path}")
            
            # Parse PDF
            character_data, errors = self.parse_pdf(pdf_path)
            print(f"✓ PDF parsed")
            
            if errors:
                print(f"⚠ Validation errors: {errors}")
            
            # Save or update character
            if character_id:
                # Update existing character
                self.update_character_from_pdf(character_id, character_data, pdf_path)
                result_character_id = character_id
                action = 'updated'
            else:
                # Create new character
                result_character_id = self.save_character_to_database(character_data, pdf_path)
                action = 'created'
            
            return {
                'success': True,
                'character_id': result_character_id,
                'action': action,
                'data': character_data,
                'errors': errors,
                'pdf_path': pdf_path
            }
            
        except Exception as e:
            print(f"✗ Error handling upload: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_character_pdf_path(self, character_id):
        """
        Get PDF path for a character.
        
        Args:
            character_id: Character ID
            
        Returns:
            str: Path to PDF file, or None if not found
        """
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute("SELECT pdf_path FROM characters WHERE id = ?", (character_id,))
        result = c.fetchone()
        
        conn.close()
        
        return result[0] if result else None


# Utility function for Flask integration
def create_upload_handler(db_path='vtm_storyteller.db'):
    """Create and return a PDFUploadHandler instance"""
    return PDFUploadHandler(db_path)

