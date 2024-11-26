from shiny import App, ui, reactive
import os
import pandas as pd  # Import pandas for handling the CSV
from datetime import date  # Import to get today's date

UPLOAD_FOLDER = "uploads"
CSV_FILE = "uploads/submissions.csv"  # Define the path to the CSV file
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Define UI
app_ui = ui.page_fluid(
    ui.h2("Upload Image and Provide Metadata"),
    ui.input_radio_buttons(
        "radio",  # Input ID for the radio button
        "Select a Population",  # Label for the radio button
        {"CM": "Cape May", "C": "Clearfield", "I": "Ithaca", "E": "etc"}  # Options
    ),
    ui.input_date(
        "date1",
        "Select a Date:",
        value=str(date.today()),  # Default date set to today's date
        min="2024-01-01",         # Minimum date allowed
        max="2030-12-31",         # Maximum date allowed
        autoclose=False           # Keep the calendar open after a selection
    ),
    ui.input_text("technician", "Research Technician Initials"),
    ui.input_text("description", "Enter a Description"),
    ui.input_file("file_input", "Upload an Image", accept=["image/*"], multiple=False),
    ui.input_action_button("submit", "Submit"),
)

# Define Server
def server(input, output, session):
    @reactive.Effect
    @reactive.event(input.submit)
    def handle_upload():
        uploaded_file = input.file_input()

        if uploaded_file is None:
            print("No file uploaded!")  # Print an error message
            return

        # Handle the uploaded file (Shiny file input is a dictionary)
        file_info = uploaded_file[0]  # Access the first (and only) file
        file_name = file_info["name"]
        file_data = file_info["datapath"]  # Temporary file path

        # Save the file to the upload folder
        file_path = os.path.join(UPLOAD_FOLDER, file_name)
        with open(file_data, "rb") as source_file:
            with open(file_path, "wb") as destination_file:
                destination_file.write(source_file.read())

        # Get additional metadata from the user inputs
        selected_option = input.radio()
        selected_date = input.date1()
        technician = input.technician()
        description = input.description()

        # Create a DataFrame for the new entry
        new_entry = pd.DataFrame([{
            "File Path": file_path,
            "Date": selected_date,
            "Technician": technician,
            "Description": description,
            "Selected Option": selected_option
        }])

        # Check if the CSV file exists
        if os.path.exists(CSV_FILE):
            # Load the existing CSV file
            existing_data = pd.read_csv(CSV_FILE)
            # Append the new entry
            updated_data = pd.concat([existing_data, new_entry], ignore_index=True)
        else:
            # Start with the new entry if the file doesn't exist
            updated_data = new_entry

        # Save the updated DataFrame to the CSV file
        updated_data.to_csv(CSV_FILE, index=False)

        # Print a thank you message
        print("Thank you for the data!")

# Run the App
app = App(app_ui, server)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)