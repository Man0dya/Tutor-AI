import re
import html
import hashlib
import secrets
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

class SecurityManager:
    """
    Security utilities for the tutoring system
    Handles input sanitization, validation, and basic security measures
    """
    
    def __init__(self):
        self.rate_limit_store = {}
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
        
        self.max_input_length = 10000  # Maximum input length
        self.rate_limit_requests = 100  # Max requests per hour
        self.rate_limit_window = 3600  # 1 hour in seconds
    
    def sanitize_input(self, text: str) -> str:
        """
        Sanitize user input to prevent XSS and injection attacks
        
        Args:
            text (str): Input text to sanitize
            
        Returns:
            str: Sanitized text
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
        Validate input according to type
        
        Args:
            text (str): Input to validate
            input_type (str): Type of input (text, email, username, etc.)
            
        Returns:
            dict: Validation results
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
        Check if user has exceeded rate limits
        
        Args:
            user_id (str): User identifier
            endpoint (str): Endpoint being accessed
            
        Returns:
            dict: Rate limit status
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
        """Generate a secure session token"""
        timestamp = str(int(time.time()))
        random_bytes = secrets.token_bytes(16)
        
        # Create token with user_id, timestamp, and random bytes
        token_data = f"{user_id}:{timestamp}:{random_bytes.hex()}"
        
        # Hash the token
        token_hash = hashlib.sha256(token_data.encode()).hexdigest()
        
        return token_hash
    
    def validate_session_token(self, token: str, user_id: str, max_age_hours: int = 24) -> bool:
        """Validate a session token (simplified implementation)"""
        # In a real implementation, you would store and validate tokens properly
        # This is a simplified version for demonstration
        
        if not token or len(token) != 64:  # SHA256 hex length
            return False
        
        # Basic format validation
        if not re.match(r'^[a-f0-9]{64}$', token):
            return False
        
        return True
    
    def encrypt_sensitive_data(self, data: str, key: Optional[str] = None) -> str:
        """Simple encryption for sensitive data (placeholder implementation)"""
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
        """Log security events for monitoring"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'event_type': event_type,
            'user_id': user_id,
            'details': details,
            'ip_address': 'unknown'  # In production, get from request
        }
        
        # In production, write to proper logging system
        print(f"SECURITY LOG: {log_entry}")
    
    def check_content_safety(self, content: str) -> Dict[str, Any]:
        """Check if content is safe for educational use"""
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
        
        # Check for personal information patterns
        personal_info_patterns = [
            r'\b\d{3}-\d{2}-\d{4}\b',  # SSN
            r'\b\d{16}\b',             # Credit card
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'  # Email
        ]
        
        for pattern in personal_info_patterns:
            if re.search(pattern, content):
                safety_result['issues'].append('Content may contain personal information')
        
        return safety_result
    
    def sanitize_filename(self, filename: str) -> str:
        """Sanitize filename for safe file operations"""
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
        """Generate CSRF token for form protection"""
        return secrets.token_urlsafe(32)
    
    def validate_csrf_token(self, token: str, stored_token: str) -> bool:
        """Validate CSRF token"""
        if not token or not stored_token:
            return False
        
        return secrets.compare_digest(token, stored_token)
