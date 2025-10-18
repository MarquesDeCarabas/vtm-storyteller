"""
PDF Character Parser for VTM 5e Character Sheets
Extracts character data from uploaded PDF character sheets
"""

import PyPDF2
import pdfplumber
import re
import json
from datetime import datetime
import hashlib


class VTMCharacterParser:
    """Parser for VTM 5e character sheet PDFs"""
    
    # Attribute names mapping
    ATTRIBUTES = {
        'physical': ['strength', 'dexterity', 'stamina'],
        'social': ['charisma', 'manipulation', 'composure'],
        'mental': ['intelligence', 'wits', 'resolve']
    }
    
    # Skill names mapping
    SKILLS = {
        'physical': ['athletics', 'brawl', 'craft', 'drive', 'firearms', 
                     'larceny', 'melee', 'stealth', 'survival'],
        'social': ['animal_ken', 'etiquette', 'insight', 'intimidation', 
                   'leadership', 'performance', 'persuasion', 'streetwise', 'subterfuge'],
        'mental': ['academics', 'awareness', 'finance', 'investigation', 
                   'medicine', 'occult', 'politics', 'science', 'technology']
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
            'generation': 13,
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
        """Main parsing method - tries multiple extraction strategies"""
        print(f"Parsing PDF: {self.pdf_path}")
        
        # Calculate PDF hash for duplicate detection
        self.data['pdf_hash'] = self._calculate_pdf_hash()
        
        # Strategy 1: Try to extract form fields (if PDF is fillable)
        try:
            self._extract_form_fields()
            print("✓ Form fields extracted")
        except Exception as e:
            print(f"⚠ Form field extraction failed: {e}")
        
        # Strategy 2: Extract text from PDF
        try:
            self._extract_text_data()
            print("✓ Text data extracted")
        except Exception as e:
            print(f"⚠ Text extraction failed: {e}")
        
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
        """Extract data from PDF form fields (if fillable)"""
        with open(self.pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            
            # Check if PDF has form fields
            if '/AcroForm' not in pdf_reader.trailer.get('/Root', {}):
                print("PDF does not contain fillable form fields")
                return
            
            # Get form fields
            fields = pdf_reader.get_fields()
            if not fields:
                print("No form fields found")
                return
            
            # Extract basic info
            self.data['name'] = fields.get('Name', {}).get('/V', '')
            self.data['player'] = fields.get('Player', {}).get('/V', '')
            self.data['chronicle'] = fields.get('Chronicle', {}).get('/V', '')
            self.data['clan'] = fields.get('Clan', {}).get('/V', '')
            self.data['predator_type'] = fields.get('Predator type', {}).get('/V', '')
            self.data['ambition'] = fields.get('Ambition', {}).get('/V', '')
            self.data['desire'] = fields.get('Desire', {}).get('/V', '')
            self.data['sect'] = fields.get('Sect', {}).get('/V', '')
            self.data['rank_title'] = fields.get('Rank/Title', {}).get('/V', '')
            
            # Extract attributes (look for checkbox patterns)
            for category, attrs in self.ATTRIBUTES.items():
                for attr in attrs:
                    # Try to find filled checkboxes for this attribute
                    dots = self._count_filled_checkboxes(fields, attr.capitalize())
                    if dots > 0:
                        self.data['attributes'][attr] = dots
            
            # Extract skills
            for category, skills in self.SKILLS.items():
                for skill in skills:
                    # Convert skill name to proper case
                    skill_display = skill.replace('_', ' ').title()
                    dots = self._count_filled_checkboxes(fields, skill_display)
                    if dots > 0:
                        self.data['skills'][skill] = dots
    
    def _count_filled_checkboxes(self, fields, field_prefix):
        """Count how many checkboxes are filled for a given field"""
        count = 0
        for i in range(1, 6):  # VTM uses 1-5 dots
            field_name = f"{field_prefix}_{i}"
            if field_name in fields:
                value = fields[field_name].get('/V', '')
                # Check if checkbox is marked (various possible values)
                if value in ['/Yes', '/On', 'Yes', 'On', True, '1']:
                    count += 1
        return count
    
    def _extract_text_data(self):
        """Extract data from PDF text (fallback method)"""
        with pdfplumber.open(self.pdf_path) as pdf:
            # Page 1: Basic info, attributes, skills
            if len(pdf.pages) > 0:
                page1_text = pdf.pages[0].extract_text()
                self._parse_page1_text(page1_text)
            
            # Page 2: Blood mechanics, disciplines
            if len(pdf.pages) > 1:
                page2_text = pdf.pages[1].extract_text()
                self._parse_page2_text(page2_text)
    
    def _parse_page1_text(self, text):
        """Parse text from page 1 (basic info, attributes, skills)"""
        lines = text.split('\n')
        
        # Try to extract basic info from first few lines
        for line in lines[:10]:
            # Look for "Name" field
            if 'Name' in line and not self.data['name']:
                # Extract text after "Name"
                match = re.search(r'Name\s+(.+?)(?:Player|$)', line)
                if match:
                    self.data['name'] = match.group(1).strip()
            
            # Look for "Chronicle" field
            if 'Chronicle' in line and not self.data['chronicle']:
                match = re.search(r'Chronicle\s+(.+?)(?:\s|$)', line)
                if match:
                    self.data['chronicle'] = match.group(1).strip()
            
            # Look for "Clan" field
            if 'Clan' in line and not self.data['clan']:
                match = re.search(r'Clan\s+(.+?)(?:Predator|$)', line)
                if match:
                    self.data['clan'] = match.group(1).strip()
    
    def _parse_page2_text(self, text):
        """Parse text from page 2 (blood mechanics, disciplines)"""
        # Look for Blood Potency
        match = re.search(r'Blood Potency.*?(\d+)', text)
        if match:
            self.data['blood_potency'] = int(match.group(1))
        
        # Look for Generation
        match = re.search(r'Generation.*?(\d+)', text)
        if match:
            self.data['generation'] = int(match.group(1))
    
    def _validate_data(self):
        """Validate extracted data and apply defaults"""
        # Ensure name is not empty
        if not self.data['name']:
            self.data['name'] = f"Character_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Ensure chronicle is not empty
        if not self.data['chronicle']:
            self.data['chronicle'] = "Default Chronicle"
        
        # Validate attribute ranges (0-5)
        for attr in self.data['attributes']:
            value = self.data['attributes'][attr]
            if not isinstance(value, int) or value < 0 or value > 5:
                self.data['attributes'][attr] = 0
        
        # Validate skill ranges (0-5)
        for skill in self.data['skills']:
            value = self.data['skills'][skill]
            if not isinstance(value, int) or value < 0 or value > 5:
                self.data['skills'][skill] = 0
        
        # Validate Blood Potency (0-10)
        if not (0 <= self.data['blood_potency'] <= 10):
            self.data['blood_potency'] = 0
        
        # Validate Humanity (0-10)
        if not (0 <= self.data['humanity'] <= 10):
            self.data['humanity'] = 7
    
    def get_validation_errors(self):
        """Get list of validation errors"""
        errors = []
        
        # Check required fields
        if not self.data['name']:
            errors.append("Character name is required")
        
        if not self.data['chronicle']:
            errors.append("Chronicle name is required")
        
        # Check if any attributes are set
        if all(v == 0 for v in self.data['attributes'].values()):
            errors.append("No attributes found in PDF. Please ensure the PDF is filled out correctly.")
        
        # Check if any skills are set
        if all(v == 0 for v in self.data['skills'].values()):
            errors.append("No skills found in PDF. Please ensure the PDF is filled out correctly.")
        
        return errors
    
    def to_json(self):
        """Convert parsed data to JSON string"""
        return json.dumps(self.data, indent=2)
    
    def get_summary(self):
        """Get human-readable summary of parsed character"""
        summary = f"""
Character Summary:
-----------------
Name: {self.data['name']}
Player: {self.data['player']}
Chronicle: {self.data['chronicle']}
Clan: {self.data['clan']}
Predator Type: {self.data['predator_type']}

Attributes:
  Physical: Strength {self.data['attributes']['strength']}, Dexterity {self.data['attributes']['dexterity']}, Stamina {self.data['attributes']['stamina']}
  Social: Charisma {self.data['attributes']['charisma']}, Manipulation {self.data['attributes']['manipulation']}, Composure {self.data['attributes']['composure']}
  Mental: Intelligence {self.data['attributes']['intelligence']}, Wits {self.data['attributes']['wits']}, Resolve {self.data['attributes']['resolve']}

Skills (non-zero):
"""
        # Add non-zero skills
        for skill, value in self.data['skills'].items():
            if value > 0:
                summary += f"  {skill.replace('_', ' ').title()}: {value}\n"
        
        summary += f"\nBlood Potency: {self.data['blood_potency']}\n"
        summary += f"Generation: {self.data['generation']}\n"
        summary += f"Humanity: {self.data['humanity']}\n"
        summary += f"Hunger: {self.data['hunger']}\n"
        
        return summary


# Utility functions

def parse_vtm_character_pdf(pdf_path):
    """
    Parse VTM 5e character sheet PDF and return character data.
    
    Args:
        pdf_path: Path to the PDF file
        
    Returns:
        dict: Parsed character data
    """
    parser = VTMCharacterParser(pdf_path)
    return parser.parse()


def validate_character_data(data):
    """
    Validate character data extracted from PDF.
    
    Args:
        data: Character data dictionary
        
    Returns:
        list: List of validation error messages (empty if valid)
    """
    parser = VTMCharacterParser("")
    parser.data = data
    return parser.get_validation_errors()


if __name__ == "__main__":
    # Test the parser
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python pdf_character_parser.py <pdf_file>")
        sys.exit(1)
    
    pdf_file = sys.argv[1]
    
    print(f"Parsing {pdf_file}...")
    parser = VTMCharacterParser(pdf_file)
    data = parser.parse()
    
    print("\n" + parser.get_summary())
    
    errors = parser.get_validation_errors()
    if errors:
        print("\n⚠ Validation Errors:")
        for error in errors:
            print(f"  - {error}")
    else:
        print("\n✓ Character data is valid")
    
    print(f"\nJSON output:\n{parser.to_json()}")

