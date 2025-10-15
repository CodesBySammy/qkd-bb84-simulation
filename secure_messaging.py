"""
Secure Messaging using Quantum Keys
Provides encryption/decryption using AES-256 with quantum-generated keys
"""

import hashlib
import os
from typing import Dict, Optional
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes

class SecureMessaging:
    """
    Provides secure messaging using AES-256 encryption
    Uses quantum-generated keys for enhanced security
    """
    
    def __init__(self):
        self.encryption_history = []
    
    def encrypt_message(self, message: str, quantum_key: str) -> Dict:
        """
        Encrypt a message using AES-256 with quantum key
        
        Args:
            message: Plaintext message to encrypt
            quantum_key: Binary string from BB84 protocol
            
        Returns:
            Dictionary containing ciphertext, nonce, and MAC
        """
        # Convert quantum key to proper encryption key
        encryption_key = self._quantum_key_to_aes_key(quantum_key)
        
        # Generate random nonce
        nonce = get_random_bytes(16)
        
        # Create cipher
        cipher = AES.new(encryption_key, AES.MODE_GCM, nonce=nonce)
        
        # Encrypt the message
        message_bytes = message.encode('utf-8')
        ciphertext, mac = cipher.encrypt_and_digest(message_bytes)
        
        # Store encryption record
        encryption_record = {
            'message_length': len(message),
            'ciphertext_length': len(ciphertext),
            'timestamp': self._get_timestamp()
        }
        self.encryption_history.append(encryption_record)
        
        return {
            'ciphertext': ciphertext,
            'nonce': nonce,
            'mac': mac
        }
    
    def decrypt_message(self, encrypted_data: Dict, quantum_key: str) -> Optional[str]:
        """
        Decrypt a message using AES-256 with quantum key
        
        Args:
            encrypted_data: Dictionary with ciphertext, nonce, and MAC
            quantum_key: Binary string from BB84 protocol
            
        Returns:
            Decrypted message or None if authentication fails
        """
        try:
            # Convert quantum key to proper encryption key
            encryption_key = self._quantum_key_to_aes_key(quantum_key)
            
            # Extract components
            ciphertext = encrypted_data['ciphertext']
            nonce = encrypted_data['nonce']
            mac = encrypted_data['mac']
            
            # Create cipher for decryption
            cipher = AES.new(encryption_key, AES.MODE_GCM, nonce=nonce)
            
            # Decrypt and verify
            plaintext_bytes = cipher.decrypt_and_verify(ciphertext, mac)
            
            # Convert back to string
            return plaintext_bytes.decode('utf-8')
            
        except (ValueError, KeyError) as e:
            print(f"❌ Decryption failed: {e}")
            return None
    
    def _quantum_key_to_aes_key(self, quantum_key: str) -> bytes:
        """
        Convert quantum key binary string to AES-256 key
        
        Args:
            quantum_key: Binary string (e.g., "101010...")
            
        Returns:
            32-byte AES key
        """
        if not quantum_key:
            raise ValueError("Quantum key cannot be empty")
        
        # Ensure we have enough bits for SHA-256 (at least 256 bits)
        if len(quantum_key) < 256:
            # Pad with repetition if needed (in real implementation, use proper KDF)
            repeated_key = (quantum_key * (256 // len(quantum_key) + 1))[:256]
            quantum_key = repeated_key
        
        # Convert binary string to bytes
        key_bytes = self._binary_string_to_bytes(quantum_key[:256])
        
        # Use SHA-256 to get proper 32-byte key
        aes_key = hashlib.sha256(key_bytes).digest()
        
        return aes_key
    
    def _binary_string_to_bytes(self, binary_string: str) -> bytes:
        """Convert binary string to bytes"""
        # Pad to multiple of 8
        padded = binary_string.ljust((len(binary_string) + 7) // 8 * 8, '0')
        
        # Convert to bytes
        byte_array = bytearray()
        for i in range(0, len(padded), 8):
            byte = padded[i:i+8]
            byte_array.append(int(byte, 2))
        
        return bytes(byte_array)
    
    def encrypt_file(self, file_path: str, quantum_key: str, output_path: str) -> bool:
        """
        Encrypt a file using quantum key
        
        Returns:
            Success flag
        """
        try:
            with open(file_path, 'rb') as f:
                file_data = f.read()
            
            # Convert quantum key
            encryption_key = self._quantum_key_to_aes_key(quantum_key)
            nonce = get_random_bytes(16)
            
            # Encrypt
            cipher = AES.new(encryption_key, AES.MODE_GCM, nonce=nonce)
            ciphertext, mac = cipher.encrypt_and_digest(file_data)
            
            # Write encrypted file
            with open(output_path, 'wb') as f:
                f.write(nonce)
                f.write(mac)
                f.write(ciphertext)
            
            print(f"✅ File encrypted successfully: {output_path}")
            return True
            
        except Exception as e:
            print(f"❌ File encryption failed: {e}")
            return False
    
    def decrypt_file(self, encrypted_file_path: str, quantum_key: str, output_path: str) -> bool:
        """
        Decrypt a file using quantum key
        
        Returns:
            Success flag
        """
        try:
            with open(encrypted_file_path, 'rb') as f:
                nonce = f.read(16)
                mac = f.read(16)
                ciphertext = f.read()
            
            # Convert quantum key
            encryption_key = self._quantum_key_to_aes_key(quantum_key)
            
            # Decrypt
            cipher = AES.new(encryption_key, AES.MODE_GCM, nonce=nonce)
            plaintext = cipher.decrypt_and_verify(ciphertext, mac)
            
            # Write decrypted file
            with open(output_path, 'wb') as f:
                f.write(plaintext)
            
            print(f"✅ File decrypted successfully: {output_path}")
            return True
            
        except Exception as e:
            print(f"❌ File decryption failed: {e}")
            return False
    
    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def get_encryption_stats(self) -> dict:
        """Get encryption statistics"""
        if not self.encryption_history:
            return {}
        
        total_messages = len(self.encryption_history)
        total_data = sum(record['message_length'] for record in self.encryption_history)
        
        return {
            'total_encryptions': total_messages,
            'total_data_encrypted': total_data,
            'average_message_length': total_data / total_messages if total_messages > 0 else 0
        }