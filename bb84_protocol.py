"""
BB84 Quantum Key Distribution Protocol Implementation
"""

import numpy as np
import time
from typing import Tuple, List, Dict, Optional
from quantum_simulator import QuantumSimulator, Basis
from classical_channel import ClassicalChannel
from quantum_channel import QuantumChannel
from error_correction import ErrorCorrection

class BB84Protocol:
    """
    Implements the complete BB84 Quantum Key Distribution protocol
    """
    
    def __init__(self, key_length: int = 256, eavesdrop_probability: float = 0.0):
        self.key_length = key_length
        self.eavesdrop_probability = eavesdrop_probability
        self.quantum_simulator = QuantumSimulator()
        self.quantum_channel = QuantumChannel(eavesdrop_probability=eavesdrop_probability)
        self.classical_channel = ClassicalChannel()
        self.error_correction = ErrorCorrection()
        
        # Protocol state
        self.alice_bits = None
        self.alice_bases = None
        self.bob_bases = None
        self.bob_measurements = None
        self.sifted_key_alice = None
        self.sifted_key_bob = None
        self.final_key = None
        self.qber = 0.0
        
    def run_protocol(self) -> Tuple[bool, Optional[str], float, Dict]:
        """
        Execute the complete BB84 protocol
        
        Returns:
            Tuple[bool, Optional[str], float, Dict]: 
            - Success flag
            - Final key (if successful)
            - QBER value
            - Statistics dictionary
        """
        print("🚀 Starting BB84 Protocol...")
        
        try:
            # Step 1: Alice generates random bits and bases
            print("1. 🔑 Alice generating random bits and bases...")
            self.alice_bits, self.alice_bases = self._generate_alice_data()
            
            # Step 2: Prepare and send quantum states
            print("2. 📡 Preparing and sending qubits...")
            quantum_states = self._prepare_quantum_states()
            
            # Step 3: Quantum transmission with potential eavesdropping
            print("3. 🌌 Transmitting through quantum channel...")
            transmitted_states = self.quantum_channel.transmit(quantum_states)
            
            # Step 4: Bob measures with random bases
            print("4. 📊 Bob measuring qubits...")
            self.bob_bases = self._generate_bob_bases()
            self.bob_measurements = self._bob_measure(transmitted_states)
            
            # Step 5: Basis reconciliation (sifting)
            print("5. 🔄 Performing basis reconciliation...")
            self.sifted_key_alice, self.sifted_key_bob = self._basis_reconciliation()
            
            # Step 6: Error rate estimation
            print("6. 📈 Estimating quantum bit error rate (QBER)...")
            self.qber = self._estimate_qber()
            
            # Step 7: Check security threshold
            security_threshold = 0.12  # 12%
            if self.qber > security_threshold:
                print(f"❌ QBER {self.qber:.3f} exceeds security threshold {security_threshold}")
                return False, None, self.qber, self._get_stats()
            
            # Step 8: Error correction
            print("7. 🔧 Performing error correction...")
            corrected_key = self.error_correction.cascade_correction(
                self.sifted_key_bob, self.sifted_key_alice
            )
            
            # Step 9: Privacy amplification
            print("8. 🛡️  Performing privacy amplification...")
            self.final_key = self._privacy_amplification(corrected_key)
            
            print("✅ BB84 Protocol Completed Successfully!")
            return True, self.final_key, self.qber, self._get_stats()
            
        except Exception as e:
            print(f"❌ Protocol failed with error: {e}")
            return False, None, self.qber, self._get_stats()
    
    def _generate_alice_data(self) -> Tuple[List[int], List[Basis]]:
        """Alice generates random bits and random bases"""
        bits = np.random.randint(0, 2, self.key_length).tolist()
        bases = np.random.choice([Basis.RECTILINEAR, Basis.DIAGONAL], 
                               self.key_length).tolist()
        return bits, bases
    
    def _prepare_quantum_states(self) -> List[complex]:
        """Alice prepares quantum states based on her bits and bases"""
        states = []
        for bit, basis in zip(self.alice_bits, self.alice_bases):
            state = self.quantum_simulator.prepare_state(bit, basis)
            states.append(state)
        return states
    
    def _generate_bob_bases(self) -> List[Basis]:
        """Bob generates random measurement bases"""
        return np.random.choice([Basis.RECTILINEAR, Basis.DIAGONAL], 
                              self.key_length).tolist()
    
    def _bob_measure(self, states: List[complex]) -> List[int]:
        """Bob measures the quantum states"""
        measurements = []
        for state, basis in zip(states, self.bob_bases):
            result = self.quantum_simulator.measure(state, basis)
            measurements.append(result)
        return measurements
    
    def _basis_reconciliation(self) -> Tuple[str, str]:
        """Perform basis reconciliation to get sifted keys"""
        alice_sifted = []
        bob_sifted = []
        
        for i in range(len(self.alice_bases)):
            if self.alice_bases[i] == self.bob_bases[i]:
                alice_sifted.append(str(self.alice_bits[i]))
                bob_sifted.append(str(self.bob_measurements[i]))
        
        # Convert to binary strings
        sifted_alice_str = ''.join(alice_sifted)
        sifted_bob_str = ''.join(bob_sifted)
        
        print(f"   📊 Sifted key length: {len(sifted_alice_str)} bits")
        return sifted_alice_str, sifted_bob_str
    
    def _estimate_qber(self) -> float:
        """Estimate Quantum Bit Error Rate"""
        if len(self.sifted_key_alice) == 0:
            return 1.0  # 100% error if no matching bases
            
        # Use a subset for error estimation (typically 50%)
        test_size = max(1, len(self.sifted_key_alice) // 2)
        
        errors = 0
        for i in range(test_size):
            if self.sifted_key_alice[i] != self.sifted_key_bob[i]:
                errors += 1
        
        qber = errors / test_size if test_size > 0 else 0
        return qber
    
    def _privacy_amplification(self, key: str) -> str:
        """
        Perform privacy amplification to reduce Eve's information
        Uses simple XOR-based compression
        """
        if len(key) < 2:
            return key
            
        # Simple privacy amplification: take every other bit XORed
        amplified = []
        for i in range(0, len(key)-1, 2):
            bit1 = int(key[i])
            bit2 = int(key[i+1])
            amplified.append(str(bit1 ^ bit2))
        
        final_key = ''.join(amplified)
        print(f"   📏 Key after privacy amplification: {len(final_key)} bits")
        return final_key
    
    def _get_stats(self) -> Dict:
        """Get protocol statistics"""
        sifted_length = len(self.sifted_key_alice) if self.sifted_key_alice else 0
        final_length = len(self.final_key) if self.final_key else 0
        
        efficiency = (final_length / self.key_length * 100) if self.key_length > 0 else 0
        
        return {
            'initial_bits': self.key_length,
            'sifted_bits': sifted_length,
            'final_bits': final_length,
            'efficiency': efficiency,
            'eavesdrop_probability': self.eavesdrop_probability,
            'matching_bases': sifted_length
        }
    
    def get_detailed_info(self) -> Dict:
        """Get detailed protocol information for debugging"""
        return {
            'alice_bits': self.alice_bits,
            'alice_bases': [basis.name for basis in self.alice_bases],
            'bob_bases': [basis.name for basis in self.bob_bases],
            'bob_measurements': self.bob_measurements,
            'sifted_key_alice': self.sifted_key_alice,
            'sifted_key_bob': self.sifted_key_bob,
            'final_key': self.final_key,
            'qber': self.qber
        }