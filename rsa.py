import secrets
import miller_rabin
import egcd


def is_probably_prime(x, rounds=40):
    return miller_rabin.miller_rabin(x, rounds)


def generate_random_number(bits):
    return secrets.randbits(bits)


def generate_large_prime(bits=1024, attempts=10000):
    for _ in range(attempts):
        candidate = generate_random_number(bits)
        if is_probably_prime(candidate):
            return candidate

    raise f"Failed to generate probably prime number of length {bits} in {attempts} attempts."


def generate_prime_factors(factor_bits=1024, min_factor_delta_bits=256, attempts=10000):
    while True:
        p = generate_large_prime(factor_bits, attempts)
        q = generate_large_prime(factor_bits, attempts)
        if abs(p - q).bit_length() >= min_factor_delta_bits:
            return p, q
    raise f"Failed to generate two prime factors in {attempts} attempts."


def generate_public_exponent(p, q, attempts=1000):
    euler_totient = (p - 1) * (q - 1)

    # Choose a random number [a] such that GCD(a, phi(n)) = 1 and 1 < a < phi(n).
    # Additionally, let's make sure that [a] is at least [min_bits_for_exponent] long.
    for _ in range(attempts):
        a = generate_random_number(euler_totient.bit_length())

        if a <= 1 or a >= euler_totient:
            continue

        # We only need GCD, but we can also run Extended GCD since that library is already available.
        gcd, _, _ = egcd.egcd(a, euler_totient)
        if gcd == 1:
            return a

    raise f"Failed to generate public exponent for p={p} and q={q}. Attempted {attempts} times."


def compute_private_exponent(a, p, q):
    phi = (p - 1) * (q - 1)
    # The Extended Euclidean Algorithm solves: tx + zy = GCD(t, z)
    # In our case: t=a and z=phi.
    # The solution for [x] is the private exponent.
    gcd, b, _ = egcd.egcd(a, phi)
    assert(abs(gcd) == 1)

    # EEA may return a negative number, but we need a remainder, so we convert it to the positive number.
    if b < 0:
        return b + phi
    return b


def modular_exponent(x, a, n):
    if a == 0:
        return 1
    elif a % 2 == 1:
        return x * modular_exponent(x, a - 1, n) % n
    else:
        half = modular_exponent(x, a // 2, n)
        return half * half % n


def encrypt(x, a, n):
    return modular_exponent(x, a, n)


def decrypt(y, b, n):
    return modular_exponent(y, b, n)


# Use fewer bits for demonstration purposes because the numbers don't fit on the screen otherwise.
p, q = generate_prime_factors(factor_bits=128, min_factor_delta_bits=32)
n = p * q
a = generate_public_exponent(p, q)
b = compute_private_exponent(a, p, q)

print("p = ", p)
print("q = ", q)
print("n = ", n)
print("a = ", a)
print("b = ", b)
print()
print(f"Public Key:")
print(f"  n={n}")
print(f"  a={a}")
print()
print(f"Private Key:")
print(f"  p={p}")
print(f"  q={q}")
print(f"  b={b}")
print()

x = 1234567890
y = encrypt(x, a, n)
decrypted = decrypt(y, b, n)

print(f"Let's encrypt a number: {x}")
print(f"Encrypted: {y}")
print(f"Decrypted: {decrypted}")

assert(x == decrypted)