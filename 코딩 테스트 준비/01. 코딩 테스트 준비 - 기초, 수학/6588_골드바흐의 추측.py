# 백준 문제 6588: 골드바흐의 추측

import sys

def sieve_of_eratosthenes(limit):
    # 에라토스테네스의 체를 사용하여 소수를 구하는 함수
    is_prime = [True] * (limit + 1)
    is_prime[0], is_prime[1] = False, False  # 0과 1은 소수가 아님
    
    # 2부터 √limit까지의 모든 수에 대해 배수들을 지움
    for i in range(2, int(limit ** 0.5) + 1):
        if is_prime[i]:
            for j in range(i * i, limit + 1, i):
                is_prime[j] = False
    
    return is_prime

def find_goldbach(n, is_prime):
    # 주어진 짝수 n에 대해 두 소수의 합으로 나타내는 함수
    for i in range(3, n // 2 + 1):
        if is_prime[i] and is_prime[n - i]:
            return i, n - i
    return None

def main():
    input = sys.stdin.read
    data = input().strip().split()

    # 제한과 그때까지의 소수들
    limit = 1000000  # 주의: 원래 문제의 제한인 1,000,000을 사용
    is_prime = sieve_of_eratosthenes(limit)

    # 결과
    results = []
    for num in data:
        n = int(num)
        if n == 0:
            break
        result = find_goldbach(n, is_prime)
        if result:
            a, b = result
            results.append(f"{n} = {a} + {b}")
        else:
            results.append("Goldbach's conjecture is wrong.")

    # 결과 출력
    print("\n".join(results))

# 프로그램의 시작점
if __name__ == "__main__":
    main()
