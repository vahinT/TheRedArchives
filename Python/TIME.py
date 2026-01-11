import datetime

while True:
  current_time = datetime.datetime.now()
  print()
  print("DATE")
  print()
  print(current_time.strftime("%d-%m-%Y"))
  print()
  print("TIME")
  print(current_time.strftime("%H-%M-%S"))
  print(input())
