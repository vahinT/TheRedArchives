import math

def calculate(operation, num1, num2):
    """Performs the specified calculation."""
    if operation == "+":
        return num1 + num2
    elif operation == "-":
        return num1 - num2
    elif operation == "*":
        return num1 * num2
    elif operation == "/":
        if num2 == 0:
            raise  
 ValueError("Cannot divide by zero.")   

        return num1 / num2
    elif operation == "^":
        return math.pow(num1, num2)
    else:
        raise ValueError("Invalid operation.")

def get_input(prompt):
    """Gets user input with error handling."""
    while True:
        try:
            return float(input(prompt))
        except ValueError:
            print("Invalid input. Please enter a number.")

def main():
    print("Welcome to the Interactive Calculator!")
    print("Available operations: +, -, *, /, ^")

    while True:
        operation = input("Enter the operation: ")
        num1 = get_input("Enter the first number: ")
        num2 = get_input("Enter the second number: ")

        try:
            result = calculate(operation, num1, num2)
            print(f"Result: {result}")
        except ValueError as e:
            print(f"Error: {e}")

        if input("Do you want to continue? (y/n): ").lower() != "y":
            break

if __name__ == "__main__":
    main()
