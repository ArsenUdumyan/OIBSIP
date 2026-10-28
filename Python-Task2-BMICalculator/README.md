# BMI Calculator

A desktop BMI calculator built with Python and tkinter. It calculates BMI, shows a colour-coded result, saves records for different users in a local database, and draws a trend chart of each user's BMI over time.

## Features

- Enter weight (kg) and height (m) in a GUI window with a Calculate button
- BMI calculated as weight / height², rounded to 2 decimal places
- Category shown with colour coding: Underweight (blue), Normal (green), Overweight (orange), Obese (red)
- Input validation: rejects non-numeric, zero, negative and unrealistic height values
- Multi-user support: save records under a user's name
- Records stored in a local SQLite database
- Trend graph of a user's BMI over time, made with matplotlib
- Database errors are caught and shown as a message in the window

## BMI Categories

| BMI | Category |
|-----|----------|
| Below 18.5 | Underweight |
| 18.5 to 24.9 | Normal |
| 25 to 29.9 | Overweight |
| 30 and above | Obese |

## Tech Stack

- Python 3.12
- tkinter (GUI)
- sqlite3 (database)
- matplotlib (charts)

## How to Run

1. Create a virtual environment: `py -3.12 -m venv venv`
2. Activate it: `venv\Scripts\activate`
3. Install the libraries: `pip install -r requirements.txt`
4. Start the app: `python bmi.py`

## How to Use

1. Type a name, weight and height.
2. Click **Calculate** to see the BMI and category.
3. Click **Save Result** to store the record under that name.
4. After saving at least two records for a name, click **Show Trend Graph**.

## Data Storage

Records (name, weight, height, BMI, category and date) are saved in a local file called `bmi_data.db` on your own computer. No data is sent anywhere else.

