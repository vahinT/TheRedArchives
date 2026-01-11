print("Welcome to Hydrogen Calculator")
print("a = +, s = -, m = x, d = ÷, p = (to the power of)")

smbo = input()

if smbo == "a":
    print(int(input()) + int(input()))
    print(input())
elif smbo == "s":
    print(int(input()) - int(input()))
    print(input())
elif smbo == "m":
    print(int(input()) * int(input()))
    print(input())
elif smbo == "d":
    n1 = int(input())
    n2 = int(input())
    print(input())
    if n2 == 0:
        print("∞")
        print(input())
    else:
        print(n1 / n2)
        print(n1 // n2)
        print(input())
elif smbo == "p":
    print(int(input()) ** int(input()))
    print(input())
else:
    print("Invalid symbol. Please choose a valid operation.")
    print(input())
