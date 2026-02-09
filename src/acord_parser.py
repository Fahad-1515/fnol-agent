# fnol-agent/src/acord_parser.py
"""
Specialized parser for ACORD automobile loss notice forms
"""

import re
from typing import Dict, Any, Optional
from .field_extractor import FieldExtractor

class ACORDParser(FieldExtractor):
    """Specialized parser for ACORD 2 forms"""
    
    # ACORD-specific patterns
    ACORD_PATTERNS = {
        'policy_number': [
            # ACORD specific patterns
            r'POLICY\s*NUMBER\s*([A-Z0-9\-]+)',
            r'POLICY\s*#\s*([A-Z0-9\-]+)',
            r'NAIC\s*CODE.*?POLICY\s*NUMBER\s*([A-Z0-9\-]+)',
        ],
        
        'policyholder_name': [
            r'NAME\s*OF\s*INSURED\s*(?:\(First,\s*Middle,\s*Last\))?\s*([A-Z][A-Za-z\s,\.]+?(?=\s{2,}|\n|INSURED|CONTACT))',
            r'INSURED\s*NAME[:\s]*([A-Za-z\s\.,]+?)(?=\s{2,}|\n)',
        ],
        
        'date_of_loss': [
            r'DATE\s*OF\s*LOSS\s*AND\s*TIME\s*([0-9]{1,2}/[0-9]{1,2}/[0-9]{2,4})',
            r'DATE\s*OF\s*LOSS[:\s]*([0-9]{1,2}/[0-9]{1,2}/[0-9]{2,4})',
        ],
        
        'time_of_loss': [
            r'DATE\s*OF\s*LOSS\s*AND\s*TIME.*?([0-9]{1,2}:[0-9]{2}\s*[AP]M)',
            r'TIME\s*([0-9]{1,2}:[0-9]{2}\s*[AP]M)',
        ],
        
        'location': [
            r'LOCATION\s*OF\s*LOSS\s*(.*?)(?=POLICE\s*OR\s*FIRE|DESCRIBE\s*LOCATION)',
            r'STREET[:\s]*(.*?)(?=\n|CITY)',
            r'CITY,\s*STATE,\s*ZIP[:\s]*(.*?)(?=\n|REPORT)',
        ],
        
        'description': [
            r'DESCRIPTION\s*OF\s*ACCIDENT\s*(.*?)(?=1\.\s*WAS\s*A\s*STANDARD|Page\s*\d+|ACORD)',
            r'DESCRIBE\s*DAMAGE\s*(.*?)(?=\n\n|ESTIMATE\s*AMOUNT)',
        ],
        
        'estimate_amount': [
            r'ESTIMATE\s*AMOUNT[:\s]*\$?\s*([0-9,]+\.?[0-9]*)',
            r'Damage\s*Estimate[:\s]*\$?\s*([0-9,]+\.?[0-9]*)',
        ],
        
        'vin': [
            r'V\.I\.N\.\s*[:\s]*([A-Z0-9]{17})',
            r'VIN[:\s]*([A-Z0-9]{17})',
        ],
        
        'make': [
            r'MAKE[:\s]*([A-Za-z\s]+)(?=\n|MODEL|BODY)',
        ],
        
        'model': [
            r'MODEL[:\s]*([A-Za-z0-9\s]+)(?=\n|V\.I\.N\.)',
        ],
        
        'year': [
            r'YEAR\s*([0-9]{4})',
        ],
        
        'plate_number': [
            r'PLATE\s*NUMBER\s*([A-Z0-9\-\s]+)(?=\n|STATE)',
        ],
        
        'carrier': [
            r'CARRIER\s*([A-Za-z\s]+)(?=\n|NAIC)',
        ],
        
        'naic_code': [
            r'NAIC\s*CODE\s*([0-9]+)',
        ],
    }
    
    @classmethod
    def extract_acord_fields(cls, document_text: str) -> Dict[str, Any]:
        """
        Extract fields specifically from ACORD forms
        
        Args:
            document_text: Text from ACORD form
            
        Returns:
            Dictionary of extracted fields
        """
        results = {}
        
        # Clean the text - ACORD forms often have spacing issues
        text = cls._clean_acord_text(document_text)
        
        # Extract using ACORD-specific patterns
        for field, patterns in cls.ACORD_PATTERNS.items():
            value = cls._extract_with_patterns(text, patterns, field)
            if value:
                results[field] = value
        
        # Extract from tables if present
        results.update(cls._extract_from_acord_tables(text))
        
        # Post-process
        results = cls._post_process_acord_fields(results, text)
        
        return results
    
    @staticmethod
    def _clean_acord_text(text: str) -> str:
        """
        Clean ACORD form text which often has table formatting issues
        
        Args:
            text: Raw extracted text
            
        Returns:
            Cleaned text
        """
        if not text:
            return ""
        
        # Replace multiple spaces with single space, but preserve some structure
        text = re.sub(r' {2,}', '  ', text)  # Keep double spaces for field separation
        
        # Fix common OCR issues in ACORD forms
        replacements = {
            'l': 'I',
            '|': 'I',
            '１': '1',
            '２': '2',
            '３': '3',
            '４': '4',
            '５': '5',
            '６': '6',
            '７': '7',
            '８': '8',
            '９': '9',
            '０': '0',
            '．': '.',
            '，': ',',
            '；': ';',
            '：': ':',
            '（': '(',
            '）': ')',
            '［': '[',
            '］': ']',
            '｛': '{',
            '｝': '}',
            '＄': '$',
        }
        
        for old, new in replacements.items():
            text = text.replace(old, new)
        
        # Standardize field labels
        standardizations = {
            'POLICY NO': 'POLICY NUMBER',
            'POLICY#': 'POLICY NUMBER',
            'POL NO': 'POLICY NUMBER',
            'VEHICLE ID NUMBER': 'V.I.N.',
            'VEHICLE ID': 'V.I.N.',
            'ESTIMATED DAMAGES': 'ESTIMATE AMOUNT',
            'LOSS DATE': 'DATE OF LOSS',
            'INSUREDS NAME': 'NAME OF INSURED',
            'NAIC NO': 'NAIC CODE',
        }
        
        for old, new in standardizations.items():
            text = text.replace(old, new)
        
        return text
    
    @classmethod
    def _extract_from_acord_tables(cls, text: str) -> Dict[str, Any]:
        """
        Extract information from table-like structures in ACORD forms
        
        Args:
            text: Document text
            
        Returns:
            Dictionary of extracted table data
        """
        table_data = {}
        
        # Look for vehicle information table
        vehicle_section = cls._find_vehicle_section(text)
        if vehicle_section:
            # Extract year
            year_match = re.search(r'YEAR\s*([0-9]{4})', vehicle_section)
            if year_match:
                table_data['year'] = year_match.group(1)
            
            # Extract make
            make_match = re.search(r'MAKE[:\s]*([A-Za-z\s]+?)(?=\s{2,}|\n|MODEL|BODY)', vehicle_section)
            if make_match:
                table_data['make'] = make_match.group(1).strip()
            
            # Extract model
            model_match = re.search(r'MODEL[:\s]*([A-Za-z0-9\s]+?)(?=\s{2,}|\n|V\.I\.N\.)', vehicle_section)
            if model_match:
                table_data['model'] = model_match.group(1).strip()
            
            # Extract VIN
            vin_match = re.search(r'V\.I\.N\.\s*[:\s]*([A-Z0-9]{17})', vehicle_section)
            if vin_match:
                table_data['vin'] = vin_match.group(1)
            
            # Extract plate
            plate_match = re.search(r'PLATE\s*NUMBER\s*([A-Z0-9\-\s]+?)(?=\s{2,}|\n|STATE)', vehicle_section)
            if plate_match:
                table_data['plate_number'] = plate_match.group(1).strip()
        
        return table_data
    
    @staticmethod
    def _find_vehicle_section(text: str) -> Optional[str]:
        """
        Find the vehicle information section in ACORD text
        
        Args:
            text: Document text
            
        Returns:
            Vehicle section text or None
        """
        # Look for vehicle header pattern
        patterns = [
            r'VEH\s*#.*?DESCRIBE DAMAGE',
            r'VEHICLE INFORMATION.*?DESCRIBE DAMAGE',
            r'YEAR.*?DESCRIBE DAMAGE',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                return match.group(0)
        
        return None
    
    @classmethod
    def _post_process_acord_fields(cls, extracted: Dict[str, Any], full_text: str) -> Dict[str, Any]:
        """
        Post-process ACORD-specific fields
        
        Args:
            extracted: Dictionary of extracted fields
            full_text: Full document text
            
        Returns:
            Enhanced fields dictionary
        """
        # Ensure claim type is set
        if 'claim_type' not in extracted:
            extracted['claim_type'] = 'vehicle_damage'  # Default for ACORD auto forms
        
        # Look for injury mentions
        if 'description' in extracted:
            desc = extracted['description'].lower()
            injury_keywords = ['injury', 'injured', 'hurt', 'pain', 'hospital', 'ambulance']
            if any(keyword in desc for keyword in injury_keywords):
                extracted['claim_type'] = 'injury'
        
        # Look for estimate amount in various places
        if 'estimate_amount' not in extracted or not extracted['estimate_amount']:
            # Try alternative patterns
            patterns = [
                r'\$([0-9,]+\.?[0-9]*)\s*(?:estimate|damage|amount)',
                r'Amount[:\s]*\$?\s*([0-9,]+\.?[0-9]*)',
                r'([0-9,]+\.?[0-9]*)\s*dollars',
            ]
            
            for pattern in patterns:
                match = re.search(pattern, full_text, re.IGNORECASE)
                if match:
                    extracted['estimate_amount'] = cls._parse_amount(match.group(1))
                    break
        
        # Extract from the structured "ESTIMATE AMOUNT:" field if present
        if 'estimate_amount' not in extracted:
            # Look for the specific ACORD field format
            estimate_section = re.search(r'ESTIMATE AMOUNT[:\s]*(.*?)(?:\n|$)', full_text, re.IGNORECASE)
            if estimate_section:
                value = estimate_section.group(1).strip()
                if value:
                    extracted['estimate_amount'] = cls._parse_amount(value)
        
        return extracted
    
    @classmethod
    def parse_acord_document(cls, document_data: Dict) -> Dict[str, Any]:
        """
        Parse an ACORD document
        
        Args:
            document_data: Dictionary from DocumentLoader
            
        Returns:
            Dictionary of extracted fields
        """
        text = document_data.get('text', '')
        
        if not text:
            return {}
        
        # Use ACORD-specific extraction
        return cls.extract_acord_fields(text)