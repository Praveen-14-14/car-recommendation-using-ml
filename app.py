import pandas as pd
from flask import Flask, render_template, request

app = Flask(__name__)

# Load the CSV file into a DataFrame
try:
    df = pd.read_csv('car.csv')
except FileNotFoundError:
    print("The file 'car.csv' was not found.")
    exit()
except Exception as e:
    print(f"An error occurred while loading the CSV file: {e}")
    exit()

# Ensure relevant columns are present
required_columns = ['budget', 'dailycommute', 'roadcondition', 'recommendation']
missing_columns = [column for column in required_columns if column not in df.columns]
if missing_columns:
    print(f"The following required columns are missing in the CSV file: {', '.join(missing_columns)}")
    exit()

# Fill NaN values appropriately and ensure correct data types
for column in required_columns:
    if df[column].isnull().any():
        if column in ['budget', 'dailycommute']:
            df[column] = df[column].fillna(0)
        else:
            df[column] = df[column].fillna('Unknown')

def recommend_cars(budget, daily_commute, road_condition):
    # Filter DataFrame based on road condition suitability
    suitable_cars = df[df['roadcondition'].str.lower() == road_condition.lower()]
    
    if suitable_cars.empty:
        return []

    # Find the closest match based on budget and daily commute
    closest_cars = suitable_cars.iloc[(suitable_cars['budget'] - int(budget)).abs().argsort()[:3]]
    
    return closest_cars['recommendation'].tolist()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/recommend', methods=['POST'])
def recommend():
    budget = request.form['budget']
    daily_commute = request.form['daily_commute']
    road_condition = request.form['road_condition']

    recommendations = recommend_cars(budget, daily_commute, road_condition)
    
    if not recommendations:
        return render_template('no_results.html')
    else:
        return render_template('result.html', recommendations=recommendations)

if __name__ == "__main__":
    app.run(debug=True)
