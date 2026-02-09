# fnol-agent/src/routing_engine.py
"""
Routing decision engine for FNOL claims
"""

from typing import Dict, List, Tuple
from .config import config

class RoutingEngine:
    """Applies routing rules to determine claim handling path"""
    
    @classmethod
    def determine_route(cls, extracted_fields: Dict, missing_fields: List[str]) -> Tuple[str, str]:
        """
        Determine routing based on extracted fields and rules
        
        Args:
            extracted_fields: Dictionary of extracted fields
            missing_fields: List of missing required fields
            
        Returns:
            Tuple of (route, reasoning)
        """
        reasoning_parts = []
        
        # Rule 1: Check for missing mandatory fields
        if missing_fields:
            route = "Manual Review"
            missing_str = ", ".join(missing_fields)
            reasoning_parts.append(f"Missing required fields: {missing_str}")
            return route, ". ".join(reasoning_parts)
        
        # Get values with defaults
        description = extracted_fields.get('description', '').lower()
        damage = extracted_fields.get('estimated_damage', 0)
        claim_type = extracted_fields.get('claim_type', 'property_damage')
        
        # Rule 2: Check for fraud indicators
        fraud_detected = False
        fraud_keywords_found = []
        
        for keyword in config.FRAUD_KEYWORDS:
            if keyword in description:
                fraud_detected = True
                fraud_keywords_found.append(keyword)
        
        if fraud_detected:
            route = "Investigation Flag"
            keywords_str = ", ".join(fraud_keywords_found[:3])  # Show first 3
            reasoning_parts.append(f"Fraud indicators detected: {keywords_str}")
            return route, ". ".join(reasoning_parts)
        
        # Rule 3: Check for injury claims
        if claim_type == "injury":
            route = "Specialist Queue"
            
            # Check for specific injury keywords
            injury_keywords = []
            for keyword in config.INJURY_KEYWORDS:
                if keyword in description:
                    injury_keywords.append(keyword)
            
            if injury_keywords:
                injury_str = ", ".join(injury_keywords[:3])
                reasoning_parts.append(f"Injury claim with indicators: {injury_str}")
            else:
                reasoning_parts.append("Injury claim type identified")
            
            return route, ". ".join(reasoning_parts)
        
        # Rule 4: Check damage amount for fast-track
        if damage > 0:
            if damage < config.FAST_TRACK_THRESHOLD:
                route = "Fast-track"
                reasoning_parts.append(
                    f"Estimated damage (${damage:,.2f}) is below ${config.FAST_TRACK_THRESHOLD:,.0f} threshold"
                )
            else:
                route = "Standard Processing"
                reasoning_parts.append(
                    f"Estimated damage (${damage:,.2f}) meets or exceeds ${config.FAST_TRACK_THRESHOLD:,.0f} threshold"
                )
        else:
            # No damage amount specified
            route = "Manual Review"
            reasoning_parts.append("Damage amount not specified or could not be extracted")
        
        # Additional considerations
        additional_reasons = cls._check_additional_factors(extracted_fields)
        if additional_reasons:
            reasoning_parts.extend(additional_reasons)
        
        return route, ". ".join(reasoning_parts)
    
    @classmethod
    def _check_additional_factors(cls, extracted_fields: Dict) -> List[str]:
        """
        Check additional factors that might affect routing
        
        Args:
            extracted_fields: Dictionary of extracted fields
            
        Returns:
            List of additional reasoning strings
        """
        reasons = []
        
        # Check for multiple vehicles
        description = extracted_fields.get('description', '').lower()
        if description.count('vehicle') > 1 or description.count('car') > 1:
            reasons.append("Multiple vehicles involved")
        
        # Check for hit-and-run
        if 'hit and run' in description or 'hit & run' in description:
            reasons.append("Hit-and-run incident")
        
        # Check for commercial vehicle
        if any(word in description for word in ['commercial', 'truck', 'semi', 'fleet', 'business']):
            reasons.append("Commercial vehicle involved")
        
        # Check for previous claims mention
        if any(word in description for word in ['previous', 'prior', 'last claim', 'before']):
            reasons.append("Reference to previous claims")
        
        return reasons
    
    @classmethod
    def validate_extracted_data(cls, extracted_fields: Dict) -> Dict[str, List[str]]:
        """
        Validate extracted data for inconsistencies
        
        Args:
            extracted_fields: Dictionary of extracted fields
            
        Returns:
            Dictionary with validation results
        """
        validation_results = {
            'warnings': [],
            'errors': [],
            'inconsistencies': []
        }
        
        # Check for unrealistic damage amounts
        damage = extracted_fields.get('estimated_damage', 0)
        if damage > 1000000:  # $1M threshold
            validation_results['warnings'].append(
                f"Unusually high damage amount: ${damage:,.2f}"
            )
        
        # Check for future dates
        date_str = extracted_fields.get('date_of_loss', '')
        if date_str:
            from datetime import datetime
            try:
                loss_date = datetime.strptime(date_str, '%Y-%m-%d')
                today = datetime.now()
                if loss_date > today:
                    validation_results['errors'].append(
                        f"Date of loss is in the future: {date_str}"
                    )
            except:
                pass
        
        # Check description length
        description = extracted_fields.get('description', '')
        if len(description) < 10:
            validation_results['warnings'].append(
                "Description is very short, may be incomplete"
            )
        
        # Check for inconsistencies between claim type and description
        claim_type = extracted_fields.get('claim_type', '')
        if claim_type == 'injury' and 'injury' not in description.lower():
            validation_results['inconsistencies'].append(
                "Claim type is 'injury' but description doesn't mention injuries"
            )
        
        return validation_results