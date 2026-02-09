# fnol-agent/src/config.py
"""
Configuration settings for the FNOL Agent
"""

import os
from dataclasses import dataclass

@dataclass
class Config:
    """Configuration parameters"""
    
    # Routing thresholds
    FAST_TRACK_THRESHOLD: float = 25000.0
    
    # Fraud detection keywords
    FRAUD_KEYWORDS = [
        'fraud', 'fraudulent', 'false', 'fake', 'staged', 'setup',
        'inconsistent', 'contradict', 'lie', 'lied', 'lying', 
        'misrepresent', 'exaggerat', 'inflated', 'suspicious',
        'fabricated', 'concocted', 'scam', 'scheme'
    ]
    
    # Injury keywords
    INJURY_KEYWORDS = [
        'injury', 'injured', 'hurt', 'pain', 'hospital',
        'ambulance', 'medical', 'doctor', 'fracture', 'broken',
        'whiplash', 'concussion', 'bleeding', 'wound', 'laceration',
        'surgery', 'therapy', 'treatment', 'paramedic', 'emergency'
    ]
    
    # Required fields - MAKE SURE THESE MATCH FIELD EXTRACTOR NAMES
    REQUIRED_FIELDS = [
        'policy_number',
        'policyholder_name',
        'date_of_loss',
        'location',
        'description',
        'estimated_damage',  
        'claim_type'
    ]
    
    # Optional fields (nice to have)
    OPTIONAL_FIELDS = [
        'time_of_loss',
        'vin',
        'make_model',
        'year',
        'plate_number',
        'driver_name',
        'contact_phone',
        'contact_email',
        'attachments',
        'third_parties',
        'witnesses'
    ]

config = Config()