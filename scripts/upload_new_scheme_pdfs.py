#!/usr/bin/env python3
"""
Upload new government scheme PDFs to S3
"""

import boto3
import os
from pathlib import Path

S3_BUCKET = "ure-mvp-data-us-east-1-188238313375"
s3_client = boto3.client('s3', region_name='us-east-1')

# New PDFs to upload
NEW_PDFS = [
    "Chief_Minister's_Agriculture_Insurance_Scheme_Teachers-Statutory-Officers-27-02-2026.pdf",
    "Krishi_Sanjeevani_Yojana_Notification_-_Green_House___Shadenet_House_Erector.pdf",
    "Pradhan_Mantri_Kisan_Samman_Nidhi_finalKCCCircular.pdf",
    "Pradhan_Mantri_Krishi_Sinchai_Yojana_Revalidation Letter 2021-22.pdf"
]

def upload_pdf_to_s3(local_path, s3_key):
    """Upload PDF to S3"""
    print(f"Uploading {s3_key}...")
    
    with open(local_path, 'rb') as f:
        s3_client.put_object(
            Bucket=S3_BUCKET,
            Key=s3_key,
            Body=f,
            ContentType='application/pdf'
        )
    
    print(f"✓ Uploaded: {s3_key}")

def main():
    print("="*60)
    print("Upload New Government Scheme PDFs to S3")
    print("="*60)
    
    data_dir = Path("data/government_schemes")
    
    for pdf_name in NEW_PDFS:
        local_path = data_dir / pdf_name
        
        if local_path.exists():
            # Clean filename for S3 (replace spaces with underscores)
            clean_name = pdf_name.replace(" ", "_")
            s3_key = f"schemes/{clean_name}"
            
            try:
                upload_pdf_to_s3(local_path, s3_key)
            except Exception as e:
                print(f"✗ Error uploading {pdf_name}: {e}")
        else:
            print(f"⚠ File not found: {local_path}")
    
    print("\n" + "="*60)
    print("Upload Complete")
    print("="*60)
    print("\nNew PDFs uploaded:")
    for pdf in NEW_PDFS:
        clean_name = pdf.replace(" ", "_")
        print(f"  - schemes/{clean_name}")

if __name__ == "__main__":
    main()
