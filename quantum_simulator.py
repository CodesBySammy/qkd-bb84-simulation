"""
Quantum State Simulator for BB84 Protocol
"""

import numpy as np
import random
from enum import Enum
from typing import Tuple, List, Dict

class Basis(Enum):
    """Measurement bases in BB84 protocol"""
    RECTILINEAR = 0  # + basis (0°, 90°)
    DIAGONAL = 1     # × basis (45°, 135°)

class QuantumSimulator:
    """
    Simulates quantum states and measurements for BB84 protocol
    Implements quantum principles: superposition, measurement collapse, no-cloning
    """
    
    # Quantum state representations
    # |0⟩ = [1, 0]ᵀ, |1⟩ = [0, 1]ᵀ
    # |+⟩ = 1/√2 [1, 1]ᵀ, |-⟩ = 1/√2 [1, -1]ᵀ
    
    STATES = {
        # Rectilinear basis states
        (0, Basis.RECTILINEAR): np.array([1.0 + 0j, 0.0 + 0j]),  # |0⟩
        (1, Basis.RECTILINEAR): np.array([0.0 + 0j, 1.0 + 0j]),  # |1⟩
        
        # Diagonal basis states  
        (0, Basis.DIAGONAL): np.array([1.0/np.sqrt(2) + 0j, 1.0/np.sqrt(2) + 0j]),  # |+⟩
        (1, Basis.DIAGONAL): np.array([1.0/np.sqrt(2) + 0j, -1.0/np.sqrt(2) + 0j]), # |-⟩
    }
    
    def __init__(self):
        self.measurement_history = []
    
    def prepare_state(self, bit: int, basis: Basis) -> np.ndarray:
        """
        Prepare a quantum state based on bit value and basis
        
        Args:
            bit: 0 or 1
            basis: Measurement basis
            
        Returns:
            Quantum state vector
        """
        if bit not in [0, 1]:
            raise ValueError("Bit must be 0 or 1")
        
        return self.STATES[(bit, basis)].copy()
    
    def measure(self, state: np.ndarray, basis: Basis) -> int:
        """
        Measure a quantum state in the specified basis
        
        Args:
            state: Quantum state vector
            basis: Measurement basis
            
        Returns:
            Measurement result (0 or 1)
        """
        # If measuring in rectilinear basis
        if basis == Basis.RECTILINEAR:
            prob_0 = abs(state[0])**2
            result = 0 if random.random() < prob_0 else 1
            
        # If measuring in diagonal basis  
        else:
            # Convert to diagonal basis
            diagonal_state = self._to_diagonal_basis(state)
            prob_plus = abs(diagonal_state[0])**2
            result = 0 if random.random() < prob_plus else 1
        
        # Record measurement
        self.measurement_history.append({
            'state': state.copy(),
            'basis': basis,
            'result': result
        })
        
        return result
    
    def _to_diagonal_basis(self, state: np.ndarray) -> np.ndarray:
        """
        Convert state to diagonal basis representation
        """
        # Hadamard transformation
        H = np.array([[1/np.sqrt(2), 1/np.sqrt(2)],
                      [1/np.sqrt(2), -1/np.sqrt(2)]])
        return H @ state
    
    def calculate_measurement_probabilities(self, state: np.ndarray, basis: Basis) -> Tuple[float, float]:
        """
        Calculate probabilities of measuring 0 or 1 in given basis
        
        Returns:
            Tuple[probability_0, probability_1]
        """
        if basis == Basis.RECTILINEAR:
            prob_0 = abs(state[0])**2
            prob_1 = abs(state[1])**2
        else:
            diagonal_state = self._to_diagonal_basis(state)
            prob_0 = abs(diagonal_state[0])**2  # Probability of |+⟩
            prob_1 = abs(diagonal_state[1])**2  # Probability of |-⟩
        
        return prob_0, prob_1
    
    def eavesdrop_measurement(self, state: np.ndarray) -> Tuple[int, np.ndarray]:
        """
        Simulate eavesdropper's measurement
        Eve randomly chooses a basis and measures
        
        Returns:
            Tuple[measurement_result, collapsed_state]
        """
        # Eve randomly chooses basis
        eve_basis = random.choice([Basis.RECTILINEAR, Basis.DIAGONAL])
        
        # Measure in chosen basis
        result = self.measure(state, eve_basis)
        
        # Prepare new state based on measurement result (wavefunction collapse)
        new_state = self.prepare_state(result, eve_basis)
        
        return result, new_state
    
    def get_measurement_statistics(self) -> Dict:
        """Get statistics about all measurements performed"""
        if not self.measurement_history:
            return {}
        
        rectilinear_measurements = [m for m in self.measurement_history 
                                  if m['basis'] == Basis.RECTILINEAR]
        diagonal_measurements = [m for m in self.measurement_history 
                               if m['basis'] == Basis.DIAGONAL]
        
        return {
            'total_measurements': len(self.measurement_history),
            'rectilinear_measurements': len(rectilinear_measurements),
            'diagonal_measurements': len(diagonal_measurements),
            'average_rectilinear_0': (
                sum(1 for m in rectilinear_measurements if m['result'] == 0) 
                / len(rectilinear_measurements) if rectilinear_measurements else 0
            ),
            'average_diagonal_0': (
                sum(1 for m in diagonal_measurements if m['result'] == 0) 
                / len(diagonal_measurements) if diagonal_measurements else 0
            )
        }