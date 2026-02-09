# fnol-agent/src/main.py - UPDATED VERSION
"""
Main orchestrator for FNOL processing pipeline
"""

import json
import os
import sys
from datetime import datetime
from typing import Dict, List, Optional

# FIXED IMPORTS - removed the dots for compatibility
try:
    # Try relative imports first (for package mode)
    from .document_loader import DocumentLoader
    from .field_extractor import FieldExtractor
    from .routing_engine import RoutingEngine
    from .config import config
    from .acord_parser import ACORDParser
except ImportError:
    # Fallback to absolute imports (for script mode)
    from document_loader import DocumentLoader
    from field_extractor import FieldExtractor
    from routing_engine import RoutingEngine
    from config import config
    from acord_parser import ACORDParser


class FNOLAgent:
    """Main agent class orchestrating the FNOL processing pipeline"""
    
    def __init__(self, verbose: bool = False):
        """
        Initialize the FNOL Agent
        
        Args:
            verbose: Whether to print detailed processing information
        """
        self.loader = DocumentLoader()
        self.extractor = FieldExtractor()
        self.router = RoutingEngine()
        self.verbose = verbose
        
        # Processing statistics
        self.stats = {
            'processed': 0,
            'errors': 0,
            'routes': {},
            'avg_processing_time': 0
        }
    
    def process_document(self, file_path: str) -> Dict:
        """
        Process a single FNOL document
        
        Args:
            file_path: Path to the document file
            
        Returns:
            Dictionary with processing results
        """
        start_time = datetime.now()
        
        result = {
            'document': os.path.basename(file_path),
            'timestamp': start_time.isoformat(),
            'status': 'success',
            'extractedFields': {},
            'missingFields': [],
            'validation': {},
            'recommendedRoute': '',
            'reasoning': '',
            'processingTime': 0
        }
        
        try:
            if self.verbose:
                print(f"Processing: {file_path}")
            
            # 1. Load document
            document_data = self.loader.load_document(file_path)
            
            if not document_data.get('text'):
                raise ValueError(f"No text could be extracted from {file_path}")
            
            # 2. Extract fields - CHECK FOR ACORD FORMS
            text = document_data['text']
            
            # Check if this is an ACORD form
            if 'ACORD' in text.upper() or 'acord' in text.lower():
                if self.verbose:
                    print("  Detected ACORD form, using specialized parser")
                extracted_fields = ACORDParser.extract_acord_fields(text)
            else:
                extracted_fields = self.extractor.extract_all_fields(text)
            
            # 3. Identify missing fields
            missing_fields = self.extractor.identify_missing_fields(extracted_fields)
            
            # 4. Validate extracted data
            validation_results = self.router.validate_extracted_data(extracted_fields)
            
            # 5. Determine routing
            route, reasoning = self.router.determine_route(extracted_fields, missing_fields)
            
            # 6. Compile results
            result['extractedFields'] = extracted_fields
            result['missingFields'] = missing_fields
            result['validation'] = validation_results
            result['recommendedRoute'] = route
            result['reasoning'] = reasoning
            
            # Update statistics
            self.stats['processed'] += 1
            if route in self.stats['routes']:
                self.stats['routes'][route] += 1
            else:
                self.stats['routes'][route] = 1
            
            if self.verbose:
                print(f"  Extracted {len(extracted_fields)} fields")
                print(f"  Missing: {len(missing_fields)} fields")
                print(f"  Route: {route}")
                if missing_fields:
                    print(f"  Missing fields: {missing_fields}")
            
        except Exception as e:
            result['status'] = 'error'
            result['error'] = str(e)
            result['recommendedRoute'] = 'Error - Manual Review'
            result['reasoning'] = f'Processing error: {str(e)}'
            
            self.stats['errors'] += 1
            
            if self.verbose:
                print(f"  ERROR: {str(e)}")
        
        # Calculate processing time
        end_time = datetime.now()
        processing_time = (end_time - start_time).total_seconds()
        result['processingTime'] = processing_time
        
        # Update average processing time
        if self.stats['processed'] > 0:
            self.stats['avg_processing_time'] = (
                (self.stats['avg_processing_time'] * (self.stats['processed'] - 1) + processing_time) 
                / self.stats['processed']
            )
        
        return result
    
    def process_batch(self, file_paths: List[str]) -> List[Dict]:
        """
        Process multiple documents
        
        Args:
            file_paths: List of file paths to process
            
        Returns:
            List of processing results
        """
        results = []
        
        if self.verbose:
            print(f"Processing batch of {len(file_paths)} documents...")
        
        for file_path in file_paths:
            result = self.process_document(file_path)
            results.append(result)
        
        if self.verbose:
            print(f"\nBatch processing complete:")
            print(f"  Successfully processed: {self.stats['processed'] - self.stats['errors']}")
            print(f"  Errors: {self.stats['errors']}")
            print(f"  Routes: {self.stats['routes']}")
            print(f"  Average processing time: {self.stats['avg_processing_time']:.2f} seconds")
        
        return results
    
    def save_results(self, results: Dict, output_path: str):
        """
        Save processing results to JSON file
        
        Args:
            results: Processing results dictionary
            output_path: Path to save JSON file
        """
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            
            if self.verbose:
                print(f"Results saved to: {output_path}")
                
        except Exception as e:
            print(f"Error saving results: {e}")
    
    def get_statistics(self) -> Dict:
        """
        Get processing statistics
        
        Returns:
            Dictionary with statistics
        """
        return self.stats.copy()


def main():
    """Command-line interface for the FNOL Agent"""
    import argparse
    
    parser = argparse.ArgumentParser(description='FNOL Processing Agent')
    parser.add_argument('input', help='Input file or directory')
    parser.add_argument('-o', '--output', help='Output file path (JSON)')
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output')
    parser.add_argument('-b', '--batch', action='store_true', help='Process directory in batch')
    
    args = parser.parse_args()
    
    agent = FNOLAgent(verbose=args.verbose)
    
    if args.batch:
        # Process directory
        if not os.path.isdir(args.input):
            print(f"Error: {args.input} is not a directory")
            sys.exit(1)
        
        # Get all PDF and TXT files
        file_paths = []
        for ext in ['*.pdf', '*.txt']:
            import glob
            file_paths.extend(glob.glob(os.path.join(args.input, ext)))
        
        if not file_paths:
            print(f"No PDF or TXT files found in {args.input}")
            sys.exit(1)
        
        results = agent.process_batch(file_paths)
        
    else:
        # Process single file
        if not os.path.isfile(args.input):
            print(f"Error: {args.input} is not a file")
            sys.exit(1)
        
        result = agent.process_document(args.input)
        results = [result]
    
    # Output results
    if args.output:
        if args.batch:
            agent.save_results(results, args.output)
        else:
            agent.save_results(results[0], args.output)
    else:
        # Print to console
        print(json.dumps(results[0] if not args.batch else results, indent=2))
    
    # Print summary
    if args.verbose:
        stats = agent.get_statistics()
        print(f"\nSummary Statistics:")
        print(f"  Total processed: {stats['processed']}")
        print(f"  Errors: {stats['errors']}")
        print(f"  Routes: {json.dumps(stats['routes'], indent=2)}")
        print(f"  Average time: {stats['avg_processing_time']:.2f}s")


if __name__ == "__main__":
    main()