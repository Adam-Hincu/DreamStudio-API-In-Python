import PySimpleGUI as sg
import getpass
import io
import os
from IPython.display import display
from PIL import Image
from stability_sdk import client
import stability_sdk.interfaces.gooseai.generation.generation_pb2 as generation

# Define your API key here or enter it in the window
API_KEY = ""

# Define the layout of the window
layout = [
    [sg.Text("Enter your Stability AI API key here:")],
    [sg.Input(key="-KEY-", default_text=API_KEY)],
    [sg.Text("Enter your prompt here:")],
    [sg.Input(key="-PROMPT-")],
    [sg.Button("Generate")],
]

# Create the window
window = sg.Window("Stability AI", layout)

# Event loop
while True:
    event, values = window.read()
    # If user closes window or clicks cancel
    if event == sg.WINDOW_CLOSED:
        break
    # If user clicks generate button
    if event == "Generate":
        # Get the API key from the input field or the variable above
        API_KEY = values["-KEY-"] or API_KEY 
        # Get the prompt from the input field
        prompt = values["-PROMPT-"]
        # Create a client object for Stability AI with your API key and host url 
        stability_api = client.StabilityInference(
            key=API_KEY,
            host="grpc.stability.ai:443",
            verbose=True,
        )
        # Call the generate method with your prompt and other parameters (such as seed and steps)
        answers = stability_api.generate(
            prompt=prompt,
            seed=34567,
            steps=20,
        )
        # Iterate over the generator to get the response objects 
        for resp in answers:
            for artifact in resp.artifacts:
                if artifact.finish_reason == generation.FILTER:
                    warnings.warn(
                        "Your request activated the API's safety filters and could not be processed."
                        "Please modify the prompt and try again.")
                if artifact.type == generation.ARTIFACT_IMAGE:
                    img = Image.open(io.BytesIO(artifact.binary))
                    # Convert image object to byte array using io.BytesIO and getvalue 
                    img_bytes = io.BytesIO()
                    img.save(img_bytes, format='PNG')
                    img_bytes = img_bytes.getvalue()
                    # Create an image element with the byte array 
                    image_element = sg.Image(data=img_bytes)
                    # Add it to a new layout 
                    image_layout = [[image_element], [sg.Button('Save Image')]]
                    # Create a new window with this layout 
                    image_window = sg.Window(f"Image:", image_layout)
                    # Read events from this window until closed 
                    while True:
                        event, values = image_window.read()
                        if event == sg.WINDOW_CLOSED:
                            break
                        elif event == 'Save Image':
                            # Get the directory path to save the image
                            save_path = sg.popup_get_folder("Select folder to save image")
                            if save_path:
                                # Save the image to the specified directory
                                file_name = os.path.join(save_path, "generated_image.png")
                                with open(file_name, "wb") as f:
                                    f.write(img_bytes)
                                sg.popup(f"Image saved to {save_path}")
                    # Close this window 
                    image_window.close()

# Close the main window                    
window.close()
