#!/usr/bin/env python3
"""
Quantum Key Distribution BB84 Protocol - Main Terminal Interface
"""

import sys
import time
from bb84_protocol import BB84Protocol
from secure_messaging import SecureMessaging
from error_correction import ErrorCorrection

def print_banner():
    banner = """
    ╔══════════════════════════════════════════════════════════════╗
    ║           QUANTUM KEY DISTRIBUTION BB84 PROTOCOL            ║
    ║                  Secure Communication System               ║
    ╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)

def main_menu():
    print("\n" + "="*60)
    print("MAIN MENU")
    print("="*60)
    print("1. Generate Quantum Key (BB84 Protocol)")
    print("2. Encrypt/Decrypt Message")
    print("3. Simulate Eavesdropping Attack")
    print("4. Error Correction Demo")
    print("5. Exit")
    print("-"*60)
    
    while True:
        try:
            choice = input("Enter your choice (1-5): ").strip()
            if choice in ['1', '2', '3', '4', '5']:
                return choice
            else:
                print("❌ Invalid choice. Please enter 1-5.")
        except KeyboardInterrupt:
            print("\n👋 Exiting...")
            sys.exit(0)

def run_bb84_demo():
    print("\n🎯 BB84 Quantum Key Distribution Demo")
    print("-" * 40)
    
    try:
        key_length = int(input("Enter desired key length (128-512): ") or "256")
        if key_length < 128 or key_length > 512:
            print("⚠️  Key length adjusted to 256 (must be between 128-512)")
            key_length = 256
    except ValueError:
        key_length = 256
    
    print(f"\n🔑 Generating quantum key with {key_length} bits...")
    
    # Initialize BB84 protocol
    bb84 = BB84Protocol(key_length=key_length)
    
    # Run the complete protocol
    print("\n🚀 Starting BB84 Protocol...")
    print("═" * 50)
    
    success, final_key, qber, stats = bb84.run_protocol()
    
    if success:
        print(f"\n✅ BB84 Protocol Completed Successfully!")
        print(f"🔑 Final Key: {final_key[:64]}..." if len(final_key) > 64 else f"🔑 Final Key: {final_key}")
        print(f"📊 Key Length: {len(final_key)} bits")
        print(f"📈 QBER: {qber:.3f}")
        print(f"📊 Efficiency: {stats['efficiency']:.2f}%")
    else:
        print(f"\n❌ BB84 Protocol Failed!")
        print(f"📈 QBER: {qber:.3f} (above security threshold)")
    
    return success, final_key if success else None

def run_encryption_demo():
    print("\n🔐 Secure Messaging Demo")
    print("-" * 40)
    
    # First generate a quantum key
    print("Step 1: Generating quantum key...")
    bb84 = BB84Protocol(key_length=256)
    success, quantum_key, _, _ = bb84.run_protocol()
    
    if not success:
        print("❌ Cannot proceed - quantum key generation failed!")
        return
    
    secure_msg = SecureMessaging()
    
    print("\nStep 2: Encrypting message...")
    message = input("Enter message to encrypt: ").strip() or "Hello Quantum World! 🚀"
    
    # Encrypt the message
    encrypted_data = secure_msg.encrypt_message(message, quantum_key)
    
    print(f"\n📨 Original Message: {message}")
    print(f"🔒 Encrypted Data: {encrypted_data['ciphertext'].hex()[:64]}...")
    print(f"🎯 Nonce: {encrypted_data['nonce'].hex()}")
    print(f"🔐 MAC: {encrypted_data['mac'].hex()[:32]}...")
    
    # Decrypt the message
    print("\nStep 3: Decrypting message...")
    decrypted_message = secure_msg.decrypt_message(encrypted_data, quantum_key)
    
    if decrypted_message:
        print(f"📬 Decrypted Message: {decrypted_message}")
        print("✅ Encryption/Decryption Successful!")
    else:
        print("❌ Decryption Failed!")

def run_eavesdropping_demo():
    print("\n👂 Eavesdropping Detection Demo")
    print("-" * 40)
    
    print("This demo shows how BB84 detects eavesdroppers...")
    
    # Run without eavesdropping
    print("\n1. Running BB84 without eavesdropping...")
    bb84_secure = BB84Protocol(key_length=128, eavesdrop_probability=0.0)
    success_secure, _, qber_secure, _ = bb84_secure.run_protocol()
    print(f"   QBER: {qber_secure:.3f} - {'✅ Secure' if success_secure else '❌ Insecure'}")
    
    # Run with eavesdropping
    print("\n2. Running BB84 WITH eavesdropping...")
    bb84_eavesdrop = BB84Protocol(key_length=128, eavesdrop_probability=0.5)
    success_eavesdrop, _, qber_eavesdrop, _ = bb84_eavesdrop.run_protocol()
    print(f"   QBER: {qber_eavesdrop:.3f} - {'✅ Secure' if success_eavesdrop else '❌ Eavesdropper Detected!'}")
    
    print(f"\n📊 Eavesdropping increases QBER from {qber_secure:.3f} to {qber_eavesdrop:.3f}")
    print("💡 This allows Alice and Bob to detect the presence of Eve!")
    print("🎯 Security Threshold: 0.12 (12%)")

def run_error_correction_demo():
    print("\n🔧 Error Correction Demo")
    print("-" * 40)
    
    ec = ErrorCorrection()
    
    # Simulate noisy key
    original_key = "10101010101010101010101010101010"
    print(f"🔑 Original Key: {original_key}")
    
    # Introduce errors
    noisy_key = ec._introduce_errors(original_key, error_rate=0.15)
    print(f"📡 Noisy Key:    {noisy_key}")
    
    # Correct errors
    corrected_key = ec.cascade_correction(noisy_key, original_key)
    print(f"🔧 Corrected Key: {corrected_key}")
    
    # Calculate error rates
    original_errors = ec.calculate_error_rate(original_key, noisy_key)
    corrected_errors = ec.calculate_error_rate(original_key, corrected_key)
    
    print(f"\n📊 Error Rate Before Correction: {original_errors:.3f}")
    print(f"📊 Error Rate After Correction: {corrected_errors:.3f}")
    print(f"🎯 Correction Efficiency: {(1 - corrected_errors/original_errors)*100:.1f}%")

def main():
    print_banner()
    
    while True:
        choice = main_menu()
        
        if choice == '1':
            run_bb84_demo()
        elif choice == '2':
            run_encryption_demo()
        elif choice == '3':
            run_eavesdropping_demo()
        elif choice == '4':
            run_error_correction_demo()
        elif choice == '5':
            print("\n👋 Thank you for using Quantum BB84 Protocol!")
            print("🔒 Stay secure! 🌟")
            break
        
        input("\nPress Enter to continue...")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Program interrupted. Goodbye!")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")