print("VTax v 2.0")
print("")
print("Enter all your bills, then type 'done' to enter the tax rate.")
print("Do not include '%' in the tax rate.")
print("Bills can contain decimals.")
print("")

bill = 0
total_bill = 0
while True:
  bill = input("Bill = ")
  if bill.lower() == 'done':
    break
  
  total_bill += float(bill)
  



tax_rate = float(input("Tax rate = "))
tax_amount = (total_bill * tax_rate) / 100
total_amount = tax_amount + total_bill

print("Total bill: {:.2f}".format(total_bill))
print("Tax amount: {:.2f}".format(tax_amount))
print("Total amount to pay: {:.2f}".format(total_amount))