# Implementation Plan: AWS Privacy & Security Suite MVP

## Overview

This plan implements privacy and security enhancements for the GramSetu agricultural assistant, focusing on anonymous authentication via Amazon Cognito, automatic data deletion with DynamoDB TTL, IP address hashing, encryption at rest, and seamless legacy user migration. The implementation uses Python 3.11 for Lambda functions and deployment scripts, with comprehensive testing using pytest and hypothesis for property-based tests.

## Tasks

- [ ] 1. Set up core privacy infrastructure
  - [x] 1.1 Create Cognito Identity Pool and IAM roles
    - Implement `scripts/setup_cognito.py` to create Cognito Identity Pool with unauthenticated access
    - Create IAM role for unauthenticated users with API Gateway invoke permissions
    - Create DynamoDB table `ure-user-migrations` for tracking legacy user migrations
    - _Requirements: 1.1, 1.2_
  
  - [ ]* 1.2 Write property test for Cognito identity generation performance
    - **Property 1: Cognito Identity Generation Performance**
    - **Validates: Requirements 1.2**
    - Test that Cognito generates Identity IDs within 2 seconds for any anonymous user request
    - _Requirements: 1.2_
  
  - [ ]* 1.3 Write property test for credential expiration correctness
    - **Property 2: Credential Expiration Correctness**
    - **Validates: Requirements 1.3**
    - Test that generated credentials expire 60 minutes (±1 minute) from issuance
    - _Requirements: 1.3_
  
  - [ ]* 1.4 Write unit test for Cognito pool configuration
    - Test that Cognito Identity Pool allows unauthenticated access
    - Verify pool name and configuration settings
    - _Requirements: 1.1, 1.2_

- [ ] 2. Implement privacy components in Lambda
  - [x] 2.1 Implement IP Address Hasher component
    - Create `IPAddressHasher` class with SHA-256 hashing using salt
    - Implement IP extraction from API Gateway events (handle X-Forwarded-For)
    - Add environment variable support for `IP_HASH_SALT`
    - _Requirements: 4.1, 4.2, 4.3_
  
  - [ ]* 2.2 Write property test for IP address hashing determinism
    - **Property 10: IP Address Hashing Determinism**
    - **Validates: Requirements 4.1, 4.2**
    - Test that hashing the same IP multiple times produces identical results
    - Test that different IPs produce different hashes
    - _Requirements: 4.1, 4.2_
  
  - [ ]* 2.3 Write unit test for IP hashing with missing salt
    - Test IP hashing behavior when salt environment variable is not configured
    - Verify it uses default salt and logs warning
    - _Requirements: 4.3_
  
  - [x] 2.4 Implement TTL Manager component
    - Create `TTLManager` class with 3-hour session duration calculation
    - Implement `calculate_expiry_time()` method returning Unix timestamp
    - Implement `extend_session()` method for session extension on user interaction
    - _Requirements: 3.1, 3.2, 3.4_
  
  - [ ]* 2.5 Write property test for TTL attribute correctness
    - **Property 8: TTL Attribute Correctness**
    - **Validates: Requirements 3.1, 3.2**
    - Test that expiry_time is set to ~3 hours (10800 seconds ±60 seconds) from current time
    - _Requirements: 3.1, 3.2_
  
  - [ ]* 2.6 Write unit test for TTL configuration verification
    - Test that TTL is enabled on all required DynamoDB tables
    - Verify TTL attribute name is 'expiry_time'
    - _Requirements: 3.1, 3.3_

- [ ] 3. Implement legacy user migration
  - [x] 3.1 Implement migration detection logic
    - Create `detect_migration_needed()` function to identify legacy users (farmer_* format)
    - Handle three cases: new Cognito users, legacy users, already migrated users
    - _Requirements: 2.1, 2.4_
  
  - [x] 3.2 Implement migration handler
    - Create `migrate_user_data()` function to copy conversations and profiles
    - Implement idempotency check using `ure-user-migrations` table
    - Copy data from legacy user_id to Cognito Identity ID
    - Set short TTL (1 hour) on legacy records for cleanup
    - Record migration in tracking table with 30-day TTL
    - _Requirements: 2.2, 2.3, 2.5_
  
  - [ ]* 3.3 Write property test for complete data migration
    - **Property 6: Complete Data Migration**
    - **Validates: Requirements 2.2, 2.3**
    - Test that all legacy user data (conversations, profile) is accessible via Cognito ID after migration
    - Verify no data loss during migration
    - _Requirements: 2.2, 2.3_
  
  - [ ]* 3.4 Write unit test for empty legacy user migration
    - Test migration for legacy user with no existing data
    - Verify migration completes successfully with zero conversations
    - _Requirements: 2.2_

- [x] 4. Checkpoint - Verify core components
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 5. Integrate privacy features into Lambda handler
  - [x] 5.1 Update Lambda handler with IP hashing
    - Initialize `IPAddressHasher` at module level
    - Extract and hash IP address in `lambda_handler()`
    - Store hashed IP in conversation metadata, never store plaintext IP
    - _Requirements: 4.1, 4.2, 4.4_
  
  - [ ]* 5.2 Write property test for no plaintext IP storage
    - **Property 11: No Plaintext IP Storage**
    - **Validates: Requirements 4.4**
    - Test that stored DynamoDB records never contain plaintext IP addresses
    - _Requirements: 4.4_
  
  - [x] 5.3 Update conversation storage with TTL
    - Modify `store_conversation_with_ttl()` to calculate and set expiry_time
    - Extend TTL on every user interaction (session extension)
    - Implement fallback to store without TTL if update fails
    - _Requirements: 3.1, 3.2, 3.4_
  
  - [ ] 5.4 Integrate migration handler into Lambda
    - Call `detect_migration_needed()` on every request
    - Trigger `migrate_user_data()` for legacy users
    - Handle migration errors gracefully with rollback
    - _Requirements: 2.1, 2.2, 2.3_
  
  - [ ] 5.5 Add Cognito authentication support
    - Accept both legacy user_id and cognito_identity_id in requests
    - Support dual authentication during 30-day migration window
    - Implement graceful fallback if Cognito is unavailable
    - _Requirements: 1.4, 1.5, 2.5_

- [ ] 6. Implement data deletion API
  - [ ] 6.1 Create data deletion function
    - Implement `delete_user_data()` function to remove conversations, profiles, and S3 uploads
    - Add retry logic with exponential backoff for failed deletions
    - Return detailed status of deleted and failed items
    - _Requirements: 9.1, 9.2_
  
  - [ ] 6.2 Add deletion endpoint to Lambda handler
    - Handle `action: delete_user_data` requests
    - Validate confirmation token "DELETE_MY_DATA"
    - Return success/failure status with deleted items list
    - _Requirements: 9.1, 9.2_
  
  - [ ]* 6.3 Write property test for data deletion completeness
    - **Property 14: Data Deletion Completeness**
    - **Validates: Requirements 9.2**
    - Test that all user data is deleted within 5 minutes
    - Verify subsequent queries return no data
    - _Requirements: 9.2_
  
  - [ ]* 6.4 Write unit test for complete data removal
    - Create test user with conversations, profile, and S3 uploads
    - Execute deletion and verify all records are removed
    - _Requirements: 9.2_

- [ ] 7. Create deployment scripts
  - [ ] 7.1 Create pre-deployment validation script
    - Implement `scripts/pre_deployment_check.py` to verify AWS credentials
    - Check required IAM permissions
    - Verify existing infrastructure (tables, bucket, Lambda)
    - Enable point-in-time recovery backups on DynamoDB tables
    - _Requirements: 8.1, 8.5_
  
  - [ ] 7.2 Create privacy features enablement script
    - Implement `scripts/enable_privacy_features.py` to enable DynamoDB encryption
    - Enable DynamoDB TTL on all tables (ure-conversations, ure-user-profiles, ure-user-migrations)
    - Enable S3 bucket encryption with AWS-managed KMS keys
    - _Requirements: 5.1, 5.2, 3.1, 3.3_
  
  - [ ]* 7.3 Write unit test for encryption configuration
    - Test that encryption is enabled on all DynamoDB tables
    - Verify S3 bucket has default encryption enabled
    - Check encryption uses AWS-managed KMS keys
    - _Requirements: 5.1, 5.2_
  
  - [ ] 7.4 Create Lambda deployment script
    - Implement `scripts/deploy_lambda_privacy_update.py` to update Lambda environment variables
    - Generate random IP hash salt using secrets.token_hex(16)
    - Create deployment package with updated Lambda code
    - Deploy Lambda function code and wait for update completion
    - _Requirements: 8.2, 8.3, 4.3_
  
  - [ ] 7.5 Create rollback script
    - Implement `scripts/rollback_privacy_features.py` to rollback Lambda to previous version
    - Add option to disable TTL on tables
    - Add option to restore tables from backup
    - _Requirements: 8.4_
  
  - [ ] 7.6 Create monitoring dashboard script
    - Implement `scripts/create_monitoring_dashboard.py` to create CloudWatch dashboard
    - Add widgets for Lambda performance (duration, errors, invocations)
    - Add widgets for DynamoDB errors
    - Add log insights query for migration logs
    - _Requirements: 8.6_
  
  - [ ] 7.7 Create deployment validation script
    - Implement `scripts/validate_deployment.py` to check TTL on sample records
    - Verify no plaintext IPs in stored data
    - Check for migrated users in database
    - _Requirements: 8.5_
  
  - [ ] 7.8 Create migration statistics script
    - Implement `scripts/get_migration_stats.py` to query ure-user-migrations table
    - Report total migrations, success rate, and failed migrations
    - Show migration timeline and progress
    - _Requirements: 2.6_

- [ ] 8. Checkpoint - Verify deployment scripts
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 9. Implement frontend Cognito integration
  - [ ] 9.1 Add AWS SDK and Cognito configuration
    - Add AWS SDK to frontend dependencies
    - Create config.js with Cognito Identity Pool ID
    - Initialize AWS.CognitoIdentityCredentials
    - _Requirements: 1.1, 1.2_
  
  - [ ] 9.2 Implement user identity management
    - Create auth.js with `getUserIdentity()` function
    - Detect legacy user IDs (farmer_* format) in localStorage
    - Trigger migration by sending both legacy and Cognito IDs to Lambda
    - Update localStorage with Cognito Identity ID after migration
    - _Requirements: 1.4, 2.1, 2.4_
  
  - [ ] 9.3 Implement credential auto-refresh
    - Set up interval to refresh credentials every 55 minutes (5 min before expiry)
    - Handle refresh failures gracefully
    - _Requirements: 1.5_
  
  - [ ] 9.4 Add data deletion UI
    - Create deleteMyData() function with user confirmation
    - Call deletion API with confirmation token
    - Clear localStorage and reload page on success
    - _Requirements: 9.1_

- [ ] 10. Testing and validation
  - [ ]* 10.1 Write property test for response time performance
    - **Property 12: Response Time Performance**
    - **Validates: Requirements 7.1, 7.2**
    - Test that 95th percentile response time is below 3 seconds for 100 consecutive requests
    - _Requirements: 7.1, 7.2_
  
  - [ ]* 10.2 Write property test for deployment script validation
    - **Property 13: Deployment Script Credential Validation**
    - **Validates: Requirements 8.5**
    - Test that deployment scripts validate AWS credentials before modifications
    - Verify scripts fail fast with invalid credentials
    - _Requirements: 8.5_
  
  - [ ]* 10.3 Write unit test for HTTPS enforcement
    - Test that HTTP requests are redirected to HTTPS
    - Verify redirect status code (301 or 302)
    - Check Location header starts with https://
    - _Requirements: 6.1_
  
  - [ ] 10.4 Run all unit tests
    - Execute pytest on all unit tests
    - Verify all tests pass
    - Generate coverage report
    - _Requirements: All_
  
  - [ ] 10.5 Run all property-based tests
    - Execute pytest with hypothesis on all property tests
    - Use CI profile with 200 examples per test
    - Verify all properties hold
    - _Requirements: All_

- [ ] 11. Final checkpoint and documentation
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional testing tasks and can be skipped for faster MVP delivery
- Each task references specific requirements from requirements-mvp.md for traceability
- Property tests validate universal correctness properties using hypothesis library (100-200 examples per test)
- Unit tests validate specific examples, edge cases, and configuration
- Deployment scripts are numbered 1-8 as specified in requirements
- Migration window is 30 days for dual authentication support
- TTL deletion occurs automatically within 48 hours after expiry time
- IP hash salt must be saved securely during deployment (cannot be recovered if lost)
- All encryption uses AWS-managed KMS keys (no additional cost)
- Frontend changes require CloudFront cache invalidation after deployment
