import random
import math
from decimal import Decimal
#To-do list: Make sure it can take in secrets of any size
# Make sure it can take in secrets of any type (int, str, bytes, etc.)
# Make sure the coefficients generation is efficient
# Implement hashing
# Implement syndrome decoding

FIELD_SIZE = 10**5 #Base field size


def reconstruct_secret(shares):
    sums = 0
    prod_arr = []

    for j, share_j in enumerate(shares):
        xj, yj = share_j
        prod = Decimal(1)

        for i, share_i in enumerate(shares):
            xi, _ = share_i
            if i != j:
                prod *= Decimal(Decimal(xi)/(xi-xj))

        prod *= yj
        sums += Decimal(prod)

    return int(round(Decimal(sums), 0))


def polynom(x, coefficients):
    point = 0
    # Loop through reversed list, so that indices from enumerate match the
    # actual coefficient indices
    for coefficient_index, coefficient_value in enumerate(coefficients[::-1]):
        point += x ** coefficient_index * coefficient_value
    return point


def coeff(t, secret):
    for b in secret:
        coeff = [random.randrange(0, FIELD_SIZE) for _ in range(t - 1)]
        coeff.append(b)
    return coeff


def generate_shares(n, m, secret):
    # global FIELD_SIZE
    # print(FIELD_SIZE)
    # if(FIELD_SIZE <= secret):
    #     FIELD_SIZE = 10 ** (int(math.log10(secret))) * 10
    #     print(FIELD_SIZE)
    coefficients = coeff(m, secret)
    shares = []

    for i in range(1, n+1):
        x = random.randrange(1, FIELD_SIZE)
        shares.append((x, polynom(x, coefficients)))

    return shares


# Driver code
if __name__ == '__main__':

    t, n = 3, 5
    secret = "Manchego"
    print(f'Original Secret: {secret}')

    # Phase I: Generation of shares
    bytes = secret.encode('utf-8')
    print(f'Integer Secret: {list(bytes)}')
    shares = generate_shares(n, t, bytes)
    print(f'Shares: {", ".join(str(share) for share in shares)}')

    # Phase II: Secret Reconstruction
    # Picking t shares randomly for
    # reconstruction
    pool = random.sample(shares, t)
    print(f'Combining shares: {", ".join(str(share) for share in pool)}')
    print(f'Reconstructed secret: {reconstruct_secret(pool)}')