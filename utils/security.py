"""
Security Utilities Module

This module provides comprehensive security utilities for the Tutor AI system, including
input sanitization, validation, rate limiting, session management, and content safety checks.
It implements multiple layers of security to protect against common web application vulnerabilities.

Key Features:
- Input sanitization and validation against XSS and injection attacks
- Rate limiting to prevent abuse and DoS attacks
- Session token generation and validation
- Content safety analysis for educational appropriateness
- Filename sanitization for secure file operations
- CSRF protection token management

Security Layers:
1. Input Sanitization: HTML escaping, pattern blocking, length limits
2. Input Validation: Type-specific validation (email, username, topic)
3. Rate Limiting: Request throttling with configurable limits
4. Content Safety: Pattern-based inappropriate content detection
5. Session Security: Secure token generation and validation
6. File Security: Safe filename handling and path traversal prevention

Attack Mitigations:
- XSS: HTML escaping and script pattern blocking
- SQL Injection: Pattern detection and blocking
- Command Injection: Dangerous command pattern filtering
- DoS: Rate limiting and input length restrictions
- CSRF: Token-based form protection
- Path Traversal: Filename sanitization

Configuration:
- max_input_length: Maximum allowed input length (default: 10,000 chars)
- rate_limit_requests: Max requests per hour (default: 100)
- rate_limit_window: Rate limit time window in seconds (default: 3,600)

Dependencies:
- re: Regular expression pattern matching
- html: HTML entity escaping
- hashlib: Cryptographic hashing for tokens
- secrets: Cryptographically secure random number generation
- time: Time-based operations for rate limiting
- datetime: Timestamp handling
- typing: Type hints for better code documentation
"""

import re
import html
import hashlib
import secrets
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

class SecurityManager:
    """
    Security utilities for the tutoring system
    Handles input sanitization, validation, and basic security measures

    This class provides a comprehensive security toolkit for the Tutor AI application,
    implementing multiple security layers to protect against common web vulnerabilities.
    It includes input sanitization, rate limiting, session management, and content safety
    analysis specifically tailored for educational content and user interactions.
    """

    def __init__(self):
        """Initialize the SecurityManager with default security configurations."""
        self.rate_limit_store = {}

        # Define patterns for blocking potentially malicious input
        self.blocked_patterns = [
            # Common injection patterns
            r'<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>',
            r'javascript:',
            r'onload\s*=',
            r'onerror\s*=',
            r'onclick\s*=',
            r'eval\s*\(',
            r'expression\s*\(',
            # SQL injection patterns
            r'union\s+select',
            r'drop\s+table',
            r'delete\s+from',
            r'insert\s+into',
            r'update\s+set',
            # Command injection
            r';\s*rm\s+',
            r';\s*cat\s+',
            r';\s*ls\s+',
            r'&&\s*rm\s+',
        ]

        # Security configuration parameters
        self.max_input_length = 10000  # Maximum input length
        self.rate_limit_requests = 100  # Max requests per hour
        self.rate_limit_window = 3600  # 1 hour in seconds

        # Compile basic PII detection patterns
        # Note: Keep patterns conservative to avoid excessive false positives
        self._pii_patterns: Dict[str, re.Pattern] = {
            # Emails
            "email": re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"),
            # Simple international phone formats (e.g., +1 555-123-4567, 071-234-5678)
            "phone": re.compile(r"\b(?:\+?\d{1,3}[-.\s]?)?(?:\(\d{2,4}\)[-.\s]?|\d{2,4}[-.\s]?)?\d{3,4}[-.\s]?\d{3,4}\b"),
            # US SSN
            "ssn": re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
            # IBAN (very rough)
            "iban": re.compile(r"\b[A-Z]{2}\d{2}[A-Z0-9]{11,30}\b"),
        }

    # ---------------------------
    # PII detection and redaction
    # ---------------------------
    def _luhn_check(self, number: str) -> bool:
        """Validate a number using the Luhn algorithm (for credit cards)."""
        try:
            digits = [int(d) for d in number if d.isdigit()]
        except ValueError:
            return False
        if len(digits) < 13 or len(digits) > 19:
            return False
        checksum = 0
        parity = (len(digits) - 2) % 2
        for i, d in enumerate(digits[:-1]):
            if i % 2 == parity:
                d = d * 2
                if d > 9:
                    d -= 9
            checksum += d
        return (checksum + digits[-1]) % 10 == 0

    def detect_pii(self, text: str) -> Dict[str, List[str]]:
        """
        Detect potential PII elements in text.

        Returns a dict mapping PII type -> list of matched strings.
        Types: email, phone, ssn, credit_card, iban
        """
        if not isinstance(text, str) or not text:
            return {}
        found: Dict[str, List[str]] = {k: [] for k in ["email", "phone", "ssn", "credit_card", "iban"]}

        # Regex-based detection
        for t, pattern in self._pii_patterns.items():
            matches = pattern.findall(text)
            if matches:
                found[t].extend(matches if isinstance(matches, list) else [matches])

        # Credit card detection using Luhn on 13-19 digit sequences
        for m in re.findall(r"\b(?:\d[ -]?){13,19}\b", text):
            digits_only = re.sub(r"[^\d]", "", m)
            if self._luhn_check(digits_only):
                found["credit_card"].append(m)

        # Remove empty entries
        return {k: v for k, v in found.items() if v}

    def redact_pii(self, text: str) -> str:
        """
        Redact detected PII from text, replacing with type-specific masks.
        - email -> [REDACTED:EMAIL]
        - phone -> [REDACTED:PHONE]
        - ssn -> ***-**-****
        - credit card -> **** **** **** 1234 (keep last 4)
        - iban -> [REDACTED:IBAN]
        """
        if not isinstance(text, str) or not text:
            return text

        # Emails
        text = self._pii_patterns["email"].sub("[REDACTED:EMAIL]", text)
        # Phones
        text = self._pii_patterns["phone"].sub("[REDACTED:PHONE]", text)
        # SSN
        text = self._pii_patterns["ssn"].sub("***-**-****", text)
        # IBAN
        text = self._pii_patterns["iban"].sub("[REDACTED:IBAN]", text)
        # Credit cards (mask keep last 4)
        def _mask_card(m: re.Match) -> str:
            raw = m.group(0)
            digits = re.sub(r"[^\d]", "", raw)
            if not self._luhn_check(digits):
                return raw
            last4 = digits[-4:]
            return "**** **** **** " + last4
        text = re.sub(r"\b(?:\d[ -]?){13,19}\b", _mask_card, text)

        return text

    def redact_pii_in_obj(self, obj: Any) -> Any:
        """Recursively redact PII in strings within dicts/lists/tuples."""
        if isinstance(obj, str):
            return self.redact_pii(obj)
        if isinstance(obj, list):
            return [self.redact_pii_in_obj(x) for x in obj]
        if isinstance(obj, tuple):
            return tuple(self.redact_pii_in_obj(x) for x in obj)
        if isinstance(obj, dict):
            return {k: self.redact_pii_in_obj(v) for k, v in obj.items()}
        return obj
    
    def sanitize_input(self, text: str) -> str:
        """
        Sanitize user input to prevent XSS and injection attacks

        This method applies multiple sanitization techniques:
        1. Length validation and truncation
        2. HTML entity escaping
        3. Malicious pattern removal
        4. Whitespace normalization
        5. Control character removal

        Args:
            text (str): Input text to sanitize

        Returns:
            str: Sanitized text safe for processing and display
        """
        if not isinstance(text, str):
            return str(text)
        
        # Length check
        if len(text) > self.max_input_length:
            text = text[:self.max_input_length]
        
        # HTML escape
        text = html.escape(text)
        
        # Remove dangerous patterns
        for pattern in self.blocked_patterns:
            text = re.sub(pattern, '', text, flags=re.IGNORECASE)
        
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Remove null bytes and control characters
        text = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', text)
        
        return text
    
    def validate_input(self, text: str, input_type: str = 'text') -> Dict[str, bool]:
        """
        Validate input according to type and security requirements

        Performs comprehensive validation including:
        - Empty input checking
        - Length validation
        - Malicious pattern detection
        - Type-specific format validation

        Args:
            text (str): Input to validate
            input_type (str): Type of input ('text', 'email', 'username', 'topic')

        Returns:
            dict: Validation results with 'is_valid' boolean and 'errors' list
        """
        validation_result = {
            'is_valid': True,
            'errors': []
        }
        
        if not text:
            validation_result['is_valid'] = False
            validation_result['errors'].append('Input cannot be empty')
            return validation_result
        
        # Length validation
        if len(text) > self.max_input_length:
            validation_result['is_valid'] = False
            validation_result['errors'].append(f'Input too long (max {self.max_input_length} characters)')
        
        # Check for malicious patterns
        for pattern in self.blocked_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                validation_result['is_valid'] = False
                validation_result['errors'].append('Input contains potentially malicious content')
                break
        
        # Type-specific validation
        if input_type == 'email':
            if not self._validate_email(text):
                validation_result['is_valid'] = False
                validation_result['errors'].append('Invalid email format')
        
        elif input_type == 'username':
            if not self._validate_username(text):
                validation_result['is_valid'] = False
                validation_result['errors'].append('Invalid username format')
        
        elif input_type == 'topic':
            if not self._validate_topic(text):
                validation_result['is_valid'] = False
                validation_result['errors'].append('Invalid topic format')
        
        return validation_result
    
    def _validate_email(self, email: str) -> bool:
        """Validate email format"""
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(email_pattern, email) is not None
    
    def _validate_username(self, username: str) -> bool:
        """Validate username format"""
        # Allow alphanumeric characters, underscores, and hyphens
        username_pattern = r'^[a-zA-Z0-9_-]{3,20}$'
        return re.match(username_pattern, username) is not None
    
    def _validate_topic(self, topic: str) -> bool:
        """Validate topic format"""
        # Allow letters, numbers, spaces, and common punctuation
        topic_pattern = r'^[a-zA-Z0-9\s\-_.,;:()]+$'
        return re.match(topic_pattern, topic) is not None and len(topic.strip()) >= 2
    
    def check_rate_limit(self, user_id: str, endpoint: str = 'default') -> Dict[str, Any]:
        """
        Check if user has exceeded rate limits for the specified endpoint

        Implements sliding window rate limiting to prevent abuse:
        - Tracks requests per user per endpoint
        - Blocks users exceeding limits for the configured window
        - Automatically cleans old requests outside the window

        Args:
            user_id (str): User identifier for rate limiting
            endpoint (str): Endpoint being accessed (default: 'default')

        Returns:
            dict: Rate limit status with 'allowed', 'reason', and timing information
        """
        current_time = time.time()
        key = f"{user_id}:{endpoint}"
        
        if key not in self.rate_limit_store:
            self.rate_limit_store[key] = {
                'requests': [],
                'blocked_until': None
            }
        
        user_data = self.rate_limit_store[key]
        
        # Check if user is currently blocked
        if user_data['blocked_until'] and current_time < user_data['blocked_until']:
            return {
                'allowed': False,
                'reason': 'Rate limit exceeded',
                'retry_after': int(user_data['blocked_until'] - current_time)
            }
        
        # Clean old requests outside the window
        window_start = current_time - self.rate_limit_window
        user_data['requests'] = [req_time for req_time in user_data['requests'] if req_time > window_start]
        
        # Check request count
        if len(user_data['requests']) >= self.rate_limit_requests:
            # Block user for 1 hour
            user_data['blocked_until'] = current_time + self.rate_limit_window
            return {
                'allowed': False,
                'reason': 'Rate limit exceeded',
                'retry_after': self.rate_limit_window
            }
        
        # Add current request
        user_data['requests'].append(current_time)
        
        return {
            'allowed': True,
            'requests_remaining': self.rate_limit_requests - len(user_data['requests'])
        }
    
    def generate_session_token(self, user_id: str) -> str:
        """
        Generate a secure session token for user authentication

        Creates cryptographically secure session tokens using:
        - User ID for identification
        - Timestamp for expiration tracking
        - Random bytes for uniqueness
        - SHA256 hashing for security

        Args:
            user_id (str): User identifier for token association

        Returns:
            str: Secure session token hash
        """
        timestamp = str(int(time.time()))
        random_bytes = secrets.token_bytes(16)
        
        # Create token with user_id, timestamp, and random bytes
        token_data = f"{user_id}:{timestamp}:{random_bytes.hex()}"
        
        # Hash the token
        token_hash = hashlib.sha256(token_data.encode()).hexdigest()
        
        return token_hash
    
    def validate_session_token(self, token: str, user_id: str, max_age_hours: int = 24) -> bool:
        """
        Validate a session token (simplified implementation)

        Note: This is a simplified version for demonstration.
        In production, implement proper token storage and validation
        with database-backed session management.

        Args:
            token (str): Session token to validate
            user_id (str): Associated user ID
            max_age_hours (int): Maximum token age in hours

        Returns:
            bool: True if token is valid, False otherwise
        """
        # In a real implementation, you would store and validate tokens properly
        # This is a simplified version for demonstration
        
        if not token or len(token) != 64:  # SHA256 hex length
            return False
        
        # Basic format validation
        if not re.match(r'^[a-f0-9]{64}$', token):
            return False
        
        return True
    
    def encrypt_sensitive_data(self, data: str, key: Optional[str] = None) -> str:
        """
        Simple encryption for sensitive data (placeholder implementation)

        WARNING: This is a simplified example for demonstration only.
        In production, use proper encryption libraries like the 'cryptography' package
        with proper key management, IVs, and authenticated encryption.

        Args:
            data (str): Data to encrypt
            key (Optional[str]): Encryption key (uses default if None)

        Returns:
            str: Base64-encoded encrypted data
        """
        # In production, use proper encryption libraries like cryptography
        # This is a simplified example
        
        if not key:
            key = "default_encryption_key"  # In production, use proper key management
        
        # Simple XOR encryption (NOT for production use)
        encrypted = ""
        for i, char in enumerate(data):
            key_char = key[i % len(key)]
            encrypted += chr(ord(char) ^ ord(key_char))
        
        # Base64-like encoding for safe storage
        import base64
        return base64.b64encode(encrypted.encode('latin1')).decode()
    
    def decrypt_sensitive_data(self, encrypted_data: str, key: Optional[str] = None) -> str:
        """Decrypt sensitive data"""
        if not key:
            key = "default_encryption_key"
        
        try:
            import base64
            decoded = base64.b64decode(encrypted_data).decode('latin1')
            
            decrypted = ""
            for i, char in enumerate(decoded):
                key_char = key[i % len(key)]
                decrypted += chr(ord(char) ^ ord(key_char))
            
            return decrypted
        except:
            return ""
    
    def log_security_event(self, event_type: str, user_id: str, details: str):
        """
        Log security events for monitoring and auditing

        Records security-related events for analysis and compliance.
        In production, integrate with proper logging systems and SIEM tools.

        Args:
            event_type (str): Type of security event (e.g., 'rate_limit_exceeded')
            user_id (str): User associated with the event
            details (str): Detailed description of the event
        """
        safe_details = self.redact_pii(details) if isinstance(details, str) else details
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'event_type': event_type,
            'user_id': user_id,
            'details': safe_details,
            'ip_address': 'unknown'  # In production, get from request
        }
        
        # In production, write to proper logging system
        print(f"SECURITY LOG: {log_entry}")
    
    def check_content_safety(self, content: str) -> Dict[str, Any]:
        """
        Check if content is safe for educational use

        Analyzes content for inappropriate material and personal information
        that should not be present in educational contexts.

        Args:
            content (str): Content to analyze for safety

        Returns:
            dict: Safety analysis with 'is_safe' boolean and 'issues' list
        """
        safety_result = {
            'is_safe': True,
            'issues': []
        }
        
        # Check for inappropriate content patterns
        inappropriate_patterns = [
            r'\b(hate|violence|explicit)\b',
            r'\b(drugs|alcohol|gambling)\b',
            r'\b(suicide|self-harm)\b'
        ]
        
        content_lower = content.lower()
        
        for pattern in inappropriate_patterns:
            if re.search(pattern, content_lower):
                safety_result['is_safe'] = False
                safety_result['issues'].append(f'Content may contain inappropriate material')
                break
        
        # Check for personal information using PII detector
        pii_found = self.detect_pii(content)
        if pii_found:
            safety_result['issues'].append('Content may contain personal information')
        
        return safety_result
    
    def sanitize_filename(self, filename: str) -> str:
        """
        Sanitize filename for safe file operations

        Removes dangerous characters and patterns to prevent:
        - Directory traversal attacks
        - Command injection through filenames
        - Filesystem corruption

        Args:
            filename (str): Filename to sanitize

        Returns:
            str: Safe filename for file operations
        """
        # Remove directory traversal attempts
        filename = filename.replace('..', '').replace('/', '').replace('\\', '')
        
        # Keep only safe characters
        filename = re.sub(r'[^a-zA-Z0-9._-]', '', filename)
        
        # Limit length
        if len(filename) > 100:
            name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
            filename = name[:95] + ('.' + ext if ext else '')
        
        return filename or 'default_filename'
    
    def generate_csrf_token(self) -> str:
        """
        Generate CSRF token for form protection

        Creates cryptographically secure tokens to prevent
        Cross-Site Request Forgery attacks.

        Returns:
            str: URL-safe CSRF token
        """
        return secrets.token_urlsafe(32)
    
    def validate_csrf_token(self, token: str, stored_token: str) -> bool:
        """
        Validate CSRF token against stored token

        Uses constant-time comparison to prevent timing attacks.

        Args:
            token (str): Token from request
            stored_token (str): Expected token from session

        Returns:
            bool: True if tokens match, False otherwise
        """
        if not token or not stored_token:
            return False
        
        return secrets.compare_digest(token, stored_token)
