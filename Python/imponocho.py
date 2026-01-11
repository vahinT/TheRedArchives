import torch
import torch.nn as nn
import tkinter as tk
from tkinter import filedialog

# Define the simple model (ensure it matches the model you're loading)
class SimpleModel(nn.Module):
    def __init__(self):
        super(SimpleModel, self).__init__()
        self.fc1 = nn.Linear(10, 5)
        self.fc2 = nn.Linear(5, 2)

    def forward(self, x):
        x = torch.relu(self.fc1(x))
        x = self.fc2(x)
        return x

# Function to load the model from a .pth file
def load_model(model, model_path):
    model.load_state_dict(torch.load(model_path))
    model.eval()  # Set the model to evaluation mode
    return model

# Function to open file dialog and get the file path
def open_file_dialog():
    root = tk.Tk()
    root.withdraw()  # Hide the root window
    file_path = filedialog.askopenfilename(filetypes=[("PyTorch model files", "*.pth")])
    return file_path

# Main loop for loading and using the model
def model_loader_loop():
    while True:
        # Ask user to choose a model file
        print("Please select a .pth model file.")
        model_path = open_file_dialog()

        if not model_path:
            print("No file selected. Exiting.")
            break  # Exit if no file was selected

        # Initialize the model
        model = SimpleModel()

        try:
            # Load the model
            model = load_model(model, model_path)
            print(f"Model loaded successfully from {model_path}")

            # Example usage: pass a random tensor to the model
            sample_input = torch.randn(1, 10)  # Example input matching the model's input shape
            output = model(sample_input)
            print(f"Model output: {output}")

        except Exception as e:
            print(f"Error loading model: {e}")

        # Ask if the user wants to load another model
        user_input = input("Do you want to load another model? (y/n): ").strip().lower()
        if user_input != 'y':
            print("Exiting model loader.")
            break  # Exit loop if user doesn't want to load another model

# Run the model loader loop
model_loader_loop()
