from shiny import App, ui, reactive
import os
from datetime import date  # Import to get today's date

UPLOAD_FOLDER = "uploads"
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
        selected_option = input.radio()  # Get the selected radio button value
        selected_date = input.date1()    # Get the selected date
        
        if uploaded_file is None:
            output.status.set("No file uploaded!")
            return
        
        # Save uploaded file
        file_path = os.path.join(UPLOAD_FOLDER, uploaded_file["name"])
        with open(file_path, "wb") as f:
            f.write(uploaded_file["datapath"].read_bytes())
        
        # Display the form data
        output.status.set(
            f"File saved: {file_path}\n"
            f"Date: {selected_date}\n"
            f"Technician: {input.technician()}\n"
            f"Description: {input.description()}\n"
            f"Selected Option: {selected_option}"
        )

# Run the App
app = App(app_ui, server)