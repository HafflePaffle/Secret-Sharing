import random
from typing import List, Tuple


# Function to generate a random polynomial
def generate_coefficients(secret: int, threshold: int) -> List[int]:
    coefficients = [secret]
    for _ in range(threshold - 1):
        coefficients.append(random.randint(1, 256))
    return coefficients


# Function to create shares
def create_shares(
    secret: int, total_shares: int, threshold: int
) -> List[Tuple[int, int]]:
    coefficients = generate_coefficients(secret, threshold)
    shares = []
    for x in range(1, total_shares + 1):
        y = sum(coeff * (x**exp) for exp, coeff in enumerate(coefficients))
        shares.append((x, y))
    return shares


# Function to reconstruct the secret
def reconstruct_secret(shares: List[Tuple[int, int]], threshold: int) -> int:
    def _lagrange_interpolation(x: int, x_s: List[int], y_s: List[int]) -> int:
        def _basis(j: int) -> int:
            num = 1
            den = 1
            for m in range(len(x_s)):
                if m != j:
                    num *= x - x_s[m]
                    den *= x_s[j] - x_s[m]
            return num // den

        result = 0
        for j in range(len(y_s)):
            result += y_s[j] * _basis(j)
        return result

    x_s, y_s = zip(*shares)
    return _lagrange_interpolation(0, x_s, y_s)


# Example usage
if __name__ == "__main__":
    secret = 1234
    total_shares = 5
    threshold = 3

    shares = create_shares(secret, total_shares, threshold)
    print("Shares:", shares)

    # Select any 'threshold' number of shares to reconstruct the secret
    selected_shares = shares[:threshold]
    recovered_secret = reconstruct_secret(selected_shares, threshold)
    print("Recovered Secret:", recovered_secret)