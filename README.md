# FNOL Agent - First Notice of Loss Processing System

<div align="center">

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Documentation](https://img.shields.io/badge/docs-passing-brightgreen)](#)
[![Code Style](https://img.shields.io/badge/code%20style-black-black)](https://github.com/psf/black)

**An intelligent system for automated insurance claim processing**

</div>

## Overview

The **FNOL Agent** is an intelligent document processing system designed to automate the handling of First Notice of Loss (FNOL) insurance claims. It extracts key information from unstructured claim documents, validates the data, and routes claims to appropriate workflows based on configurable business rules.

### Key Capabilities

- **Document Processing**: PDF and TXT file support
- **Field Extraction**: AI-powered extraction of policy, incident, and asset details
- **Smart Routing**: Rule-based claim classification and routing
- **Fraud Detection**: Identification of suspicious claims
- **Batch Processing**: High-volume document handling
- **ACORD Form Support**: Specialized parser for industry-standard forms

## Features

### Core Functionality

- **Multi-format Document Support**: Process PDFs and text files with robust error handling
- **Intelligent Field Extraction**: Regex-based extraction with fallback patterns
- **ACORD Form Specialization**: Dedicated parser for insurance industry forms
- **Rule-based Routing Engine**: Configurable business rules for claim handling
- **Fraud & Anomaly Detection**: Keyword-based fraud identification
- **Batch Processing**: Efficient handling of multiple documents

### Technical Features

- **Modular Architecture**: Clean separation of concerns
- **Configurable Rules**: Easy adjustment of thresholds and keywords
- **JSON Output**: Standardized output format
- **Comprehensive Logging**: Detailed processing statistics
- **Unit Test Coverage**: Robust testing framework
- **CLI Interface**: Easy command-line usage

## Quick Start

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/fnol-agent.git
cd fnol-agent

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```
