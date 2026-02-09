# fnol-agent/src/document_loader.py - COMPLETE UPDATED VERSION
"""
Document loading and preprocessing module
"""

import os
import pdfplumber
import re
import PyPDF2
from typing import Dict, List, Optional, Union
import warnings

warnings.filterwarnings("ignore")

class DocumentLoader:
    """Handles loading and preprocessing of FNOL documents"""
    
    @staticmethod
    def load_document(file_path: str) -> Dict[str, Union[str, List]]:
        """
        Load document from file path, auto-detecting format
        
        Args:
            file_path: Path to document file
            
        Returns:
            Dictionary with text content and metadata
        """
        if not file_path:
            raise ValueError("File path cannot be empty")
        
        file_path_lower = file_path.lower()
        
        if file_path_lower.endswith('.pdf'):
            return DocumentLoader._load_pdf(file_path)
        elif file_path_lower.endswith('.txt'):
            return DocumentLoader._load_txt(file_path)
        else:
            raise ValueError(f"Unsupported file format: {file_path}")
    
    @staticmethod
    def _load_pdf(file_path: str) -> Dict[str, Union[str, List]]:
        """
        Extract text from PDF using multiple methods for robustness
        
        Args:
            file_path: Path to PDF file
            
        Returns:
            Dictionary with extracted text and tables
        """
        try:
            # Method 1: Use pdfplumber (better for structured forms)
            with pdfplumber.open(file_path) as pdf:
                full_text = ""
                all_tables = []
                
                for page_num, page in enumerate(pdf.pages, 1):
                    # Extract text
                    text = page.extract_text()
                    if text:
                        # Clean and normalize text
                        text = DocumentLoader._clean_text(text)
                        full_text += f"\n--- Page {page_num} ---\n{text}\n"
                    
                    # Extract tables if present
                    tables = page.extract_tables()
                    if tables:
                        for table in tables:
                            all_tables.append({
                                'page': page_num,
                                'table': table
                            })
                
                # Fallback if pdfplumber gets empty text
                if not full_text or len(full_text.strip()) < 100:
                    full_text = DocumentLoader._fallback_pdf_extraction(file_path)
                
                return {
                    'text': full_text.strip(),
                    'tables': all_tables,
                    'pages': len(pdf.pages),
                    'format': 'pdf'
                }
                
        except Exception as e:
            print(f"pdfplumber failed: {e}, trying PyPDF2 fallback...")
            return {
                'text': DocumentLoader._fallback_pdf_extraction(file_path),
                'tables': [],
                'pages': 1,
                'format': 'pdf'
            }
    
    @staticmethod
    def _load_txt(file_path: str) -> Dict[str, Union[str, List]]:
        """
        Load plain text document with robust error handling
        
        Args:
            file_path: Path to text file
            
        Returns:
            Dictionary with text content
        """
        try:
            # First check if file exists
            if not os.path.exists(file_path):
                print(f"ERROR: File not found: {file_path}")
                return {
                    'text': '',
                    'tables': [],
                    'pages': 1,
                    'format': 'txt'
                }
            
            # Try multiple encodings in order
            encodings_to_try = ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252', 'iso-8859-1', 'ascii']
            
            for encoding in encodings_to_try:
                try:
                    with open(file_path, 'r', encoding=encoding) as f:
                        text = f.read()
                    
                    # If we got here, reading succeeded
                    if text:  # Check if we actually got content
                        # Clean text
                        text = DocumentLoader._clean_text(text)
                        
                        return {
                            'text': text,
                            'tables': [],
                            'pages': 1,
                            'format': 'txt'
                        }
                    else:
                        print(f"WARNING: File {file_path} is empty or couldn't be read with {encoding}")
                        
                except UnicodeDecodeError:
                    # Try next encoding
                    continue
                except Exception as e:
                    print(f"Error reading {file_path} with {encoding}: {e}")
                    continue
            
            # If all encodings fail, try binary read with error ignoring
            print(f"WARNING: All encodings failed for {file_path}, trying binary read...")
            try:
                with open(file_path, 'rb') as f:
                    raw_data = f.read()
                
                # Try to decode with error ignoring
                text = raw_data.decode('utf-8', errors='ignore')
                text = DocumentLoader._clean_text(text)
                
                return {
                    'text': text,
                    'tables': [],
                    'pages': 1,
                    'format': 'txt'
                }
            except Exception as e:
                print(f"ERROR: Binary read also failed for {file_path}: {e}")
                
        except Exception as e:
            print(f"ERROR loading TXT file {file_path}: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
        
        # Return empty result if everything fails
        return {
            'text': '',
            'tables': [],
            'pages': 1,
            'format': 'txt'
        }
    
    @staticmethod
    def _fallback_pdf_extraction(file_path: str) -> str:
        """Fallback PDF extraction using PyPDF2"""
        try:
            full_text = ""
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                for page_num in range(len(pdf_reader.pages)):
                    page = pdf_reader.pages[page_num]
                    text = page.extract_text()
                    if text:
                        text = DocumentLoader._clean_text(text)
                        full_text += f"\n--- Page {page_num + 1} ---\n{text}\n"
            
            return full_text.strip()
        except Exception as e:
            print(f"PyPDF2 extraction failed: {e}")
            return "PDF extraction failed"
    
    @staticmethod
    def _clean_text(text: str) -> str:
        """
        Clean and normalize text
        
        Args:
            text: Raw text to clean
            
        Returns:
            Cleaned text
        """
        if not text:
            return ""
        
        # Replace multiple spaces/newlines with single space
        text = re.sub(r'\s+', ' ', text)
        
        # Fix common OCR issues
        replacements = {
            '|': 'I',
            'l': 'I',
            '０': '0',
            '１': '1',
            '２': '2',
            '３': '3',
            '４': '4',
            '５': '5',
            '６': '6',
            '７': '7',
            '８': '8',
            '９': '9',
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
            '％': '%',
            '＆': '&',
            '＠': '@',
            '＃': '#',
            '＊': '*',
            '＋': '+',
            '＝': '=',
            '～': '~',
            '＾': '^',
            '＿': '_',
            '－': '-',
            '／': '/',
            '＼': '\\',
            '｜': '|',
            '＜': '<',
            '＞': '>',
            '？': '?',
            '！': '!',
            '＂': '"',
            '＇': "'",
            '｀': '`',
        }
        
        for old, new in replacements.items():
            text = text.replace(old, new)
        
        # Remove control characters
        text = ''.join(char for char in text if ord(char) >= 32 or ord(char) in [9, 10, 13])
        
        return text.strip()