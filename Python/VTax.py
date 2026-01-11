print("VTax v 1.0 ")
print("")
print("enter all your bills so that they get added up and then type 'b'in the bill slot to enter the tax rate , then it will output then money need to pay , do not include '%'in the tax rate , it dosent include the currency , bills can contain decimals.")
print("")
b = 0
while b == 1:
    set = bill
    bill = ((input("bill = ")))
    if bill == b:
     b = 1
     taxrate = float(input("tax rate = "))

    else:
     bill = set + bill
    