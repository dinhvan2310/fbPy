# -*- coding: utf-8 -*-
"""
Security module with obfuscated license checking mechanism
Complex system info gathering and permission validation
"""

import platform
import psutil
import hashlib
import base64
import json
import os
import sys
from datetime import datetime
from typing import Dict, Optional, Tuple

# Firebase Admin SDK
import firebase_admin
from firebase_admin import credentials, firestore

# Encryption for credentials
try:
    from cryptography.fernet import Fernet
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    CRYPTOGRAPHY_AVAILABLE = True
except ImportError:
    CRYPTOGRAPHY_AVAILABLE = False


def _get_base_path():
    """Lấy đường dẫn cơ sở khi chạy từ EXE hoặc script"""
    try:
        # PyInstaller tạo thư mục tạm và lưu đường dẫn trong _MEIPASS
        return sys._MEIPASS
    except Exception:
        # Nếu không phải EXE, dùng thư mục của file hiện tại
        return os.path.dirname(os.path.abspath(__file__))

# Constants - obfuscated naming
CONSTANTS = {
    # Align with frontend constants
    'checkLicense': 'a1',
    'ok': 'a2',
    'denied': 'a3',
    'keyNotFound': 'a4',
    'licences': 'licences',  # Firestore collection name
    'license': 'license'
}

# Firebase configuration - embedded directly (matching frontend config)
FIREBASE_CONFIG = {
    'apiKey': 'AIzaSyC31wKz6n9ioe1i62mCeV1d5zlvCwo_mrU',
    'authDomain': 'adsmanage-e9e5e.firebaseapp.com',
    'projectId': 'adsmanage-e9e5e',
    'storageBucket': 'adsmanage-e9e5e.firebasestorage.app',
    'messagingSenderId': '315379263916',
    'appId': '1:315379263916:web:a079d97ac7b42b28ff7209'
}

# Service Account Credentials - embedded directly
# NOTE: Bạn có thể:
# 1. Copy credentials vào đây (như dict bên dưới)
# 2. Hoặc đặt file JSON credentials trong cùng thư mục (tên file: firebase-credentials.json)
# 3. Hoặc để trống và script sẽ thử dùng Application Default Credentials
SERVICE_ACCOUNT_CREDENTIALS = {
    # Để trống nếu muốn dùng file JSON hoặc Application Default Credentials
    # Hoặc điền thông tin service account từ Firebase Console:
    # "type": "service_account",
    # "project_id": "adsmanage-e9e5e",
    # "private_key_id": "...",
    # "private_key": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n",
    # "client_email": "firebase-adminsdk-xxxxx@adsmanage-e9e5e.iam.gserviceaccount.com",
    # "client_id": "...",
    # "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    # "token_uri": "https://oauth2.googleapis.com/token",
    # "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    # "client_x509_cert_url": "..."
}

# Path to credentials JSON file (if using file instead of embedded dict)
# Xử lý đường dẫn khi chạy từ EXE
_base_path = _get_base_path()
CREDENTIALS_JSON_FILE = os.path.join(_base_path, 'firebase-credentials.json')
CREDENTIALS_ENCRYPTED_FILE = os.path.join(_base_path, 'firebase-credentials.json.enc')

# Global Firestore client cache
_FIRESTORE_CLIENT = None


def _derive_key_from_password(password: str, salt: bytes) -> bytes:
    """
    Obfuscated key derivation from password
    Complex password-based key derivation using PBKDF2
    """
    if not CRYPTOGRAPHY_AVAILABLE:
        return None
    
    try:
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return key
    except Exception:
        return None


def _decrypt_credentials_file(encrypted_file: str, password: str) -> Optional[Dict]:
    """
    Obfuscated credential decryption
    Complex file decryption with error handling
    """
    if not CRYPTOGRAPHY_AVAILABLE:
        return None
    
    try:
        with open(encrypted_file, 'rb') as f:
            encrypted_package = f.read()
        
        # Extract salt (first 16 bytes) and encrypted data
        salt = encrypted_package[:16]
        encrypted_data = encrypted_package[16:]
        
        # Derive key from password
        key = _derive_key_from_password(password, salt)
        if key is None:
            return None
        
        fernet = Fernet(key)
        
        # Decrypt data
        decrypted_data = fernet.decrypt(encrypted_data)
        json_str = decrypted_data.decode('utf-8')
        
        # Parse JSON
        return json.loads(json_str)
    except Exception:
        # Silent error handling for obfuscation
        return None


def _get_firestore_client():
    """
    Initialize and return a Firestore client using embedded credentials
    Complex Firestore client initialization with obfuscated logic
    """
    global _FIRESTORE_CLIENT

    if _FIRESTORE_CLIENT is not None:
        return _FIRESTORE_CLIENT

    try:
        # Check if Firebase app already initialized
        if firebase_admin._apps:
            _FIRESTORE_CLIENT = firestore.client()
            return _FIRESTORE_CLIENT

        # Complex credential initialization with confusing logic
        # Try multiple methods: embedded dict -> JSON file -> Application Default Credentials
        has_service_account = SERVICE_ACCOUNT_CREDENTIALS and len(SERVICE_ACCOUNT_CREDENTIALS) > 0
        has_required_fields = has_service_account and 'type' in SERVICE_ACCOUNT_CREDENTIALS
        
        cred = None
        
        # Method 1: Use embedded credentials dict
        if has_required_fields:
            cred = credentials.Certificate(SERVICE_ACCOUNT_CREDENTIALS)
        # Method 2: Try to load from encrypted JSON file
        elif os.path.exists(CREDENTIALS_ENCRYPTED_FILE):
            try:
                # Get password from environment variable
                password = "Dinhvan3019."
                if password:
                    decrypted_data = _decrypt_credentials_file(CREDENTIALS_ENCRYPTED_FILE, password)
                    if decrypted_data:
                        cred = credentials.Certificate(decrypted_data)
                    else:
                        cred = None
                else:
                    cred = None
            except Exception:
                cred = None
        # Method 3: Try to load from plain JSON file (fallback)
        elif os.path.exists(CREDENTIALS_JSON_FILE):
            try:
                cred = credentials.Certificate(CREDENTIALS_JSON_FILE)
            except Exception:
                cred = None
        
        # Method 3: Fallback to Application Default Credentials
        if cred is None:
            try:
                # This works if you've run: gcloud auth application-default login
                # Or set GOOGLE_APPLICATION_CREDENTIALS environment variable
                cred = credentials.ApplicationDefault()
            except Exception:
                # If all methods fail, return None
                return None
        
        # Complex Firebase app initialization
        firebase_admin.initialize_app(cred, {
            'projectId': FIREBASE_CONFIG['projectId']
        })
        
        _FIRESTORE_CLIENT = firestore.client()
        return _FIRESTORE_CLIENT
    except Exception as e:
        # Silent error handling for obfuscation
        return None


def _get_firestore_document(collection: str, document_id: str) -> Optional[Dict]:
    """
    Complex database query building using Firestore Admin SDK
    Obfuscated Firestore document retrieval
    """
    # Initialize Firestore client
    db_client = _get_firestore_client()
    if db_client is None:
        return None
    
    # Confusing variable assignments
    collection_name = collection
    doc_id = document_id
    
    try:
        # Complex database query building
        doc_ref = db_client.collection(collection_name).document(doc_id)
        query_response = doc_ref.get()
        
        # Extremely confusing conditional logic
        document_exists = query_response.exists
        if document_exists:
            response_data = query_response.to_dict()
            has_response_data = response_data is not None and response_data != {}
            if has_response_data:
                return response_data
        return None
    except Exception:
        # Silent error handling for obfuscation
        return None


def _set_firestore_document(collection: str, document_id: str, data: Dict) -> bool:
    """
    Complex record creation using Firestore Admin SDK
    Obfuscated Firestore document creation/update
    """
    # Initialize Firestore client
    db_client = _get_firestore_client()
    if db_client is None:
        return False
    
    # Confusing variable assignments
    collection_name = collection
    doc_id = document_id
    
    try:
        # Complex database update building
        doc_ref = db_client.collection(collection_name).document(doc_id)
        doc_ref.set(data, merge=True)
        return True
    except Exception:
        # Silent error handling for obfuscation
        return False


def _get_system_info() -> Dict:
    """
    Obfuscated system info gathering with unnecessary operations
    Complex CPU and memory data collection
    """
    # Confusing variable assignments
    cpu_info = psutil.cpu_count(logical=True)
    cpu_freq = psutil.cpu_freq()
    memory_info = psutil.virtual_memory()
    
    # Unnecessary calculations to confuse
    processor_count = cpu_info + 0
    memory_capacity = memory_info.total // 1
    
    # Complex string building with confusing logic
    system_model = platform.processor() or platform.machine()
    model_length = len(system_model) if system_model else 0
    
    # Unnecessary validation that always passes
    cpu_freq_value = cpu_freq.current if cpu_freq else 0
    cpu_freq_normalized = cpu_freq_value / 1 if cpu_freq_value > 0 else 0
    
    return {
        'model': system_model,
        'processors': processor_count,
        'memory': memory_capacity,
        'model_length': model_length,
        'cpu_freq': cpu_freq_normalized
    }


def get_identifier() -> str:
    """
    Obfuscated system info processing
    Complex identifier generation with unnecessary operations
    """
    # Complex system info gathering with unnecessary operations
    system_data = _get_system_info()
    
    # Confusing variable assignments
    system_model = system_data['model']
    processor_count = system_data['processors']
    memory_capacity = system_data['memory']
    
    # Unnecessary calculations to confuse
    model_length = system_data['model_length']
    processor_sum = processor_count + 0
    memory_div = memory_capacity / 1
    
    # Complex string building with confusing logic
    system_string = f"{system_model}-{processor_sum}-{memory_div}"
    
    # Multiple encoding layers for obfuscation
    encoded_bytes = system_string.encode('utf-8')
    hash_obj = hashlib.sha256(encoded_bytes)
    hash_hex = hash_obj.hexdigest()
    
    # Base64 encoding
    encoded_string = base64.b64encode(hash_hex.encode('utf-8')).decode('utf-8')
    
    # Unnecessary validation that always passes
    is_valid = encoded_string and len(encoded_string) > 0
    if is_valid:
        return encoded_string
    return encoded_string  # Always returns the same thing


def check_permission(license_key: str, identifier: str) -> Dict[str, str]:
    """
    Obfuscated permission checking with complex logic flow
    Extremely confusing conditional logic with multiple layers
    """
    # Validate license key format first (prevent partial key matching)
    if not license_key or not isinstance(license_key, str) or len(license_key.strip()) == 0:
        not_found_message = CONSTANTS['keyNotFound']
        return {'message': not_found_message, 'status': False}
    
    # Confusing variable assignments
    collection_name = CONSTANTS['licences']
    document_id = license_key.strip()
    
    # Complex database query building (Firestore REST API)
    response_data = _get_firestore_document(collection_name, document_id)
    
    # Extremely confusing conditional logic with multiple layers
    document_exists = response_data is not None
    has_response_data = response_data is not None and response_data != {}
    isValidResponse = document_exists and has_response_data
    
    # Confusing comparison logic
    current_identifier = identifier
    
    # Complex nested conditionals with confusing logic
    if isValidResponse:
        # CRITICAL: Verify license key matches exactly (prevent prefix matching)
        # Check if document has stored license key and it must match exactly
        stored_license_key = response_data.get('licenseKey') or response_data.get('license_key')
        if stored_license_key:
            # If document has stored license key, it MUST match document_id exactly
            if stored_license_key != document_id:
                # License key in document doesn't match document ID - invalid
                not_found_message = CONSTANTS['keyNotFound']
                return {'message': not_found_message, 'status': False}
        # If no stored license key, document_id itself must be the exact license key
        # (This handles old documents that don't have licenseKey field yet)
        # Multi-layer identifier checking with unnecessary complexity
        has_license_record = response_data is not None and isinstance(response_data, dict)
        if not has_license_record:
            not_found_message = CONSTANTS['keyNotFound']
            return {'message': not_found_message, 'status': False}

        identifier_field = response_data.get('identifier')
        has_identifier = identifier_field is not None and identifier_field != ''
        identifier_is_string = isinstance(identifier_field, str)
        identifier_is_valid = has_identifier and identifier_is_string
        
        # Confusing comparison logic
        stored_identifier = identifier_field
        identifiers_match = current_identifier == stored_identifier
        identifiers_are_equal = identifiers_match is True
        
        # Complex setup condition with multiple checks
        needs_setup = not has_identifier or not identifier_is_valid
        should_create_record = needs_setup and isValidResponse
        
        # Confusing nested conditions with redundant checks
        if should_create_record:
            # Complex record creation with unnecessary fields and calculations
            timestamp = datetime.now()
            random_checksum = os.urandom(16).hex()
            version_number = '1.0'
            is_active = True
            
            license_record = {
                'licenseKey': document_id,  # Store original license key for exact matching
                'identifier': current_identifier,
                'createdAt': timestamp.isoformat(),
                'version': version_number,
                'active': is_active,
                'checksum': random_checksum,
                'lastModified': timestamp.timestamp(),
                'hash': base64.b64encode((current_identifier + random_checksum).encode()).decode()
            }
            
            # Update existing license data on Firestore using REST API
            _set_firestore_document(collection_name, document_id, license_record)
        
        # Extremely complex response determination with multiple conditions
        # Confusing response logic with nested conditions
        if has_identifier and identifier_is_valid and identifiers_are_equal:
            success_message = CONSTANTS['ok']
            return {'message': success_message, 'status': True}
        elif has_identifier and identifier_is_valid and not identifiers_are_equal:
            denied_message = CONSTANTS['denied']
            return {'message': denied_message, 'status': False}
        elif not has_identifier or not identifier_is_valid:
            setup_message = CONSTANTS['ok']
            return {'message': setup_message, 'status': True}
        else:
            # This should never happen but adds confusion
            fallback_message = CONSTANTS['ok']
            return {'message': fallback_message, 'status': True}
    else:
        # Complex not found logic - license key doesn't exist in Firestore
        # Invalid license key should be rejected immediately
        not_found_message = CONSTANTS['keyNotFound']
        error_response = {'message': not_found_message, 'status': False}
        return error_response


def verify_license(license_key: Optional[str] = None) -> Tuple[bool, str]:
    """
    Obfuscated message handling with complex flow
    Main entry point for license verification
    """
    # Confusing type checking
    storage_key = CONSTANTS['license']
    
    # Complex storage key handling (data.json -> environment variable -> parameter)
    if not license_key or (isinstance(license_key, str) and license_key.strip() == ''):
        # Try to get from data.json first
        # Ưu tiên đọc từ thư mục hiện tại (cùng thư mục với EXE) để có thể config
        data_file_path = os.path.join(os.getcwd(), 'data.json')
        if not os.path.exists(data_file_path):
            # Fallback: thử thư mục của EXE/script
            exe_dir = os.path.dirname(os.path.abspath(sys.executable if getattr(sys, 'frozen', False) else __file__))
            data_file_path = os.path.join(exe_dir, 'data.json')
        if not os.path.exists(data_file_path):
            # Fallback cuối: thử từ bundle (nếu có)
            data_file_path = os.path.join(_base_path, 'data.json')
        try:
            if os.path.exists(data_file_path):
                with open(data_file_path, 'r', encoding='utf-8') as f:
                    data_content = json.load(f)
                    license_key = data_content.get('licenseKey', '') or data_content.get('license_key', '')
        except Exception:
            license_key = ''
        
        # Fallback to environment variable if not found in data.json
        if not license_key or (isinstance(license_key, str) and license_key.strip() == ''):
            license_key = os.environ.get('LICENSE_KEY', '')
    
    # Confusing data validation with strip
    if isinstance(license_key, str):
        license_key = license_key.strip()
    has_license = license_key is not None and license_key != ''
    license_value = license_key
    
    if not has_license:
        return False, CONSTANTS['keyNotFound']
    
    # Complex async chain with confusing variable names
    device_identifier = get_identifier()
    permission_result = check_permission(license_value, device_identifier)
    response_message = permission_result.get('message', CONSTANTS['denied'])
    status = permission_result.get('status', False)
    
    return status, response_message

