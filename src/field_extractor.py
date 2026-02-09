# fnol-agent/src/field_extractor.py - UPDATED & FIXED VERSION
"""
Field extraction module for FNOL documents
"""

import re
import json
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
from .config import config

class FieldExtractor:
    """Extracts and validates fields from FNOL documents"""
    
    # UPDATED AND IMPROVED regex patterns
    PATTERNS = {
        # Policy Information - FIXED PATTERNS
        'policy_number': [
            # Match "Policy Number: AUTO-78901234" (on same line)
            r'Policy\s*Number[:\s]+([A-Z0-9\-_]+[A-Z0-9])(?=\s|$|\n)',
            # Match "POLICY NUMBER: AUTO-78901234" 
            r'POLICY\s*NUMBER[:\s]+([A-Z0-9\-_]+[A-Z0-9])(?=\s|$|\n)',
            # Match "Policy # AUTO-78901234"
            r'Policy\s*#[:\s]+([A-Z0-9\-_]+[A-Z0-9])(?=\s|$|\n)',
            # Match "POLICY: AUTO-78901234"
            r'POLICY[:\s]+([A-Z0-9\-_]+[A-Z0-9])(?=\s|$|\n)',
            # Generic pattern for policy numbers
            r'(?<=\bPolicy(?: Number|#| No\.?)?[:\s])([A-Z0-9\-_]+[A-Z0-9])',
        ],
        
        'policyholder_name': [
            # Match "Policyholder Name: Sarah Johnson" (exact)
            r'Policyholder\s*Name[:\s]+([A-Z][a-zA-Z\s]+?)(?=\s*\n|\s*$|\s*[A-Z])',
            # Match "NAME OF INSURED: John Smith"
            r'NAME\s*OF\s*INSURED[:\s]+([A-Z][a-zA-Z\s]+?)(?=\s*\n|\s*$)',
            # Match "Named Insured: John Smith"
            r'Named\s*Insured[:\s]+([A-Z][a-zA-Z\s]+?)(?=\s*\n|\s*$)',
            # Match "Insured Name: John Smith"
            r'Insured\s*Name[:\s]+([A-Z][a-zA-Z\s]+?)(?=\s*\n|\s*$)',
            # Match "Name: John Smith"
            r'Name[:\s]+([A-Z][a-zA-Z\s]+?)(?=\s*\n|\s*[0-9]|\s*[A-Z]{2,})',
            # Match "CLAIMANT: John Smith"
            r'CLAIMANT[:\s]+([A-Z][a-zA-Z\s]+?)(?=\s*\n|\s*$)',
        ],
        
        'effective_dates': [
            r'Effective\s*Date[:\s]+([0-9]{1,2}/[0-9]{1,2}/[0-9]{4})',
            r'Policy\s*Period[:\s]+([0-9]{1,2}/[0-9]{1,2}/[0-9]{4})',
            r'Coverage\s*Dates[:\s]+([0-9]{1,2}/[0-9]{1,2}/[0-9]{4})',
        ],
        
        # Incident Information - FIXED PATTERNS
        'date_of_loss': [
            # Match "Date of Loss: February 1, 2024" (with month name)
            r'Date\s*of\s*Loss[:\s]+([A-Z][a-z]+\s+\d{1,2},\s+\d{4})',
            # Match "DATE OF LOSS: 01/15/2024" (with slashes)
            r'DATE\s*OF\s*LOSS[:\s]+([0-9]{1,2}/[0-9]{1,2}/[0-9]{4})',
            # Match "Date: February 1, 2024"
            r'Date[:\s]+([A-Z][a-z]+\s+\d{1,2},\s+\d{4})',
            # Match "Loss Date: 01/15/2024"
            r'Loss\s*Date[:\s]+([0-9]{1,2}/[0-9]{1,2}/[0-9]{4})',
            # Match "Incident Date: 01/15/2024"
            r'Incident\s*Date[:\s]+([0-9]{1,2}/[0-9]{1,2}/[0-9]{4})',
        ],
        
        'time_of_loss': [
            r'Time[:\s]+(\d{1,2}:\d{2}\s*[AP]M)',
            r'Time\s*of\s*Loss[:\s]+(\d{1,2}:\d{2}\s*[AP]M)',
            r'(\d{1,2}:\d{2}\s*[AP]M)(?=\s*on|\s*date)',
        ],
        
        'location': [
            # Match "Location: 456 Oak Avenue, Springfield, IL 62704"
            r'Location[:\s]+(.*?)(?=\s*\n[A-Z]|\s*\n\d|\s*$)',
            # Match "LOCATION OF LOSS: 123 Main Street"
            r'LOCATION\s*OF\s*LOSS[:\s]+(.*?)(?=\s*\n[A-Z]|\s*\n\d|\s*$)',
            # Match "Address: 123 Main Street"
            r'Address[:\s]+(.*?)(?=\s*\n[A-Z]|\s*\n\d|\s*$)',
            # Match "STREET: 123 Main Street"
            r'STREET[:\s]+(.*?)(?=\s*\n[A-Z]|\s*\n\d|\s*$)',
        ],
        
        'description': [
            # Match multi-line descriptions more effectively
            r'Description[:\s]+(.*?)(?=\n[A-Z]{2,}|\n\d|\n\n|\Z)',
            r'DESCRIPTION[:\s]+(.*?)(?=\n[A-Z]{2,}|\n\d|\n\n|\Z)',
            r'Loss\s*Description[:\s]+(.*?)(?=\n[A-Z]{2,}|\n\d|\n\n|\Z)',
            r'Remarks[:\s]+(.*?)(?=\n[A-Z]{2,}|\n\d|\n\n|\Z)',
            # For ACORD forms
            r'DESCRIPTION\s*OF\s*(?:ACCIDENT|LOSS|INCIDENT)[:\s]+(.*?)(?=\n1\.|\n[A-Z]{2,}|\n\d|\Z)',
        ],
        
        # Asset Details
        'asset_type': [
            r'Vehicle\s*Type[:\s]+([A-Za-z\s]+)',
            r'Asset\s*Type[:\s]+([A-Za-z\s]+)',
            r'Type\s*of\s*Vehicle[:\s]+([A-Za-z\s]+)',
        ],
        
        'asset_id': [
            r'V\.I\.N\.\s*[:\s]+([A-Z0-9]{17})',
            r'VIN[:\s]+([A-Z0-9]{17})',
            r'Vehicle\s*ID[:\s]+([A-Z0-9]+)',
        ],
        
        'estimated_damage': [
            # Match "Damage Estimate: $8,200"
            r'Damage\s*Estimate[:\s]+\$?\s*([0-9,]+\.?[0-9]*)',
            # Match "ESTIMATE AMOUNT: $8,200"
            r'ESTIMATE\s*AMOUNT[:\s]+\$?\s*([0-9,]+\.?[0-9]*)',
            # Match "Estimated Damage: $8,200"
            r'Estimated\s*Damage[:\s]+\$?\s*([0-9,]+\.?[0-9]*)',
            # Match "Amount: $8,200"
            r'Amount[:\s]+\$?\s*([0-9,]+\.?[0-9]*)',
            # Match any dollar amount preceded by estimate keywords
            r'(?:Estimate|Damage|Amount)[:\s]+\$?\s*([0-9,]+\.?[0-9]*)',
        ],
        
        # Alias for estimate_amount to match config
        'estimate_amount': [
            r'ESTIMATE\s*AMOUNT[:\s]+\$?\s*([0-9,]+\.?[0-9]*)',
            r'Damage\s*Estimate[:\s]+\$?\s*([0-9,]+\.?[0-9]*)',
            r'Estimated\s*Damage[:\s]+\$?\s*([0-9,]+\.?[0-9]*)',
            r'\$([0-9,]+\.?[0-9]*)',
        ],
        
        # Involved Parties
        'claimant': [
            r'Claimant[:\s]+([A-Z][a-zA-Z\s]+?)(?=\s*\n|\s*$)',
            r'Driver\s*Name[:\s]+([A-Z][a-zA-Z\s]+?)(?=\s*\n|\s*$)',
            r'NAME\s*OF\s*CONTACT[:\s]+([A-Z][a-zA-Z\s]+?)(?=\s*\n|\s*$)',
        ],
        
        'contact_details': [
            r'Phone[:\s]+(?:\(?[A-Z]?\)?\s*)?([0-9\-\(\)\.\s]{10,})',
            r'PHONE[:\s]+(?:\(?[A-Z]?\)?\s*)?([0-9\-\(\)\.\s]{10,})',
            r'Contact[:\s]+(?:\(?[A-Z]?\)?\s*)?([0-9\-\(\)\.\s]{10,})',
            r'E-MAIL[:\s]+([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,})',
            r'Email[:\s]+([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,})',
        ],
        
        # Other Fields
        'attachments': [
            r'Attachments[:\s]+(.*?)(?=\s*\n|\s*$)',
            r'Documents\s*Attached[:\s]+(.*?)(?=\s*\n|\s*$)',
            r'Photos[:\s]+(.*?)(?=\s*\n|\s*$)',
        ],
        
        'initial_estimate': [
            r'Initial\s*Estimate[:\s]+\$?\s*([0-9,]+\.?[0-9]*)',
            r'Initial\s*Assessment[:\s]+\$?\s*([0-9,]+\.?[0-9]*)',
        ],
    }
    
    @classmethod
    def extract_all_fields(cls, document_text: str) -> Dict[str, Any]:
        """
        Extract all possible fields from document text
        
        Args:
            document_text: Full text of the document
            
        Returns:
            Dictionary of extracted fields
        """
        results = {}
        
        # Normalize line endings and spaces
        text = cls._normalize_text(document_text)
        
        # Extract using regex patterns
        for field, patterns in cls.PATTERNS.items():
            value = cls._extract_with_patterns(text, patterns, field)
            if value:
                results[field] = value
        
        # Post-process and clean values
        results = cls._post_process_fields(results, text)
        
        return results
    
    @staticmethod
    def _normalize_text(text: str) -> str:
        """
        Normalize text for better pattern matching
        
        Args:
            text: Raw document text
            
        Returns:
            Normalized text
        """
        if not text:
            return ""
        
        # Replace multiple spaces with single space
        text = re.sub(r' {2,}', ' ', text)
        
        # Ensure consistent line endings
        text = re.sub(r'\r\n', '\n', text)
        
        # Remove excessive empty lines
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        return text.strip()
    
    @classmethod
    def _extract_with_patterns(cls, text: str, patterns: List[str], field_name: str) -> Any:
        """
        Try multiple patterns for a field
        
        Args:
            text: Document text
            patterns: List of regex patterns
            field_name: Name of field being extracted
            
        Returns:
            Extracted value or None
        """
        for pattern in patterns:
            try:
                match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
                if match:
                    # Get the first non-empty group
                    for group in match.groups():
                        if group and str(group).strip():
                            value = str(group).strip()
                            return cls._clean_field_value(value, field_name)
            except Exception as e:
                continue
        
        return None
    
    @classmethod
    def _clean_field_value(cls, value: str, field_name: str) -> Any:
        """
        Clean and convert field value based on field type
        
        Args:
            value: Raw extracted value
            field_name: Name of the field
            
        Returns:
            Cleaned/converted value
        """
        if not value:
            return None
        
        # Remove extra whitespace
        value = re.sub(r'\s+', ' ', value.strip())
        
        # Field-specific cleaning
        if field_name in ['estimated_damage', 'initial_estimate', 'estimate_amount']:
            return cls._parse_amount(value)
        elif field_name in ['date_of_loss']:
            return cls._parse_date(value)
        elif field_name in ['policy_number', 'asset_id']:
            return value.upper()
        elif field_name in ['description']:
            return cls._clean_description(value)
        elif field_name in ['policyholder_name', 'claimant']:
            # Clean up names - remove extra titles or suffixes
            value = re.sub(r'\s+[A-Z]\.?$', '', value)  # Remove single initials at end
            value = re.sub(r'\s+(?:JR|SR|II|III|IV|V)$', '', value, flags=re.IGNORECASE)
        
        return value
    
    @staticmethod
    def _parse_amount(amount_str: str) -> float:
        """
        Parse amount string to float
        
        Args:
            amount_str: String like "$12,500.00" or "12500"
            
        Returns:
            Float value
        """
        try:
            # Remove all non-numeric except decimal point
            clean_str = re.sub(r'[^\d.]', '', amount_str)
            if clean_str:
                return float(clean_str)
        except:
            pass
        return 0.0
    
    @staticmethod
    def _parse_date(date_str: str) -> str:
        """
        Parse date string to standard format
        
        Args:
            date_str: Date string in various formats
            
        Returns:
            Date in YYYY-MM-DD format or original if can't parse
        """
        try:
            # Try month name format first (for "February 5, 2024")
            month_formats = [
                '%B %d, %Y',      # February 5, 2024
                '%b %d, %Y',      # Feb 5, 2024
                '%B %d, %Y %I:%M %p',  # February 5, 2024 10:15 AM
                '%m/%d/%Y', '%m/%d/%y',
                '%d/%m/%Y', '%d/%m/%y',
                '%Y-%m-%d', '%d-%m-%Y'
            ]
            
            for fmt in month_formats:
                try:
                    dt = datetime.strptime(date_str, fmt)
                    return dt.strftime('%Y-%m-%d')
                except:
                    continue
        except:
            pass
        
        return date_str  # Return original if can't parse
    
    @staticmethod
    def _clean_description(desc: str) -> str:
        """
        Clean description text
        
        Args:
            desc: Raw description
            
        Returns:
            Cleaned description
        """
        if not desc:
            return ""
        
        # Remove excessive whitespace
        desc = re.sub(r'\s+', ' ', desc.strip())
        
        # Remove common prefixes/suffixes
        desc = re.sub(r'^[:\.\-\s]+', '', desc)
        desc = re.sub(r'[:\.\-\s]+$', '', desc)
        
        # Fix common OCR errors
        ocr_corrections = {
            'Iight': 'light',
            'poIe': 'pole',
            'Iot': 'lot',
            'corners': 'corners',
        }
        
        for wrong, correct in ocr_corrections.items():
            desc = desc.replace(wrong, correct)
        
        # Limit length but keep meaningful
        if len(desc) > 2000:
            # Try to cut at sentence boundary
            sentences = re.split(r'[.!?]+', desc)
            trimmed = ""
            for sentence in sentences:
                if len(trimmed + sentence) < 1500:
                    trimmed += sentence + "."
                else:
                    break
            desc = trimmed if trimmed else desc[:1500] + "..."
        
        return desc
    
    @classmethod
    def _post_process_fields(cls, extracted: Dict[str, Any], full_text: str) -> Dict[str, Any]:
        """
        Post-process extracted fields and infer missing ones
        
        Args:
            extracted: Dictionary of extracted fields
            full_text: Full document text
            
        Returns:
            Enhanced fields dictionary
        """
        # Sync estimated_damage and estimate_amount fields
        if 'estimated_damage' in extracted and 'estimate_amount' not in extracted:
            extracted['estimate_amount'] = extracted['estimated_damage']
        elif 'estimate_amount' in extracted and 'estimated_damage' not in extracted:
            extracted['estimated_damage'] = extracted['estimate_amount']
        
        # Infer claim type from description
        if 'claim_type' not in extracted:
            extracted['claim_type'] = cls._infer_claim_type(extracted.get('description', ''))
        
        # If no explicit estimate amount, check for amount in text
        if 'estimated_damage' not in extracted or not extracted['estimated_damage']:
            # Look for any dollar amount in the text
            amount_match = re.search(r'\$([0-9,]+\.?[0-9]*)', full_text)
            if amount_match:
                amount = cls._parse_amount(amount_match.group(1))
                extracted['estimated_damage'] = amount
                extracted['estimate_amount'] = amount
        
        # Extract vehicle info from ACORD tables
        extracted.update(cls._extract_vehicle_info(full_text))
        
        # Extract contact info patterns
        extracted.update(cls._extract_contact_info(full_text))
        
        # Clean up any extracted values
        for key, value in list(extracted.items()):
            if isinstance(value, str):
                extracted[key] = value.strip()
        
        return extracted
    
    @classmethod
    def _infer_claim_type(cls, description: str) -> str:
        """
        Infer claim type from description text
        
        Args:
            description: Claim description
            
        Returns:
            Claim type string
        """
        if not description:
            return "property_damage"
        
        desc_lower = description.lower()
        
        # Check for injury
        injury_keywords = ['injury', 'injured', 'hurt', 'pain', 'hospital', 
                          'ambulance', 'medical', 'whiplash', 'fracture', 
                          'broken bone', 'concussion', 'emergency room', 'er']
        
        if any(keyword in desc_lower for keyword in injury_keywords):
            return "injury"
        
        # Check for theft
        theft_keywords = ['stolen', 'theft', 'robbery', 'burglary', 'break-in', 
                         'missing vehicle', 'car stolen', 'auto theft']
        
        if any(keyword in desc_lower for keyword in theft_keywords):
            return "theft"
        
        # Check for fire
        fire_keywords = ['fire', 'burned', 'arson', 'smoke', 'flame', 'ignite']
        
        if any(keyword in desc_lower for keyword in fire_keywords):
            return "fire"
        
        # Check for flood/water
        water_keywords = ['flood', 'water', 'leak', 'pipe burst', 'rain', 
                         'storm', 'hurricane', 'flooding']
        
        if any(keyword in desc_lower for keyword in water_keywords):
            return "water_damage"
        
        # Check for vandalism
        vandalism_keywords = ['vandal', 'graffiti', 'broken window', 'keyed', 
                             'scratched', 'malicious', 'intentional']
        
        if any(keyword in desc_lower for keyword in vandalism_keywords):
            return "vandalism"
        
        # Default based on vehicle mention
        vehicle_keywords = ['vehicle', 'car', 'truck', 'auto', 'accident', 
                           'collision', 'crash', 'wreck', 'rear-end', 'bumper']
        
        if any(keyword in desc_lower for keyword in vehicle_keywords):
            return "vehicle_damage"
        
        return "property_damage"
    
    @classmethod
    def _extract_vehicle_info(cls, text: str) -> Dict[str, str]:
        """
        Extract vehicle information from ACORD form
        
        Args:
            text: Document text
            
        Returns:
            Dictionary with vehicle info
        """
        vehicle_info = {}
        
        # Try to find vehicle section
        vehicle_section_patterns = [
            r'VEH\s*#.*?DESCRIBE DAMAGE',
            r'VEHICLE INFORMATION.*?DESCRIBE DAMAGE',
            r'YEAR.*?MAKE.*?MODEL.*?VIN',
        ]
        
        for pattern in vehicle_section_patterns:
            vehicle_match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if vehicle_match:
                vehicle_text = vehicle_match.group(0)
                
                # Extract year
                year_match = re.search(r'YEAR\s*[:\s]*([0-9]{4})', vehicle_text, re.IGNORECASE)
                if year_match:
                    vehicle_info['year'] = year_match.group(1).strip()
                
                # Extract make
                make_match = re.search(r'MAKE\s*[:\s]*([A-Za-z\s]+)', vehicle_text, re.IGNORECASE)
                if make_match:
                    vehicle_info['make'] = make_match.group(1).strip()
                
                # Extract model
                model_match = re.search(r'MODEL\s*[:\s]*([A-Za-z0-9\s\-]+)', vehicle_text, re.IGNORECASE)
                if model_match:
                    vehicle_info['model'] = model_match.group(1).strip()
                
                # Extract VIN
                vin_match = re.search(r'V\.?I\.?N\.?\s*[:\s]*([A-Z0-9]{17})', vehicle_text, re.IGNORECASE)
                if vin_match:
                    vehicle_info['vin'] = vin_match.group(1).upper()
                
                # Extract plate
                plate_match = re.search(r'PLATE\s*(?:NUMBER|NO|#)\s*[:\s]*([A-Z0-9\-\s]+)', vehicle_text, re.IGNORECASE)
                if plate_match:
                    vehicle_info['plate_number'] = plate_match.group(1).strip().upper()
                
                break  # Stop after first match
        
        return vehicle_info
    
    @classmethod
    def _extract_contact_info(cls, text: str) -> Dict[str, str]:
        """
        Extract contact information
        
        Args:
            text: Document text
            
        Returns:
            Dictionary with contact info
        """
        contact_info = {}
        
        # Phone patterns - improved
        phone_patterns = [
            r'Phone[:\s]+(?:\(?\d{3}\)?[-.\s]?)?(\d{3}[-.\s]?\d{4})',
            r'PHONE[:\s]+(?:\(?\d{3}\)?[-.\s]?)?(\d{3}[-.\s]?\d{4})',
            r'Contact[:\s]+(?:\(?\d{3}\)?[-.\s]?)?(\d{3}[-.\s]?\d{4})',
            r'Telephone[:\s]+(?:\(?\d{3}\)?[-.\s]?)?(\d{3}[-.\s]?\d{4})',
            r'Tel[:\s]+(?:\(?\d{3}\)?[-.\s]?)?(\d{3}[-.\s]?\d{4})',
            r'(\d{3}[-.\s]?\d{3}[-.\s]?\d{4})(?=\s|$|\n)',  # Generic phone pattern
        ]
        
        for pattern in phone_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                phone = re.sub(r'[^\d]', '', match.group(1))
                if len(phone) >= 10:
                    contact_info['contact_phone'] = phone
                    break
        
        # Email patterns
        email_patterns = [
            r'Email[:\s]+([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})',
            r'E-MAIL[:\s]+([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})',
            r'Contact[:\s]+([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})',
            r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})',
        ]
        
        for pattern in email_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                contact_info['contact_email'] = match.group(1).lower()
                break
        
        return contact_info
    
    @classmethod
    def identify_missing_fields(cls, extracted_fields: Dict[str, Any]) -> List[str]:
        """
        Identify which required fields are missing
        
        Args:
            extracted_fields: Dictionary of extracted fields
            
        Returns:
            List of missing required field names
        """
        missing = []
        
        for field in config.REQUIRED_FIELDS:
            if field not in extracted_fields or not extracted_fields.get(field):
                missing.append(field)
        
        return missing