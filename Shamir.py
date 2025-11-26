import random
import hashlib
from decimal import Decimal

FIELD_SIZE = 47951


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


def reconstruct_secret(shares):
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



if __name__ == '__main__':
    t, n = 5, 7

    secret = ""
    with open('sample.txt', 'rb') as f:
        secret = f.read()
    
    #secret = "ManchegoManchegoManchegoManchegoManchegoManchegoManchegoManchegoManchego"
    print(f'Original Secret: {secret}')

    # Phase I: Generation of shares
    #secret_bytes = list(secret.encode('utf-8'))
    secret_bytes = list(secret)
    print(f'Byte values: {secret_bytes}')
    
    shares = generate_shares(n, t, secret_bytes)
    print(f'Number of shares: {len(shares)}')
    print(f'Bytes per share: {len(shares[0])}')

    # Phase II: Secret Reconstruction
    pool = random.sample(shares, t)
    print(f'Using {len(pool)} shares for reconstruction')
    
    reconstructed_bytes = reconstruct_secret(pool)
    #print(f'Reconstructed bytes: {reconstructed_bytes}')
    
    try:
        reconstructed_secret = bytes(reconstructed_bytes).decode('utf-8')
        print(f'Reconstructed secret: "{reconstructed_secret}"')
    except UnicodeDecodeError:
        print("Error: Could not decode bytes to string")