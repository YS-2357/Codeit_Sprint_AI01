from decimal import Decimal, getcontext

def pi_to_n_decimal_places(n):
    getcontext().prec = n + 2  # 소수점 아래 n자리 + 2자리로 정밀도 설정
    C = 426880 * Decimal(10005).sqrt()
    K, M, X, L, S = 6, 1, 1, 13591409, 13591409

    for i in range(1, n * 14 // 10):  # 차수 증가
        M = (K ** 3 - 16 * K) * M // i ** 3
        L += 545140134
        X *= -262537412640768000
        S += Decimal(M * L) / X
        K += 12

    pi = C / S
    return str(pi)[:n + 2]  # 3. 을 포함하여 반환

# 사용 예시
print(pi_to_n_decimal_places(100))  # 100자리 예시
# print(pi_to_n_decimal_places(100000))  # 100,000자리 예시

n = int(input())
print(pi_to_n_decimal_places(n))