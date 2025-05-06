from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
import joblib
import pandas as pd

# Sample data (replace with actual data)
data = {
    'from_city': ['CityA', 'CityB', 'CityC', 'CityA'], 
    'to_city': ['CityB', 'CityC', 'CityA', 'CityD'],
    'weight': [500, 700, 300, 600],
    'shipping_class': [1, 2, 1, 2],
    'distance': [300, 400, 350, 500],
    'weather': [1.0, 1.5, 2.0, 1.2],
    'traffic_factor': [1.2, 1.0, 1.3, 1.1],
    'ETA': [5.5, 6.0, 4.5, 7.0]  # Target variable (hours)
}

df = pd.DataFrame(data)

# Load the LabelEncoder
le = joblib.load('models/label_encoder.pkl')

# Convert categorical cities to numerical using LabelEncoder
df['from_city'] = le.transform(df['from_city'])
df['to_city'] = le.transform(df['to_city'])

# Features (X) and target variable (y)
X = df[['from_city', 'to_city', 'weight', 'shipping_class', 'distance', 'weather', 'traffic_factor']]
y = df['ETA']

# Split data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train a Random Forest Regressor model for ETA prediction
eta_model = RandomForestRegressor()
eta_model.fit(X_train, y_train)

# Save the trained ETA model
joblib.dump(eta_model, 'models/eta_model.pkl')

print("ETA model saved successfully!")
