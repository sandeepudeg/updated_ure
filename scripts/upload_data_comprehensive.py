#!/usr/bin/env python3
"""
Comprehensive Data Upload Script for GramSetu
Uploads crop disease images, government schemes, and market prices to S3
"""

import sys
import os
import argparse
import logging
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from utils.s3_uploader import S3Uploader

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def check_data_availability():
    """Check what data is available locally"""
    data_dir = Path('data')
    
    available_data = {
        'government_schemes': data_dir / 'government_schemes',
        'market_prices': data_dir / 'mandi_prices' / 'Agriculture_price_dataset.csv',
        'plantvillage_train': data_dir / 'plantvillage' / 'New Plant Diseases Dataset(Augmented)',
        'plantvillage_test': data_dir / 'plantvillage' / 'test',
        'sample_farmers': data_dir / 'sample_farmers.csv'
    }
    
    logger.info("=" * 60)
    logger.info("Checking Local Data Availability")
    logger.info("=" * 60)
    
    for name, path in available_data.items():
        if path.exists():
            if path.is_dir():
                file_count = len(list(path.rglob('*')))
                logger.info(f"✓ {name}: {path} ({file_count} files)")
            else:
                size_mb = path.stat().st_size / (1024 * 1024)
                logger.info(f"✓ {name}: {path} ({size_mb:.2f} MB)")
        else:
            logger.warning(f"✗ {name}: {path} (NOT FOUND)")
    
    logger.info("=" * 60 + "\n")
    
    return available_data


def upload_all_data(bucket_name, region='us-east-1', dry_run=False):
    """Upload all available data to S3"""
    
    logger.info("=" * 60)
    logger.info("GramSetu Data Upload to S3")
    logger.info("=" * 60)
    logger.info(f"Bucket: {bucket_name}")
    logger.info(f"Region: {region}")
    logger.info(f"Dry Run: {dry_run}")
    logger.info("=" * 60 + "\n")
    
    # Check available data
    available_data = check_data_availability()
    
    # Initialize uploader
    uploader = S3Uploader(bucket_name=bucket_name, region=region)
    
    # Ensure bucket exists
    logger.info("Checking S3 bucket...")
    uploader.create_bucket_if_not_exists()
    uploader.enable_versioning()
    logger.info("✓ Bucket ready\n")
    
    upload_stats = {}
    
    # 1. Upload Government Schemes
    if available_data['government_schemes'].exists():
        logger.info("=" * 60)
        logger.info("1. Uploading Government Scheme PDFs")
        logger.info("=" * 60)
        
        if not dry_run:
            stats = uploader.upload_scheme_pdfs(str(available_data['government_schemes']))
            upload_stats['schemes'] = stats
            logger.info(f"✓ Schemes uploaded: {stats}\n")
        else:
            logger.info("[DRY RUN] Would upload scheme PDFs\n")
    
    # 2. Upload Market Prices
    if available_data['market_prices'].exists():
        logger.info("=" * 60)
        logger.info("2. Uploading Market Prices Dataset")
        logger.info("=" * 60)
        
        if not dry_run:
            success = uploader.upload_agmarknet_data(str(available_data['market_prices']))
            upload_stats['market_prices'] = 'Success' if success else 'Failed'
            logger.info(f"✓ Market prices uploaded: {success}\n")
        else:
            logger.info("[DRY RUN] Would upload market prices\n")
    
    # 3. Upload PlantVillage Training Dataset
    if available_data['plantvillage_train'].exists():
        logger.info("=" * 60)
        logger.info("3. Uploading Crop Disease Images (Training)")
        logger.info("=" * 60)
        logger.info("⚠ This may take 30-60 minutes for large datasets")
        
        if not dry_run:
            stats = uploader.upload_plantvillage_dataset(str(available_data['plantvillage_train']))
            upload_stats['plantvillage_train'] = stats
            logger.info(f"✓ Training images uploaded: {stats}\n")
        else:
            logger.info("[DRY RUN] Would upload training images\n")
    
    # 4. Upload PlantVillage Test Dataset
    if available_data['plantvillage_test'].exists():
        logger.info("=" * 60)
        logger.info("4. Uploading Crop Disease Images (Test)")
        logger.info("=" * 60)
        
        if not dry_run:
            # Upload test dataset to separate prefix
            import boto3
            s3_client = boto3.client('s3', region_name=region)
            
            test_files = list(available_data['plantvillage_test'].rglob('*'))
            test_files = [f for f in test_files if f.is_file()]
            
            uploaded = 0
            for file_path in test_files:
                relative_path = file_path.relative_to(available_data['plantvillage_test'])
                s3_key = f"plantvillage-test/{relative_path}"
                
                try:
                    s3_client.upload_file(
                        str(file_path),
                        bucket_name,
                        s3_key
                    )
                    uploaded += 1
                    if uploaded % 100 == 0:
                        logger.info(f"  Uploaded {uploaded}/{len(test_files)} files...")
                except Exception as e:
                    logger.error(f"  Failed to upload {file_path}: {e}")
            
            upload_stats['plantvillage_test'] = f"{uploaded}/{len(test_files)} files"
            logger.info(f"✓ Test images uploaded: {uploaded}/{len(test_files)}\n")
        else:
            logger.info("[DRY RUN] Would upload test images\n")
    
    # 5. Upload Sample Farmers Data
    if available_data['sample_farmers'].exists():
        logger.info("=" * 60)
        logger.info("5. Uploading Sample Farmers Data")
        logger.info("=" * 60)
        
        if not dry_run:
            import boto3
            s3_client = boto3.client('s3', region_name=region)
            
            try:
                s3_client.upload_file(
                    str(available_data['sample_farmers']),
                    bucket_name,
                    'datasets/sample_farmers.csv'
                )
                upload_stats['sample_farmers'] = 'Success'
                logger.info("✓ Sample farmers data uploaded\n")
            except Exception as e:
                logger.error(f"✗ Failed to upload sample farmers: {e}\n")
                upload_stats['sample_farmers'] = 'Failed'
        else:
            logger.info("[DRY RUN] Would upload sample farmers data\n")
    
    # Summary
    logger.info("=" * 60)
    logger.info("Upload Summary")
    logger.info("=" * 60)
    
    if dry_run:
        logger.info("\n[DRY RUN] No files were actually uploaded")
        logger.info("Run without --dry-run flag to perform actual upload\n")
    else:
        logger.info("\nUpload Statistics:")
        for key, value in upload_stats.items():
            logger.info(f"  {key}: {value}")
        
        logger.info("\n✓ Data upload complete!")
        logger.info("\nNext Steps:")
        logger.info("  1. Verify data in S3 console or CLI")
        logger.info("  2. Update Bedrock Knowledge Base to index scheme PDFs")
        logger.info("  3. Test crop disease detection")
        logger.info("  4. Test market price queries")
        logger.info("=" * 60 + "\n")


def main():
    parser = argparse.ArgumentParser(
        description='Upload all GramSetu data to S3'
    )
    
    parser.add_argument(
        '--bucket',
        default='ure-mvp-data-us-east-1-188238313375',
        help='S3 bucket name'
    )
    parser.add_argument(
        '--region',
        default='us-east-1',
        help='AWS region'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be uploaded without actually uploading'
    )
    
    args = parser.parse_args()
    
    try:
        upload_all_data(
            bucket_name=args.bucket,
            region=args.region,
            dry_run=args.dry_run
        )
    except Exception as e:
        logger.error(f"\n✗ Upload failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
