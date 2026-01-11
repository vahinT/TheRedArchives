
print("Welcome to Hydrogen Calculator")
print("a = +, s = -, m = x, d = ÷, p = (to the power of) , c-clear , q-quit , cred-credits")
import os

while True:
    smbo = input("Enter the symbol: ")

    if smbo == "a":
        print((float(input())) + (float(input())))


    elif smbo == "s":
        print((float(input( ))) - (float(input())))


    elif smbo == "m":
        print(float(input())* float(input()))


    elif smbo == "d":
        n1 = float(input())
        n2 = float(input())
        if n2 == 0:
            print("∞")
        else:
            nr1 = (n1 / n2)
            nr2 = (n1 // n2)
            if nr1 == nr2 :
             nr2 = 0
             print(nr1)
             print(nr2)
            else :
                print(nr1)
                print(nr2)


    elif smbo == "p":
        print(float(input("base: ")) ** float(input("exponent: ")))

    elif smbo == "c":
         os.system('cls')

    elif smbo == "q":
        if (input("Do you want to quit?(y/n)")) == "y":
            break

    elif smbo == "cred":
        print("Credits:-")
        print("BY Vahin Vamsidhar Masavarpu")
        print("USING python 3.12")

    else:
        print("Invalid symbol. Please choose a valid operation.")
        print(input())
        os.system('cls')
        
    