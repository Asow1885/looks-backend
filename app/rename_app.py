import os

# Path to the app.py file
file_path = 'C:/Users/asow1/logistics-finance-ai/app/app.py.py'

# Check if the file with .py.py extension exists
if os.path.exists(file_path):
    # Rename the file to app.py
    new_file_path = 'C:/Users/asow1/logistics-finance-ai/app/app.py'
    os.rename(file_path, new_file_path)
    print(f"File renamed to {new_file_path}")
else:
    print("File app.py.py not found!")
