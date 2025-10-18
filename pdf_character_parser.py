"""
PDF Character Parser for VTM 5e Character Sheets - Version 2
Improved field name mappings for official VTM 5e character sheet
"""

import PyPDF2
import pdfplumber
import re
import json
from datetime import datetime
import hashlib


class VTMCharacterParser:
    """Parser for VTM 5e character sheet PDFs"""
    
    # Field name mappings for official VTM 5e character sheet
    ATTRIBUTE_FIELDS = {
        'strength': 'Str',
        'dexterity': 'Dex',
        'stamina': 'Sta',
        'charisma': 'Cha',
        'manipulation': 'Man',
        'composure': 'Com',
        'intelligence': 'Int',
        'wits': 'Wit',
        'resolve': 'Res'
    }
    
    SKILL_FIELDS = {
        'athletics': 'Ath',
        'brawl': 'Bra',
        'craft': 'Cra',
        'drive': 'Dri',
        'firearms': 'Fri',
        'larceny': 'Lar',
        'melee': 'Mel',
        'stealth': 'Ste',
        'survival': 'Sur',
        'animal_ken': 'AniKen',
        'etiquette': 'Etiq',
        'insight': 'Ins',
        'intimidation': 'Inti',
        'leadership': 'Lead',
        'performance': 'Perf',
        'persuasion': 'Pers',
        'streetwise': 'Stree',
        'subterfuge': 'Subt',
        'academics': 'Acad',
        'awareness': 'Awar',
        'finance': 'Fina',
        'investigation': 'Inve',
        'medicine': 'Med',
        'occult': 'Occu',
        'politics': 'Poli',
        'science': 'Scie',
        'technology': 'Tech'
    }
    
    def __init__(self, pdf_path):
        """Initialize parser with PDF path"""
        self.pdf_path = pdf_path
        self.data = self._initialize_data_structure()
        
    def _initialize_data_structure(self):
        """Initialize empty character data structure"""
        return {
            # Basic Info
            'name': '',
            'player': '',
            'chronicle': '',
            'clan': '',
            'predator_type': '',
            'ambition': '',
            'desire': '',
            'sect': '',
            'rank_title': '',
            'concept': '',
            'sire': '',
            'generation': 13,
            
            # Attributes (0-5 dots each)
            'attributes': {
                'strength': 0,
                'dexterity': 0,
                'stamina': 0,
                'charisma': 0,
                'manipulation': 0,
                'composure': 0,
                'intelligence': 0,
                'wits': 0,
                'resolve': 0
            },
            
            # Skills (0-5 dots each)
            'skills': {
                'athletics': 0,
                'brawl': 0,
                'craft': 0,
                'drive': 0,
                'firearms': 0,
                'larceny': 0,
                'melee': 0,
                'stealth': 0,
                'survival': 0,
                'animal_ken': 0,
                'etiquette': 0,
                'insight': 0,
                'intimidation': 0,
                'leadership': 0,
                'performance': 0,
                'persuasion': 0,
                'streetwise': 0,
                'subterfuge': 0,
                'academics': 0,
                'awareness': 0,
                'finance': 0,
                'investigation': 0,
                'medicine': 0,
                'occult': 0,
                'politics': 0,
                'science': 0,
                'technology': 0
            },
            
            # Disciplines
            'disciplines': {},
            
            # Backgrounds/Advantages
            'backgrounds': {},
            
            # Core Stats
            'health_max': 3,
            'willpower_max': 3,
            'humanity': 7,
            'hunger': 1,
            'resonance': '',
            
            # Blood
            'blood_potency': 0,
            'blood_surge': '',
            'power_bonus': '',
            'mend_amount': '',
            'rouse_reroll': '',
            'bane_severity': '',
            
            # Clan specifics
            'clan_bane': '',
            'clan_compulsion': '',
            
            # Metadata
            'pdf_hash': '',
            'extraction_date': datetime.now().isoformat()
        }
    
    def parse(self):
        """Main parsing method"""
        print(f"✓ Parsing PDF: {self.pdf_path}")
        
        # Calculate PDF hash
        self.data['pdf_hash'] = self._calculate_pdf_hash()
        
        # Extract form fields
        try:
            self._extract_form_fields()
            print("✓ Form fields extracted successfully")
        except Exception as e:
            print(f"✗ Form field extraction failed: {e}")
        
        # Validate extracted data
        self._validate_data()
        
        return self.data
    
    def _calculate_pdf_hash(self):
        """Calculate SHA256 hash of PDF file"""
        sha256_hash = hashlib.sha256()
        with open(self.pdf_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    
    def _extract_form_fields(self):
        """Extract data from PDF form fields"""
        with open(self.pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            
            if not hasattr(pdf_reader, 'get_fields'):
                print("✗ PDF reader does not support form field extraction")
                return
                
            fields = pdf_reader.get_fields()
            if not fields or not isinstance(fields, dict):
                print("✗ No form fields found")
                return
            
            print(f"✓ Found {len(fields)} form fields in PDF")
            
            # Helper function to safely get field value
            def get_field_value(field_name):
                try:
                    field = fields.get(field_name, {})
                    if isinstance(field, dict):
                        value = field.get('/V', '')
                        # Handle indirect objects
                        if hasattr(value, 'get_object'):
                            value = value.get_object()
                        return str(value) if value else ''
                    return ''
                except Exception as e:
                    return ''
            
            # Extract basic info
            self.data['name'] = get_field_value('Name') or get_field_value('Character Name')
            self.data['player'] = get_field_value('Player')
            self.data['chronicle'] = get_field_value('Chronicle')
            self.data['clan'] = get_field_value('Clan')
            self.data['predator_type'] = get_field_value('Predator type')
            self.data['ambition'] = get_field_value('Ambition')
            self.data['desire'] = get_field_value('Desire')
            self.data['sect'] = get_field_value('Sect')
            self.data['concept'] = get_field_value('Concept')
            self.data['sire'] = get_field_value('Sire')
            
            print(f"✓ Basic info extracted: {self.data['name']} ({self.data['clan']})")
            
            # Extract attributes using correct field names
            attrs_found = 0
            for attr_name, field_prefix in self.ATTRIBUTE_FIELDS.items():
                dots = self._count_filled_checkboxes(fields, field_prefix)
                if dots > 0:
                    self.data['attributes'][attr_name] = dots
                    attrs_found += 1
            
            print(f"✓ Attributes extracted: {attrs_found}/9")
            
            # Extract skills using correct field names
            skills_found = 0
            for skill_name, field_prefix in self.SKILL_FIELDS.items():
                dots = self._count_filled_checkboxes(fields, field_prefix)
                if dots > 0:
                    self.data['skills'][skill_name] = dots
                    skills_found += 1
            
            print(f"✓ Skills extracted: {skills_found}/27")
            
            # Extract disciplines
            for i in range(1, 10):
                disc_name = get_field_value(f'Disc{i}')
                if disc_name:
                    dots = self._count_filled_checkboxes(fields, f'Disc{i}')
                    self.data['disciplines'][disc_name] = dots
            
            # Extract backgrounds
            for i in range(1, 10):
                bg_name = get_field_value(f'Background{i}')
                if bg_name:
                    dots = self._count_filled_checkboxes(fields, f'Background{i}')
                    self.data['backgrounds'][bg_name] = dots
            
            # Extract blood potency
            bp_dots = self._count_filled_checkboxes(fields, 'BloodPotency')
            if bp_dots > 0:
                self.data['blood_potency'] = bp_dots
            
            # Extract humanity
            humanity_dots = self._count_filled_checkboxes(fields, 'Humanity')
            if humanity_dots > 0:
                self.data['humanity'] = humanity_dots
            
            # Extract willpower
            wp_dots = self._count_filled_checkboxes(fields, 'Willpower')
            if wp_dots > 0:
                self.data['willpower_max'] = wp_dots
            
            # Extract health
            health_dots = self._count_filled_checkboxes(fields, 'Health')
            if health_dots > 0:
                self.data['health_max'] = health_dots
    
    def _count_filled_checkboxes(self, fields, field_prefix):
        """Count how many checkboxes are filled for a given field prefix"""
        count = 0
        for i in range(1, 11):  # Check up to 10 dots (some fields go higher)
            field_name = f"{field_prefix}-{i}"
            if field_name in fields:
                try:
                    field = fields[field_name]
                    if isinstance(field, dict):
                        value = field.get('/V', '')
                        # Handle indirect objects
                        if hasattr(value, 'get_object'):
                            value = value.get_object()
                        # Check if checkbox is marked
                        if value in ['/Yes', '/On', 'Yes', 'On', True, '1', 1]:
                            count += 1
                except:
                    continue
        return count
    
    def _validate_data(self):
        """Validate extracted data and apply defaults"""
        # Ensure name is not empty
        if not self.data['name']:
            self.data['name'] = f"Character_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Ensure chronicle is not empty
        if not self.data['chronicle']:
            self.data['chronicle'] = "Default Chronicle"
        
        # Ensure clan is not empty
        if not self.data['clan']:
            self.data['clan'] = "Unknown"
        
        # Validate attribute ranges (0-5)
        for attr in self.data['attributes']:
            if self.data['attributes'][attr] < 0:
                self.data['attributes'][attr] = 0
            elif self.data['attributes'][attr] > 5:
                self.data['attributes'][attr] = 5
        
        # Validate skill ranges (0-5)
        for skill in self.data['skills']:
            if self.data['skills'][skill] < 0:
                self.data['skills'][skill] = 0
            elif self.data['skills'][skill] > 5:
                self.data['skills'][skill] = 5
        
        print(f"✓ Data validation complete")
    
    def get_summary(self):
        """Get a summary of extracted data for display"""
        attrs_count = sum(1 for v in self.data['attributes'].values() if v > 0)
        skills_count = sum(1 for v in self.data['skills'].values() if v > 0)
        discs_count = len(self.data['disciplines'])
        
        return {
            'name': self.data['name'],
            'clan': self.data['clan'],
            'chronicle': self.data['chronicle'],
            'attributes_found': attrs_count,
            'skills_found': skills_count,
            'disciplines_found': discs_count,
            'warnings': self._get_warnings()
        }
    
    def _get_warnings(self):
        """Get list of warnings about missing or incomplete data"""
        warnings = []
        
        attrs_count = sum(1 for v in self.data['attributes'].values() if v > 0)
        if attrs_count == 0:
            warnings.append("No attributes found in PDF. Please ensure the PDF is filled out correctly.")
        elif attrs_count < 9:
            warnings.append(f"Only {attrs_count}/9 attributes found. Some may be missing.")
        
        skills_count = sum(1 for v in self.data['skills'].values() if v > 0)
        if skills_count == 0:
            warnings.append("No skills found in PDF. Please ensure the PDF is filled out correctly.")
        
        return warnings

