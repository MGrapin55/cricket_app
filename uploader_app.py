from shiny import App, ui, reactive
import os
from datetime import date  # Import to get today's date

UPLOAD_FOLDER = "uploads"
CSV_FILE = "submissions.csv"  # Define the path to the CSV file
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Define UI
app_ui = ui.page_fluid(
    ui.h2("Upload Image and Provide Metadata"),
    ui.input_radio_buttons(
        "radio",  # Input ID for the radio button
        "Select an Population",  # Label for the radio button
        {"1": "Cape May", "2": "Clearfield", "3": "Ithaca", "4": "etc"}  # Options
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
    ui.output_text("status"),
)

# Define Server
def server(input, output, session):
    @reactive.Effect
    @reactive.event(input.submit)
    def handle_upload():
        uploaded_file = input.file_input()
        selected_option = input.radio()
        selected_date = input.date1()
        technician = input.technician()
        description = input.description()
        
        if uploaded_file is None:
            output.status.set("No file uploaded!")
            return
        
        # Save the uploaded file
        file_path = os.path.join(UPLOAD_FOLDER, uploaded_file["name"])
        with open(file_path, "wb") as f:
            f.write(uploaded_file["datapath"].read_bytes())
        
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

        # Update the status output
        output.status.set(
            f"File saved: {file_path}\n"
            f"Date: {selected_date}\n"
            f"Technician: {technician}\n"
            f"Description: {description}\n"
            f"Selected Option: {selected_option}\n"
            f"Submission saved to {CSV_FILE}"
        )

# Run the App
app = App(app_ui, server)