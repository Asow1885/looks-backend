from sklearn.preprocessing import LabelEncoder
import joblib

# Example cities (replace with actual cities you use)
cities = ['CityA', 'CityB', 'CityC', 'CityD']  # Add all the cities you want

# Initialize the LabelEncoder
le = LabelEncoder()

# Fit the encoder on the list of cities
le.fit(cities)

# Save the label encoder as a .pkl file in the 'models' folder
joblib.dump(le, 'models/label_encoder.pkl')

print("Label Encoder saved successfully!")
