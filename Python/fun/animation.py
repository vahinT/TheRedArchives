x = 0
print("Road Map!")
print("")
print("")
print("")
x = "00000"
def Frame() :
    print("00000")
    print(x)
    print("00000")
def xman() :
    if x == "00000" :
        x = "10000"
    elif x == "10000":
        x = "01000"
    elif x == "01000":
        x = "00100"
    elif x == "00100":
        x = "00010"
    elif x == "00010":
        x = "00000"
while True:
    Frame()
    xman()
        