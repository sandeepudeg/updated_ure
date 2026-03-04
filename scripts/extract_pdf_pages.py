#!/usr/bin/env python3
"""
Extract specific pages from government scheme PDFs
Creates separate PDFs for application forms, eligibility criteria, etc.
"""

import boto3
import PyPDF2
import io
import os
from pathlib import Path

S3_BUCKET = "ure-mvp-data-us-east-1-188238313375"
s3_client = boto3.client('s3', region_name='us-east-1')

# Define page ranges for each scheme
PDF_EXTRACTIONS = {
    "PMFBY_Scheme_Guidelines.pdf": {
        "application_form": {"pages": [14, 15, 16, 17], "output": "PMFBY_Application_Form.pdf"},
        "eligibility": {"pages": [4, 5, 6, 7], "output": "PMFBY_Eligibility_Criteria.pdf"},
        "claim_process": {"pages": [24, 25, 26, 27, 28, 29], "output": "PMFBY_Claim_Process.pdf"}
    },
    "PKVY_Organic_Farming_Guidelines.pdf": {
        "application_form": {"pages": [10, 11, 12, 13], "output": "PKVY_Application_Form.pdf"},
        "eligibility": {"pages": [3, 4, 5], "output": "PKVY_Eligibility_Criteria.pdf"}
    },
    "PMKSY_Irrigation_Manual.pdf": {
        "application_form": {"pages": [8, 9, 10, 11], "output": "PMKSY_Application_Form.pdf"},
        "eligibility": {"pages": [2, 3, 4], "output": "PMKSY_Eligibility_Criteria.pdf"}
    }
}

def download_pdf_from_s3(s3_key):
    """Download PDF from S3"""
    print(f"Downloading {s3_key} from S3...")
    response = s3_client.get_object(Bucket=S3_BUCKET, Key=s3_key)
    return io.BytesIO(response['Body'].read())

def extract_pages(pdf_stream, page_numbers):
    """Extract specific pages from PDF"""
    print(f"Extracting pages {page_numbers}...")
    reader = PyPDF2.PdfReader(pdf_stream)
    writer = PyPDF2.PdfWriter()
    
    for page_num in page_numbers:
        if page_num < len(reader.pages):
            writer.add_page(reader.pages[page_num])
    
    output_stream = io.BytesIO()
    writer.write(output_stream)
    output_stream.seek(0)
    return output_stream

def upload_to_s3(file_stream, s3_key):
    """Upload extracted PDF to S3"""
    print(f"Uploading {s3_key} to S3...")
    s3_client.put_object(
        Bucket=S3_BUCKET,
        Key=s3_key,
        Body=file_stream.getvalue(),
        ContentType='application/pdf'
    )
    print(f"✓ Uploaded: {s3_key}")

def process_all_pdfs():
    """Process all PDFs and extract pages"""
    print("="*60)
    print("PDF Page Extraction Tool")
    print("="*60)
    
    for source_pdf, extractions in PDF_EXTRACTIONS.items():
        print(f"\nProcessing: {source_pdf}")
        
        try:
            # Download source PDF
            s3_key = f"schemes/{source_pdf}"
            pdf_stream = download_pdf_from_s3(s3_key)
            
            # Extract each section
            for section_name, config in extractions.items():
                print(f"\n  Extracting {section_name}...")
                extracted_pdf = extract_pages(pdf_stream, config['pages'])
                
                # Upload to S3
                output_key = f"schemes/extracted/{config['output']}"
                upload_to_s3(extracted_pdf, output_key)
                
                # Reset stream for next extraction
                pdf_stream.seek(0)
            
            print(f"✓ Completed: {source_pdf}")
            
        except Exception as e:
            print(f"✗ Error processing {source_pdf}: {e}")
    
    print("\n" + "="*60)
    print("Extraction Complete")
    print("="*60)

if __name__ == "__main__":
    process_all_pdfs()
