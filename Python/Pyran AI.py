print("PyranAI")
print("Initializing...")
import random
import wikipedia
import os

os.system('cls')
print('Starting Pyran AI')
os.system('cls')
print('Pyran AI v1.0.0')
print('Searches Wikipedia for most relevant searches')
print()
def get_response(user_input):
    """Searches Wikipedia for relevant information and returns a summary."""
    try:
        summary = wikipedia.summary(user_input, sentences=2)
        return f"According to Wikipedia, {summary}"
    except wikipedia.exceptions.PageError:
        return f"I couldn't find any information about \"{user_input}\" on Wikipedia."

while True:
    user_input = input("You: ")
    if user_input.lower() == "quit":
        break
    response = get_response(user_input)
    print("PyranAI:", response)
