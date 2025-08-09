#!/usr/bin/env python3
"""
Basic security tests for the CRY-A-4MCP platform.

This module contains fundamental security tests including:
- Input validation
- Authentication checks
- Authorization verification
- Data sanitization
- SQL injection prevention
- XSS protection
"""

import pytest
import re
from typing import Any, Dict, List


class TestInputValidation:
    """Test input validation and sanitization."""
    
    @pytest.mark.security
    def test_sql_injection_prevention(self):
        """Test that SQL injection attempts are properly handled."""
        malicious_inputs = [
            "'; DROP TABLE users; --",
            "1' OR '1'='1",
            "admin'--",
            "' UNION SELECT * FROM users--",
            "1; DELETE FROM users WHERE 1=1--"
        ]
        
        for malicious_input in malicious_inputs:
            # Test that malicious SQL is detected
            assert self._contains_sql_injection_pattern(malicious_input)
    
    @pytest.mark.security
    def test_xss_prevention(self):
        """Test that XSS attempts are properly handled."""
        xss_payloads = [
            "<script>alert('XSS')</script>",
            "javascript:alert('XSS')",
            "<img src=x onerror=alert('XSS')>",
            "<svg onload=alert('XSS')>",
            "'><script>alert('XSS')</script>"
        ]
        
        for payload in xss_payloads:
            # Test that XSS patterns are detected
            assert self._contains_xss_pattern(payload)
    
    @pytest.mark.security
    def test_path_traversal_prevention(self):
        """Test that path traversal attempts are blocked."""
        path_traversal_attempts = [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32\\config\\sam",
            "%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd",
            "....//....//....//etc/passwd",
            "..%252f..%252f..%252fetc%252fpasswd"
        ]
        
        for attempt in path_traversal_attempts:
            # Test that path traversal patterns are detected
            assert self._contains_path_traversal_pattern(attempt)
    
    def _contains_sql_injection_pattern(self, input_str: str) -> bool:
        """Check if input contains SQL injection patterns."""
        sql_patterns = [
            r"('|(\-\-)|(;)|(\||\|)|(\*|\*))",
            r"(union|select|insert|delete|update|drop|create|alter|exec|execute)",
            r"(script|javascript|vbscript|onload|onerror|onclick)"
        ]
        
        for pattern in sql_patterns:
            if re.search(pattern, input_str.lower()):
                return True
        return False
    
    def _contains_xss_pattern(self, input_str: str) -> bool:
        """Check if input contains XSS patterns."""
        xss_patterns = [
            r"<script[^>]*>.*?</script>",
            r"javascript:",
            r"on\w+\s*=",
            r"<\s*img[^>]+onerror",
            r"<\s*svg[^>]+onload"
        ]
        
        for pattern in xss_patterns:
            if re.search(pattern, input_str.lower()):
                return True
        return False
    
    def _contains_path_traversal_pattern(self, input_str: str) -> bool:
        """Check if input contains path traversal patterns."""
        path_patterns = [
            r"\.\./",
            r"\.\.\\",
            r"%2e%2e%2f",
            r"%2e%2e%5c",
            r"\.\.%2f"
        ]
        
        for pattern in path_patterns:
            if re.search(pattern, input_str.lower()):
                return True
        return False


class TestAuthentication:
    """Test authentication mechanisms."""
    
    @pytest.mark.security
    def test_password_strength_requirements(self):
        """Test password strength validation."""
        weak_passwords = [
            "123456",
            "password",
            "admin",
            "qwerty",
            "abc123"
        ]
        
        strong_passwords = [
            "MyStr0ng!P@ssw0rd",
            "C0mpl3x#P@ssw0rd123",
            "S3cur3!P@ssw0rd#2024"
        ]
        
        for weak_pwd in weak_passwords:
            assert not self._is_strong_password(weak_pwd)
        
        for strong_pwd in strong_passwords:
            assert self._is_strong_password(strong_pwd)
    
    @pytest.mark.security
    def test_session_token_format(self):
        """Test that session tokens meet security requirements."""
        # Mock session token (in real implementation, this would come from auth system)
        mock_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"
        
        # Test token format
        assert len(mock_token) >= 32  # Minimum length
        assert not mock_token.isdigit()  # Not just numbers
        assert not mock_token.isalpha()  # Not just letters
    
    def _is_strong_password(self, password: str) -> bool:
        """Check if password meets strength requirements."""
        if len(password) < 8:
            return False
        
        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)
        has_digit = any(c.isdigit() for c in password)
        has_special = any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password)
        
        return has_upper and has_lower and has_digit and has_special


class TestDataSanitization:
    """Test data sanitization and validation."""
    
    @pytest.mark.security
    def test_email_validation(self):
        """Test email address validation."""
        valid_emails = [
            "user@example.com",
            "test.email@domain.co.uk",
            "user+tag@example.org"
        ]
        
        invalid_emails = [
            "invalid-email",
            "@domain.com",
            "user@",
            "user..double.dot@example.com",
            "user@domain"
        ]
        
        for email in valid_emails:
            assert self._is_valid_email(email)
        
        for email in invalid_emails:
            assert not self._is_valid_email(email)
    
    @pytest.mark.security
    def test_url_validation(self):
        """Test URL validation and sanitization."""
        valid_urls = [
            "https://example.com",
            "http://subdomain.example.org/path",
            "https://example.com:8080/api/v1"
        ]
        
        invalid_urls = [
            "javascript:alert('xss')",
            "data:text/html,<script>alert('xss')</script>",
            "ftp://malicious.com",
            "file:///etc/passwd"
        ]
        
        for url in valid_urls:
            assert self._is_safe_url(url)
        
        for url in invalid_urls:
            assert not self._is_safe_url(url)
    
    def _is_valid_email(self, email: str) -> bool:
        """Validate email address format."""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    def _is_safe_url(self, url: str) -> bool:
        """Check if URL is safe (no malicious schemes)."""
        safe_schemes = ['http', 'https']
        if '://' not in url:
            return False
        
        scheme = url.split('://')[0].lower()
        return scheme in safe_schemes


class TestSecurityHeaders:
    """Test security headers and configurations."""
    
    @pytest.mark.security
    def test_required_security_headers(self):
        """Test that required security headers are present."""
        required_headers = [
            'X-Content-Type-Options',
            'X-Frame-Options',
            'X-XSS-Protection',
            'Strict-Transport-Security',
            'Content-Security-Policy'
        ]
        
        # Mock response headers (in real implementation, test actual HTTP responses)
        mock_headers = {
            'X-Content-Type-Options': 'nosniff',
            'X-Frame-Options': 'DENY',
            'X-XSS-Protection': '1; mode=block',
            'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
            'Content-Security-Policy': "default-src 'self'"
        }
        
        for header in required_headers:
            assert header in mock_headers
            assert mock_headers[header]  # Header has a value
    
    @pytest.mark.security
    def test_csp_policy_strength(self):
        """Test Content Security Policy strength."""
        # Mock CSP policy
        csp_policy = "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'"
        
        # Test that CSP doesn't allow unsafe practices
        assert "'unsafe-eval'" not in csp_policy
        assert "*" not in csp_policy  # No wildcard sources
        assert "'self'" in csp_policy  # Restricts to same origin


if __name__ == "__main__":
    pytest.main([__file__, "-v"])