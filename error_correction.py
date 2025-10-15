"""
Error Correction for BB84 Protocol
Implements Cascade protocol for quantum key error correction
"""

import random
from typing import List, Tuple

class ErrorCorrection:
    """
    Implements error correction protocols for quantum keys
    Primary method: Cascade protocol for BB84
    """
    
    def __init__(self):
        self.correction_history = []
    
    def cascade_correction(self, bob_key: str, alice_key: str, max_passes: int = 4) -> str:
        """
        Implement Cascade error correction protocol
        
        Args:
            bob_key: Bob's noisy key
            alice_key: Alice's correct key (for verification)
            max_passes: Maximum number of correction passes
            
        Returns:
            Corrected key
        """
        if len(bob_key) != len(alice_key):
            raise ValueError("Keys must have same length")
        
        key_length = len(bob_key)
        bob_list = list(bob_key)
        alice_list = list(alice_key)
        
        print(f"   🔧 Starting Cascade protocol...")
        print(f"   📊 Initial error rate: {self.calculate_error_rate(alice_key, bob_key):.3f}")
        
        for pass_num in range(max_passes):
            block_size = 2 ** pass_num
            corrections = 0
            
            for i in range(0, key_length, block_size):
                block_end = min(i + block_size, key_length)
                
                # Calculate parity for this block
                bob_parity = self._calculate_parity(bob_list[i:block_end])
                alice_parity = self._calculate_parity(alice_list[i:block_end])
                
                # If parities differ, there's an odd number of errors in this block
                if bob_parity != alice_parity:
                    # For simplicity, we correct one error
                    # In full Cascade, this would involve binary search
                    corrected = self._correct_single_error(
                        bob_list[i:block_end], 
                        alice_list[i:block_end],
                        i
                    )
                    if corrected:
                        corrections += 1
            
            current_error_rate = self.calculate_error_rate(''.join(alice_list), ''.join(bob_list))
            print(f"   Pass {pass_num + 1}: {corrections} corrections, error rate: {current_error_rate:.3f}")
            
            if current_error_rate == 0:
                break
        
        corrected_key = ''.join(bob_list)
        final_error_rate = self.calculate_error_rate(alice_key, corrected_key)
        
        # Record correction session
        self.correction_history.append({
            'initial_errors': self._count_errors(alice_key, bob_key),
            'final_errors': self._count_errors(alice_key, corrected_key),
            'passes_used': min(pass_num + 1, max_passes),
            'key_length': key_length
        })
        
        print(f"   ✅ Final error rate: {final_error_rate:.3f}")
        return corrected_key
    
    def _calculate_parity(self, block: List[str]) -> int:
        """Calculate parity of a block (XOR of all bits)"""
        parity = 0
        for bit in block:
            parity ^= int(bit)
        return parity
    
    def _correct_single_error(self, bob_block: List[str], alice_block: List[str], start_index: int) -> bool:
        """
        Correct a single error in a block
        Simplified version - in real Cascade, this uses binary search
        """
        for i in range(len(bob_block)):
            if bob_block[i] != alice_block[i]:
                bob_block[i] = alice_block[i]  # Correct the error
                return True
        return False
    
    def _count_errors(self, key1: str, key2: str) -> int:
        """Count number of differing bits between two keys"""
        return sum(1 for a, b in zip(key1, key2) if a != b)
    
    def calculate_error_rate(self, original: str, received: str) -> float:
        """
        Calculate error rate between two keys
        
        Returns:
            Error rate (0.0 to 1.0)
        """
        if len(original) != len(received):
            raise ValueError("Keys must have same length")
        
        if len(original) == 0:
            return 0.0
        
        errors = self._count_errors(original, received)
        return errors / len(original)
    
    def _introduce_errors(self, key: str, error_rate: float) -> str:
        """
        Introduce random errors into a key (for testing)
        
        Returns:
            Key with errors
        """
        key_list = list(key)
        for i in range(len(key_list)):
            if random.random() < error_rate:
                # Flip the bit
                key_list[i] = '1' if key_list[i] == '0' else '0'
        
        return ''.join(key_list)
    
    def get_correction_statistics(self) -> dict:
        """Get error correction statistics"""
        if not self.correction_history:
            return {}
        
        total_corrections = sum(session['initial_errors'] - session['final_errors'] 
                              for session in self.correction_history)
        total_sessions = len(self.correction_history)
        
        return {
            'total_sessions': total_sessions,
            'total_errors_corrected': total_corrections,
            'average_initial_errors': sum(s['initial_errors'] for s in self.correction_history) / total_sessions,
            'average_final_errors': sum(s['final_errors'] for s in self.correction_history) / total_sessions,
            'average_efficiency': (sum((s['initial_errors'] - s['final_errors']) / s['initial_errors'] 
                                  for s in self.correction_history if s['initial_errors'] > 0) / 
                                  sum(1 for s in self.correction_history if s['initial_errors'] > 0)) * 100
        }