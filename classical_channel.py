"""
Classical Channel for BB84 Protocol
Handles public communication between Alice and Bob
"""

import hashlib
from typing import List, Any

class ClassicalChannel:
    """
    Simulates a classical authenticated channel
    All communication is public but authenticated
    """
    
    def __init__(self):
        self.communication_log = []
        self.authentication_key = None
    
    def send_message(self, sender: str, receiver: str, message: Any, message_type: str = "INFO") -> bool:
        """
        Send a message through the classical channel
        
        Args:
            sender: Message sender (Alice/Bob)
            receiver: Message receiver (Alice/Bob)  
            message: The message content
            message_type: Type of message (BASIS, KEY, ERROR, INFO)
            
        Returns:
            Success flag
        """
        communication = {
            'sender': sender,
            'receiver': receiver,
            'message': message,
            'type': message_type,
            'timestamp': self._get_timestamp()
        }
        
        self.communication_log.append(communication)
        
        # Print the communication
        print(f"   📢 {sender} → {receiver} [{message_type}]: {message}")
        
        return True
    
    def exchange_bases(self, alice_bases: List, bob_bases: List) -> List[int]:
        """
        Exchange basis information and find matching bases
        
        Returns:
            List of indices where bases match
        """
        matching_indices = []
        
        for i, (alice_basis, bob_basis) in enumerate(zip(alice_bases, bob_bases)):
            if alice_basis == bob_basis:
                matching_indices.append(i)
        
        # Log the basis exchange
        self.send_message("Alice", "Bob", f"Basis comparison: {len(matching_indices)} matches", "BASIS")
        
        return matching_indices
    
    def estimate_error_rate(self, alice_test_bits: List[int], bob_test_bits: List[int]) -> float:
        """
        Publicly compare test bits to estimate error rate
        
        Returns:
            Quantum Bit Error Rate (QBER)
        """
        if len(alice_test_bits) != len(bob_test_bits):
            raise ValueError("Test bit sequences must have same length")
        
        errors = 0
        for a_bit, b_bit in zip(alice_test_bits, bob_test_bits):
            if a_bit != b_bit:
                errors += 1
        
        qber = errors / len(alice_test_bits) if alice_test_bits else 0
        
        # Log error estimation
        self.send_message("Alice", "Bob", 
                         f"Error estimation: {errors}/{len(alice_test_bits)} = {qber:.3f}", 
                         "ERROR")
        
        return qber
    
    def authenticate_message(self, message: str, mac: str) -> bool:
        """
        Authenticate message using Message Authentication Code
        """
        if not self.authentication_key:
            # For simulation, generate a simple authentication key
            self.authentication_key = hashlib.sha256(b"bb84_auth_key").digest()
        
        expected_mac = self._compute_mac(message, self.authentication_key)
        return expected_mac == mac
    
    def _compute_mac(self, message: str, key: bytes) -> str:
        """Compute Message Authentication Code"""
        message_bytes = message.encode('utf-8')
        mac = hashlib.sha256(key + message_bytes).hexdigest()
        return mac
    
    def _get_timestamp(self) -> str:
        """Get current timestamp for logging"""
        from datetime import datetime
        return datetime.now().strftime("%H:%M:%S")
    
    def get_communication_summary(self) -> dict:
        """Get summary of all communications"""
        if not self.communication_log:
            return {}
        
        message_types = {}
        for comm in self.communication_log:
            msg_type = comm['type']
            message_types[msg_type] = message_types.get(msg_type, 0) + 1
        
        return {
            'total_messages': len(self.communication_log),
            'message_types': message_types,
            'alice_to_bob': sum(1 for comm in self.communication_log if comm['sender'] == 'Alice'),
            'bob_to_alice': sum(1 for comm in self.communication_log if comm['sender'] == 'Bob')
        }