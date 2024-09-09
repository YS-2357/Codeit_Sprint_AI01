# 백준 문제 2609: 최대공약수와 최소공배수

import math

def gcd(a, b):
    # 유클리드 호제법을 이용하여 최대공약수를 구하는 함수
    while b != 0:
        a, b = b, a % b
    return a

def lcm(a, b, gcd_value):
    # 두 수의 최소공배수를 구하는 함수
    return a * b // gcd_value

def main():
    # 두 정수를 입력받음
    a, b = map(int, input().split())
    
    # 최대공약수를 계산
    gcd_value = gcd(a, b)
    
    # 최소공배수를 계산
    lcm_value = lcm(a, b, gcd_value)
    
    # 결과 출력
    print(gcd_value)
    print(lcm_value)

# 프로그램의 시작점
if __name__ == "__main__":
    main()
