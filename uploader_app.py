from shiny import App, ui, reactive
import os
import shutil

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app_ui = ui.page_fluid(
    ui.h2("Upload Image and Provide Metadata"),
    ui.input_file("file_input", "Upload an Image", accept=["image/*"]),
    ui.input_text("text_field", "Enter a Description"),
    ui.input_action_button("submit", "Submit"),
    ui.output_text("status"),
)

def server(input, output, session):
    @reactive.Effect
    @reactive.event(input.submit)
    def handle_upload():
        uploaded_file = input.file_input()
        if uploaded_file is None:
            output.status.set("No file uploaded!")
            return

        # Save the uploaded file
        file_path = os.path.join(UPLOAD_FOLDER, uploaded_file["name"])
        with open(file_path, "wb") as f:
            shutil.copyfileobj(uploaded_file["datapath"], f)

        # Save metadata
        description = input.text_field().strip()
        if not description:
            output.status.set("Description cannot be empty!")
            return

        metadata_path = os.path.join(UPLOAD_FOLDER, "metadata.txt")
        with open(metadata_path, "a") as metadata_file:
            metadata_file.write(f"{uploaded_file['name']}: {description}\n")

        output.status.set(f"File uploaded and metadata saved!")

app = App(app_ui, server)

