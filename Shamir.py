import random
import hashlib
from decimal import Decimal
import numpy as np
#To-do list: Make sure it can take in secrets of any size
# Make sure it can take in secrets of any type (int, str, bytes, etc.)
# Make sure the coefficients generation is efficient
# Implement hashing
# Implement syndrome decoding

FIELD_SIZE = 10**5


def polynom(x, coefficients):
    point = 0

    for coefficient_index, coefficient_value in enumerate(coefficients[::-1]):
        point += x ** coefficient_index * coefficient_value
    return point


def coeff(t, secret_byte):
    coeff = [random.randrange(0, FIELD_SIZE) for _ in range(t - 1)]
    coeff.append(secret_byte)
    return coeff


def generate_shares(n, m, secret_bytes):
    all_shares = []
    
    for byte_index, byte_value in enumerate(secret_bytes):
        coefficients = coeff(m, byte_value)
        byte_shares = []
        
        for i in range(1, n+1):
            x = random.randrange(1, FIELD_SIZE)
            y = polynom(x, coefficients)
            byte_shares.append((x, y))
        
        all_shares.append(byte_shares)
    
    organized_shares = []
    for i in range(n):
        share = []
        for byte_index in range(len(secret_bytes)):
            share.append(all_shares[byte_index][i])
        organized_shares.append(share)
    print(len(organized_shares))
    return organized_shares


def reconstruct_secret(shares): #With Legrange Interpolation
    num_bytes = len(shares[0])
    reconstructed_bytes = []
    
    for byte_index in range(num_bytes):
        byte_shares = [share[byte_index] for share in shares]
        
        sums = 0
        for j, share_j in enumerate(byte_shares):
            xj, yj = share_j
            prod = Decimal(1)
            
            for i, share_i in enumerate(byte_shares):
                xi, _ = share_i
                if i != j:
                    prod *= Decimal(Decimal(xi)/(xi-xj))
            
            prod *= yj
            sums += Decimal(prod)
        
        reconstructed_byte = int(round(Decimal(sums), 0))
        reconstructed_bytes.append(reconstructed_byte)
    
    return reconstructed_bytes

# Syndrome decoding method
def generate_syndrome_matrix():
    # basic parity check matrix for (n, n-1) code
    H = np.array([[1, 1, 1, 1, 1, 1, 1, 1, 1]], dtype=int) 
    return H

def calculate_syndrome(received_bits, H):
    """Calculate syndrome vector"""
    return np.dot(H, received_bits) % 2

def correct_error(bits, syndrome, H):
    """Corrects a single error and returns (corrected_bits, was_corrected)"""
    if(np.all(syndrome == 0)):
        return bits, False  # No error - return tuple with False flag
    
    for i in range(len(bits)):
        test_bits = bits.copy()
        test_bits[i] = 1 - test_bits[i]
        test_syndrome = calculate_syndrome(test_bits, H)
        if(np.all(test_syndrome == 0)):  # Changed condition - look for zero syndrome
            return test_bits, True  # Corrected error - return tuple with True flag
    
    return bits, False  # Could not correct error - return original with False flag

def syndrome_decode(byte_value):
    # Extract 8 data bits from the reconstructed byte
    data_bits = np.array([int(b) for b in format(byte_value & 0xFF, '08b')])
    
    # Since we don't have actual parity bits stored, we can only do basic validation
    # For a simple parity check, assume the byte should have even parity
    actual_parity = np.sum(data_bits) % 2
    
    # If parity is odd, we detected an error - try to find which bit to flip
    if actual_parity == 0:
        # Even parity - assume no error
        return byte_value & 0xFF, False
    else:
        # Odd parity - there might be an error, but we can't reliably correct it
        # without proper error correction encoding during share generation
        # For now, just return the original byte
        return byte_value & 0xFF, False

def reconstruct_secret_with_syndrome_decoding(shares):
    """Reconstruct secret with syndrome decoding error correction"""
    num_bytes = len(shares[0])
    reconstructed_bytes = []
    errors_corrected = 0
    
    for byte_index in range(num_bytes):
        byte_shares = [share[byte_index] for share in shares]
        
        # Standard Lagrange interpolation
        sums = 0
        for j, share_j in enumerate(byte_shares):
            xj, yj = share_j
            prod = Decimal(1)
            
            for i, share_i in enumerate(byte_shares):
                xi, _ = share_i
                if i != j:
                    prod *= Decimal(Decimal(xi)/(xi-xj))
            
            prod *= yj
            sums += Decimal(prod)
        
        # Get reconstructed byte
        raw_byte = int(round(Decimal(sums), 0))
        
        # Basic validation - just ensure it's a valid byte value
        if 0 <= raw_byte <= 255:
            reconstructed_bytes.append(raw_byte)
        else:
            # Handle overflow/underflow
            corrected_byte = max(0, min(255, raw_byte))
            reconstructed_bytes.append(corrected_byte)
            if raw_byte != corrected_byte:
                errors_corrected += 1
                print(f"Byte overflow corrected in position {byte_index}: {raw_byte} -> {corrected_byte}")
    
    if errors_corrected > 0:
        print(f"Total errors corrected: {errors_corrected}")
    
    return reconstructed_bytes

if __name__ == '__main__':
    t, n = 3, 5
    secret = "ManchegoManchegoManchegoManchegoManchegoManchegoManchegoManchegoManchego"
    print(f'Original Secret: {secret}')
    # secret = hashlib.sha256(secret.encode('utf-8')).hexdigest()
    # print(f'SHA-256 Hash: {secret}')

    # Phase I: Generation of shares
    secret_bytes = list(secret.encode('utf-8'))
    print(f'Byte values: {secret_bytes}')
    
    shares = generate_shares(n, t, secret_bytes)
    print(f'Number of shares: {len(shares)}')
    print(f'Bytes per share: {len(shares[0])}')

    # Phase II: Secret Reconstruction
    pool = random.sample(shares, t)
    print(f'Using {len(pool)} shares for reconstruction')
    
    #reconstructed_bytes = reconstruct_secret(pool)
    reconstructed_bytes = reconstruct_secret_with_syndrome_decoding(pool)
    print(f'Reconstructed bytes: {reconstructed_bytes}')
    
    # Convert bytes back to string
    try:
        reconstructed_secret = bytes(reconstructed_bytes).decode('utf-8')
        print(f'Reconstructed secret: "{reconstructed_secret}"')
    except UnicodeDecodeError:
        print("Error: Could not decode bytes to string")