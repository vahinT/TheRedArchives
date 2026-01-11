
print("Welcome to Hydrogen Calculator")
print("a = +, s = -, m = x, d = ÷, p = (to the power of)")

while True:
    smbo = input("Enter the symbol: ")

    if smbo == "a":
        print(int(input()) + int(input()))
    elif smbo == "s":
        print(int(input( )) - int(input()))
    elif smbo == "m":
        print(int(input())* int(input()))
    elif smbo == "d":
        n1 = int(input())
        n2 = int(input())
        if n2 == 0 or n1 == 0:
            print("∞")
        else:
            print(n1 / n2)
            print(n1//n2)
    elif smbo == "p":
        print(int(input("base: ")) ** int(input("exponent: ")))
    else:
        print("Invalid symbol. Please choose a valid operation.")

    print("Do you want to perform another calculation? (y/n)")
    if input().lower() != "y":
        break
