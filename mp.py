from flask import Flask, render_template, request
import pandas as pd
import os

UPLOAD_FOLDER = 'C:\\Users\\user\\Downloads\\trails from gpt1\\trails from gpt'

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Columns to display in the selected row
selected_columns = ['Sloka_Number', 'Sloka', 'Sloka_Translation']

# Index variable to keep track of the current row
current_row_index = 0
df = None
filename = None

@app.route('/')
def index():
    global current_row_index, df
    # Check if the DataFrame is None
    if df is None:
        return render_template('error.html', message='No file uploaded')
    # Check if the current row index is out of bounds
    if current_row_index < 0 or current_row_index >= len(df):
        return render_template('error.html', message='Invalid row index')
    # Get the row based on the current index
    row = df.iloc[current_row_index][selected_columns]
    return render_template('index.html', row=row, filename=filename)
    
@app.route('/next')
def next_row():
    global current_row_index, df
    # Increment the current index to move to the next row
    current_row_index += 1
    # Wrap around to the first row if the end is reached
    if current_row_index >= len(df):
        current_row_index = 0
    return index()

@app.route('/previous')
def previous_row():
    global current_row_index, df
    # Decrement the current index to move to the previous row
    current_row_index -= 1
    # Wrap around to the last row if the beginning is reached
    if current_row_index < 0:
        current_row_index = len(df) - 1
    return index()

@app.route('/save', methods=['POST'])
def save():
    global df
    # Get the selected options from the checkboxes
    selected_options = []
    for option in range(1, 34):
        option_name = f'option{option}'
        if option_name in request.form:
            selected_options.append(option_name)

    # Get the target column where the selected options should be saved
    target_column = 'Label'  # Replace with your desired target column name

    # Update the corresponding cell in the target column for the current row
    df.at[current_row_index, target_column] = ', '.join(selected_options)

    # Save the modified DataFrame back to the Excel sheet
    df.to_excel(os.path.join(app.config['UPLOAD_FOLDER'], filename), index=False)
    return index()

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    global df, filename, current_row_index
    if request.method == 'POST':
        file = request.files['file']
        if file:
            filename = file.filename
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            df = pd.read_excel(file_path)
            current_row_index = 0
            return index()
    return render_template('upload.html')

if __name__ == '__main__':
    app.run(debug=True)