# fnol-agent/create_samples.py
"""
Create sample FNOL documents for testing - Creates files in current directory
"""

import os
import json

def create_sample_files():
    """Create sample FNOL documents in current directory"""
    
    print("Creating sample FNOL documents in current directory...")
    
    # Sample 1: Fast-track claim (minor damage)
    fast_track = """FNOL REPORT - AUTOMOBILE CLAIM
Claim Reference: CL-2024-001
Date Submitted: 2024-02-05

POLICY INFORMATION:
Policy Number: AUTO-78901234
Policyholder Name: Sarah Johnson
Effective Dates: 01/01/2024 to 01/01/2025

INCIDENT DETAILS:
Date of Loss: February 1, 2024
Time: 14:45 PM
Location: 456 Oak Avenue, Springfield, IL 62704
Description: Vehicle was side-swiped in parking lot while parked.
Minor damage to driver's side door and mirror. No other vehicles involved.

ASSET INFORMATION:
Asset Type: Automobile
Vehicle: 2020 Honda Civic
VIN: 2HGFC2F56LH123456
Plate: IL-ABC123

DAMAGE ASSESSMENT:
Estimated Damage: $8,200
Initial Estimate: $8,200
Attachments: Photos of damage

INVOLVED PARTIES:
Claimant: Sarah Johnson
Contact: (555) 123-4567, sarah.j@email.com

OTHER INFORMATION:
Claim Type: Vehicle Damage
Special Instructions: None
"""
    
    # Sample 2: Injury claim
    injury_claim = """ACORD AUTOMOBILE LOSS NOTICE
Form Version: 2016/10

AGENCY INFORMATION:
Agency: Metro Insurance Services

POLICY INFORMATION:
Policy Number: HEALTH-456-789
Named Insured: Michael Chen
Policy Period: 12/15/2023 - 12/15/2024

LOSS INFORMATION:
Date of Loss: January 30, 2024
Time: 09:15 AM
Location: 789 Broadway at 5th Avenue, Metro City
Police Report: MCPD-2024-5678
Description: Multi-vehicle collision at intersection. Insured's vehicle
was struck from behind, pushing it into vehicle in front. Airbags deployed.
Driver complained of neck and back pain. Paramedics transported to
Metro General Hospital for evaluation. X-rays showed minor whiplash.

VEHICLE INFORMATION:
Year: 2019
Make: Toyota
Model: RAV4
VIN: JTMBFREVXKD123456
Plate: MC-XYZ789

DAMAGE INFORMATION:
Estimate Amount: $42,000
Describe Damage: Severe front and rear damage, airbags deployed,
frame damage suspected.

INJURY INFORMATION:
Injured Party: Michael Chen
Extent of Injury: Neck strain, back pain, whiplash
Treatment: Hospital evaluation, prescribed pain medication

CONTACT INFORMATION:
Phone: (555) 987-6543
Email: mchen@email.com
"""
    
    # Sample 3: Fraud suspect claim
    fraud_suspect = """FIRST NOTICE OF LOSS - PROPERTY CLAIM
File Number: PROP-2024-033

INSURED INFORMATION:
Insured: Robert Wilson
Policy: PROP-123-XYZ
Address: 321 Pine Road, Suburbia

INCIDENT DETAILS:
Date of Loss: February 2, 2024
Time: Approximately 23:30
Location: Deserted industrial area on West 45th Street
Description: Vehicle theft reported. Insured states vehicle was
parked while visiting a "friend" but cannot provide friend's name or
address. Keys allegedly left in ignition. Several inconsistencies in
timeline. Previous claim filed last month for "vandalism" on same
vehicle. Possibly staged incident for insurance fraud.

VEHICLE DETAILS:
Vehicle: 2018 BMW 5 Series
VIN: WBA5E5C58JD789012
Value: $45,000

DAMAGE/LOSS:
Estimated Loss: $45,000 (total theft)
Initial Assessment: Suspicious circumstances noted

CONTACT:
Phone: (555) 555-1212
Best time to contact: Evenings

SPECIAL NOTES:
Investigation recommended. Multiple red flags:
1. Inconsistent statements
2. High-value vehicle
3. Previous recent claim
4. Location suspicious
"""
    
    # Sample 4: High damage claim
    high_damage = """COMMERCIAL AUTO CLAIM
Claim ID: COM-2024-789

BUSINESS INFORMATION:
Business Name: Quick Delivery Services
Policy: COMM-555-888

ACCIDENT DETAILS:
Date: January 25, 2024
Time: 08:30 AM
Location: Highway 101, Mile Marker 45
Description: Commercial delivery truck lost control on wet road,
collided with guardrail and overturned. Significant damage to truck
and cargo. Road closure for 3 hours for cleanup.

EQUIPMENT:
Vehicle: 2022 Ford F-650 Box Truck
VIN: 1FDXF46P2NEB45678
Gross Weight: 26,000 lbs

DAMAGE ASSESSMENT:
Vehicle Damage: $85,000
Cargo Damage: $15,000
Total Estimate: $100,000
Attachments: Police report, photos, driver statement

INJURIES:
Driver: Minor bruises, released at scene

CONTACT:
Claims Manager: Lisa Rodriguez
Phone: (555) 222-3333
Email: lisa@quickdelivery.com
"""
    
    # Sample 5: Minimal information (should go to manual review)
    minimal_info = """NOTICE OF LOSS

Policy: ABC123
Name: John Doe
Date: Last week
Car got hit.
Estimate: Unknown

Need to process quickly.
"""
    
    # Write sample files directly in current directory
    samples = {
        "fast_track_claim.txt": fast_track,
        "injury_claim.txt": injury_claim,
        "fraud_suspect.txt": fraud_suspect,
        "high_damage_claim.txt": high_damage,
        "minimal_info.txt": minimal_info,
    }
    
    for filename, content in samples.items():
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Created: {filename}")
    
    # Create a sample JSON output for reference
    sample_output = {
        "document": "fast_track_claim.txt",
        "timestamp": "2024-02-05T14:30:00",
        "status": "success",
        "extractedFields": {
            "policy_number": "AUTO-78901234",
            "policyholder_name": "Sarah Johnson",
            "date_of_loss": "2024-02-01",
            "location": "456 Oak Avenue, Springfield, IL 62704",
            "description": "Vehicle was side-swiped in parking lot while parked. Minor damage to driver's side door and mirror. No other vehicles involved.",
            "estimated_damage": 8200.0,
            "claim_type": "vehicle_damage",
            "asset_id": "2HGFC2F56LH123456",
            "contact_phone": "5551234567"
        },
        "missingFields": [],
        "validation": {
            "warnings": [],
            "errors": [],
            "inconsistencies": []
        },
        "recommendedRoute": "Fast-track",
        "reasoning": "Estimated damage ($8,200.00) is below $25,000 threshold",
        "processingTime": 0.85
    }
    
    output_path = "sample_output.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(sample_output, f, indent=2)
    
    print(f"\nCreated sample output: {output_path}")
    print("\nAll sample files created successfully in current directory!")

if __name__ == "__main__":
    create_sample_files()