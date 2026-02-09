# fnol-agent/run_demo.py - UPDATED
"""
Demo script to showcase FNOL Agent functionality
"""

import os
import sys
import json
from datetime import datetime

# FIX: Add the project root to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Now import
try:
    from src.main import FNOLAgent
    print("✓ FNOLAgent imported successfully")
except ImportError as e:
    print(f"Import error: {e}")
    sys.exit(1)


def run_demo():
    """Run a comprehensive demo of the FNOL Agent"""
    
    print("\n" + "="*60)
    print("FNOL PROCESSING AGENT - DEMONSTRATION")
    print("="*60 + "\n")
    
    # Initialize agent with verbose output
    agent = FNOLAgent(verbose=True)
    
    # Check if samples exist, create them if not
    samples_dir = "samples"
    if not os.path.exists(samples_dir):
        print("Creating sample files...")
        try:
            from samples.create_samples import create_sample_files
            create_sample_files()
        except ImportError as e:
            print(f"Error creating samples: {e}")
            return
    
    # Get sample files
    sample_files = [
        os.path.join(samples_dir, "fast_track_claim.txt"),
        os.path.join(samples_dir, "injury_claim.txt"),
        os.path.join(samples_dir, "fraud_suspect.txt"),
        os.path.join(samples_dir, "high_damage_claim.txt"),
        os.path.join(samples_dir, "minimal_info.txt"),
    ]
    
    # Ensure files exist
    sample_files = [f for f in sample_files if os.path.exists(f)]
    
    if not sample_files:
        print("No sample files found!")
        return
    
    print(f"Found {len(sample_files)} sample files for processing.\n")
    
    # Process each sample
    all_results = []
    
    for file_path in sample_files:
        print("-"*60)
        print(f"Processing: {os.path.basename(file_path)}")
        print("-"*60)
        
        result = agent.process_document(file_path)
        all_results.append(result)
        
        # Display key results
        print(f"Status: {result['status']}")
        print(f"Extracted Fields: {len(result['extractedFields'])}")
        print(f"Missing Required Fields: {len(result['missingFields'])}")
        if result['missingFields']:
            print(f"  - {', '.join(result['missingFields'])}")
        
        print(f"Recommended Route: {result['recommendedRoute']}")
        print(f"Reasoning: {result['reasoning']}")
        
        # Show some extracted fields
        extracted = result['extractedFields']
        if extracted:
            print("\nKey Extracted Fields:")
            for key in ['policy_number', 'policyholder_name', 'date_of_loss', 
                       'estimated_damage', 'claim_type']:
                if key in extracted and extracted[key]:
                    value = extracted[key]
                    if key == 'estimated_damage':
                        value = f"${value:,.2f}"
                    print(f"  {key.replace('_', ' ').title()}: {value}")
        
        print(f"Processing Time: {result['processingTime']:.2f} seconds\n")
    
    # Display statistics
    print("="*60)
    print("DEMO SUMMARY")
    print("="*60)
    
    stats = agent.get_statistics()
    print(f"\nProcessing Statistics:")
    print(f"  Total Documents Processed: {stats['processed']}")
    print(f"  Processing Errors: {stats['errors']}")
    print(f"  Average Processing Time: {stats['avg_processing_time']:.2f} seconds")
    
    print(f"\nRouting Distribution:")
    for route, count in stats['routes'].items():
        percentage = (count / stats['processed']) * 100
        print(f"  {route}: {count} ({percentage:.1f}%)")
    
    # Save combined results
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = os.path.join(output_dir, f"demo_results_{timestamp}.json")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False)
    
    print(f"\nDetailed results saved to: {output_file}")
    
    # Create a summary report
    summary_file = os.path.join(output_dir, f"demo_summary_{timestamp}.txt")
    with open(summary_file, 'w', encoding='utf-8') as f:
        f.write("FNOL Agent Demo Summary\n")
        f.write("="*50 + "\n\n")
        f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Total Documents: {stats['processed']}\n")
        f.write(f"Errors: {stats['errors']}\n\n")
        
        f.write("Document Results:\n")
        f.write("-"*50 + "\n")
        
        for result in all_results:
            f.write(f"\nDocument: {result['document']}\n")
            f.write(f"  Route: {result['recommendedRoute']}\n")
            f.write(f"  Reasoning: {result['reasoning'][:100]}...\n")
            f.write(f"  Processing Time: {result['processingTime']:.2f}s\n")
    
    print(f"Summary report saved to: {summary_file}")
    
    # Test the ACORD PDF if available
    acord_pdf = os.path.join(samples_dir, "ACORD-Automobile-Loss-Notice-12.05.16.pdf")
    if os.path.exists(acord_pdf):
        print("\n" + "="*60)
        print("PROCESSING ACORD PDF (from assessment)")
        print("="*60)
        
        result = agent.process_document(acord_pdf)
        
        print(f"ACORD PDF Results:")
        print(f"  Status: {result['status']}")
        print(f"  Extracted Fields: {len(result['extractedFields'])}")
        print(f"  Missing Fields: {len(result['missingFields'])}")
        if result['missingFields']:
            print(f"    - {', '.join(result['missingFields'])}")
        print(f"  Recommended Route: {result['recommendedRoute']}")
        print(f"  Reasoning: {result['reasoning']}")
        
        # Save ACORD results
        acord_output = os.path.join(output_dir, f"acord_results_{timestamp}.json")
        with open(acord_output, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        print(f"\nACORD results saved to: {acord_output}")
    
    print("\n" + "="*60)
    print("DEMO COMPLETE")
    print("="*60)
    print("\nThe FNOL Agent has successfully processed all sample documents.")
    print("Check the 'output/' directory for detailed JSON results.")


if __name__ == "__main__":
    run_demo()