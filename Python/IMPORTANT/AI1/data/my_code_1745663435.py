import numpy as np
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt

# Simple dataset
X = np.array([1, 2, 3, 4, 5]).reshape(-1, 1)  # Features
y = np.array([1, 2, 3, 4, 5])  # Target values (y = X)

# Train the model
model = LinearRegression()
model.fit(X, y)

# Make predictions
y_pred = model.predict(X)

# Plot results
plt.scatter(X, y, color='blue', label='Actual values')
plt.plot(X, y_pred, color='red', label='Fitted line')
plt.legend()
plt.show()