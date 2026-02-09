# fnol-agent/tests/test_fnol_agent.py
"""
Unit tests for FNOL Agent
"""

import unittest
import sys
import os
import json
import tempfile

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.document_loader import DocumentLoader
from src.field_extractor import FieldExtractor
from src.routing_engine import RoutingEngine
from src.main import FNOLAgent

class TestDocumentLoader(unittest.TestCase):
    
    def setUp(self):
        self.loader = DocumentLoader()
    
    def test_text_cleaning(self):
        """Test text cleaning function"""
        dirty_text = "  Hello   World\n\nThis  is  a  test.  "
        clean_text = self.loader._clean_text(dirty_text)
        self.assertEqual(clean_text, "Hello World This is a test.")
    
    def test_txt_loading(self):
        """Test loading TXT file"""
        # Create temporary test file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("Test content\nLine 2\nLine 3")
            temp_path = f.name
        
        try:
            result = self.loader.load_document(temp_path)
            self.assertEqual(result['format'], 'txt')
            self.assertIn('Test content', result['text'])
        finally:
            os.unlink(temp_path)

class TestFieldExtractor(unittest.TestCase):
    
    def setUp(self):
        self.extractor = FieldExtractor()
        self.sample_text = """
        ACORD FORM
        POLICY NUMBER: AUTO-78901234
        NAME OF INSURED: John Alexander Smith
        DATE OF LOSS: 01/15/2024
        TIME: 10:30 AM
        LOCATION OF LOSS: 123 Main Street, Anytown, CA 90210
        ESTIMATE AMOUNT: $12,500.00
        DESCRIPTION OF ACCIDENT: Vehicle was rear-ended at a stop light.
        Minor bumper damage observed. No injuries reported.
        Driver complained of minor neck stiffness but refused medical attention.
        V.I.N.: 1HGBH41JXMN109186
        YEAR: 2020
        MAKE: Toyota
        MODEL: Camry
        """
    
    def test_policy_number_extraction(self):
        """Test policy number extraction"""
        result = self.extractor.extract_all_fields(self.sample_text)
        self.assertEqual(result.get('policy_number'), 'AUTO-78901234')
    
    def test_name_extraction(self):
        """Test policyholder name extraction"""
        result = self.extractor.extract_all_fields(self.sample_text)
        self.assertEqual(result.get('policyholder_name'), 'John Alexander Smith')
    
    def test_date_extraction(self):
        """Test date extraction"""
        result = self.extractor.extract_all_fields(self.sample_text)
        self.assertEqual(result.get('date_of_loss'), '2024-01-15')
    
    def test_amount_extraction(self):
        """Test damage amount extraction"""
        result = self.extractor.extract_all_fields(self.sample_text)
        self.assertEqual(result.get('estimated_damage'), 12500.0)
    
    def test_vin_extraction(self):
        """Test VIN extraction"""
        result = self.extractor.extract_all_fields(self.sample_text)
        self.assertEqual(result.get('asset_id'), '1HGBH41JXMN109186')
    
    def test_missing_fields_detection(self):
        """Test missing fields identification"""
        extracted = {
            'policy_number': 'TEST123',
            'policyholder_name': 'John Doe',
            'date_of_loss': '2024-01-01',
            # Missing: location, description, estimate_amount, claim_type
        }
        missing = self.extractor.identify_missing_fields(extracted)
        self.assertIn('location', missing)
        self.assertIn('description', missing)
        self.assertIn('estimate_amount', missing)
        self.assertIn('claim_type', missing)

class TestRoutingEngine(unittest.TestCase):
    
    def setUp(self):
        self.router = RoutingEngine()
    
    def test_fast_track_routing(self):
        """Test fast-track routing for low damage claims"""
        extracted = {
            'policy_number': 'TEST123',
            'policyholder_name': 'John Doe',
            'date_of_loss': '2024-01-01',
            'location': 'Test Location',
            'description': 'Minor scratch on bumper',
            'estimate_amount': 8000.0,
            'claim_type': 'vehicle_damage'
        }
        missing = []
        
        route, reasoning = self.router.determine_route(extracted, missing)
        self.assertEqual(route, 'Fast-track')
        self.assertIn('below', reasoning)
    
    def test_injury_routing(self):
        """Test specialist routing for injury claims"""
        extracted = {
            'policy_number': 'TEST123',
            'policyholder_name': 'John Doe',
            'date_of_loss': '2024-01-01',
            'location': 'Test Location',
            'description': 'Accident with neck injury, taken to hospital',
            'estimate_amount': 15000.0,
            'claim_type': 'injury'
        }
        missing = []
        
        route, reasoning = self.router.determine_route(extracted, missing)
        self.assertEqual(route, 'Specialist Queue')
        self.assertIn('injury', reasoning.lower())
    
    def test_fraud_detection(self):
        """Test fraud detection routing"""
        extracted = {
            'policy_number': 'TEST123',
            'policyholder_name': 'John Doe',
            'date_of_loss': '2024-01-01',
            'location': 'Test Location',
            'description': 'Suspicious claim, possibly staged accident for fraud',
            'estimate_amount': 18000.0,
            'claim_type': 'vehicle_damage'
        }
        missing = []
        
        route, reasoning = self.router.determine_route(extracted, missing)
        self.assertEqual(route, 'Investigation Flag')
        self.assertIn('fraud', reasoning.lower())
    
    def test_missing_fields_routing(self):
        """Test routing when fields are missing"""
        extracted = {
            'policy_number': 'TEST123',
            'policyholder_name': 'John Doe',
            # Missing required fields
        }
        missing = ['date_of_loss', 'location', 'description', 'estimate_amount', 'claim_type']
        
        route, reasoning = self.router.determine_route(extracted, missing)
        self.assertEqual(route, 'Manual Review')
        self.assertIn('missing', reasoning.lower())

class TestFNOLAgentIntegration(unittest.TestCase):
    
    def test_agent_initialization(self):
        """Test agent initialization"""
        agent = FNOLAgent(verbose=False)
        self.assertIsNotNone(agent.loader)
        self.assertIsNotNone(agent.extractor)
        self.assertIsNotNone(agent.router)
    
    def test_end_to_end_processing(self):
        """Test end-to-end processing with sample text file"""
        # Create temporary test file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("""
            FNOL REPORT
            POLICY NUMBER: TEST-2024-001
            NAME OF INSURED: Jane Smith
            DATE OF LOSS: 02/01/2024
            LOCATION: 456 Oak Ave, Springfield
            ESTIMATE AMOUNT: $8,200
            DESCRIPTION: Side mirror damaged in parking lot.
            """)
            temp_path = f.name
        
        try:
            agent = FNOLAgent(verbose=False)
            result = agent.process_document(temp_path)
            
            self.assertEqual(result['status'], 'success')
            self.assertIn('extractedFields', result)
            self.assertIn('recommendedRoute', result)
            self.assertIn('reasoning', result)
            
            # Should be fast-track due to low damage
            self.assertEqual(result['recommendedRoute'], 'Fast-track')
            
        finally:
            os.unlink(temp_path)

if __name__ == '__main__':
    # Run tests
    unittest.main(verbosity=2)