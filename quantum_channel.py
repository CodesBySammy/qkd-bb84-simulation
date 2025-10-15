"""
Quantum Channel for BB84 Protocol
Simulates quantum transmission with noise and eavesdropping
"""

import numpy as np
import random
from typing import List, Optional
from quantum_simulator import QuantumSimulator, Basis

class QuantumChannel:
    """
    Simulates a quantum channel with:
    - Quantum noise
    - Eavesdropping capability
    - Transmission errors
    """
    
    def __init__(self, eavesdrop_probability: float = 0.0, noise_level: float = 0.01):
        self.eavesdrop_probability = eavesdrop_probability
        self.noise_level = noise_level  # Probability of natural errors
        self.quantum_simulator = QuantumSimulator()
        self.eavesdropping_attempts = 0
        self.transmission_errors = 0
        
    def transmit(self, states: List[np.ndarray]) -> List[np.ndarray]:
        """
        Transmit quantum states through the channel
        Applies noise and potential eavesdropping
        
        Returns:
            Transmitted states (possibly modified by Eve and noise)
        """
        transmitted_states = []
        
        for i, state in enumerate(states):
            # Simulate eavesdropping with given probability
            if random.random() < self.eavesdrop_probability:
                self.eavesdropping_attempts += 1
                # Eve measures and resends
                _, new_state = self.quantum_simulator.eavesdrop_measurement(state)
                transmitted_state = new_state
            else:
                transmitted_state = state.copy()
            
            # Apply quantum noise
            noisy_state = self._apply_quantum_noise(transmitted_state)
            transmitted_states.append(noisy_state)
        
        print(f"   📊 Channel stats: Eavesdropping attempts: {self.eavesdropping_attempts}/{len(states)}")
        return transmitted_states
    
    def _apply_quantum_noise(self, state: np.ndarray) -> np.ndarray:
        """
        Apply quantum noise to a state
        Simulates natural channel imperfections
        """
        if random.random() < self.noise_level:
            self.transmission_errors += 1
            
            # Apply a small random perturbation
            noise = np.random.normal(0, 0.1, 2) + 1j * np.random.normal(0, 0.1, 2)
            noisy_state = state + noise * 0.05  # Small noise amplitude
            
            # Renormalize
            norm = np.linalg.norm(noisy_state)
            if norm > 0:
                noisy_state = noisy_state / norm
            return noisy_state
        
        return state.copy()
    
    def calculate_channel_fidelity(self, original_states: List[np.ndarray], 
                                 received_states: List[np.ndarray]) -> float:
        """
        Calculate average fidelity between original and received states
        """
        if len(original_states) != len(received_states):
            raise ValueError("State lists must have same length")
        
        total_fidelity = 0.0
        for orig, recv in zip(original_states, received_states):
            fidelity = abs(np.vdot(orig, recv))**2
            total_fidelity += fidelity
        
        return total_fidelity / len(original_states)
    
    def get_channel_statistics(self) -> dict:
        """Get quantum channel statistics"""
        return {
            'eavesdrop_probability': self.eavesdrop_probability,
            'noise_level': self.noise_level,
            'eavesdropping_attempts': self.eavesdropping_attempts,
            'transmission_errors': self.transmission_errors,
            'eavesdropping_rate': self.eavesdropping_attempts / max(1, self.eavesdropping_attempts)
        }