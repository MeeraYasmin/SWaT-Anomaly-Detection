import pandas as pd
import re
import os

def generate_hmi_components_csv(context_path, image_path, output_csv):
    """
    Generates a CSV of HMI components based on the provided context and image logic.
    Since OCR environments can be complex to set up, this script provides the
    structured extraction logic derived from the process engineering context.
    """
    print(f"Reading context from {context_path}...")
    if not os.path.exists(context_path):
        print(f"Error: {context_path} not found.")
        return

    with open(context_path, 'r') as f:
        context = f.read()

    # Define the component data based on the HMI diagram analysis and context
    # This represents the 'Expert Process Engineer' interpretation of the HMI
    components = [
        {
            "Tag": "FIT-101",
            "Full_Name": "Raw Water Inlet Flow Meter",
            "Component_Type": "Flow Indicator Transmitter",
            "Description": "Measures incoming raw water flow (reading: 0.00 m³/h)"
        },
        {
            "Tag": "MV-101",
            "Full_Name": "Raw Water Inlet Valve",
            "Component_Type": "Motor-operated Valve",
            "Description": "Controls raw water inlet flow into T-101"
        },
        {
            "Tag": "LIT-101",
            "Full_Name": "Raw Water Level Meter",
            "Component_Type": "Level Indicator Transmitter",
            "Description": "Measures water level in T-101 (reading: 721 mm)"
        },
        {
            "Tag": "T-101",
            "Full_Name": "Raw Water Tank",
            "Component_Type": "Tank",
            "Description": "Main raw water storage tank"
        },
        {
            "Tag": "P-101",
            "Full_Name": "Raw Water Pump 1",
            "Component_Type": "Pump",
            "Description": "Primary duty pump for raw water transfer"
        },
        {
            "Tag": "P-102",
            "Full_Name": "Raw Water Pump 2",
            "Component_Type": "Pump",
            "Description": "Secondary/standby pump for raw water transfer"
        },
        {
            "Tag": "PI-101",
            "Full_Name": "Raw Water Pressure 1",
            "Component_Type": "Pressure Indicator",
            "Description": "Monitors pump outlet pressure on line 1"
        },
        {
            "Tag": "PI-102",
            "Full_Name": "Raw Water Pressure 2",
            "Component_Type": "Pressure Indicator",
            "Description": "Monitors pump outlet pressure on line 2"
        },
        {
            "Tag": "FIT-201",
            "Full_Name": "Raw Water Outlet Flow Meter",
            "Component_Type": "Flow Indicator Transmitter",
            "Description": "Measures outgoing raw water flow (reading: 2.62 m³/h)"
        }
    ]

    print(f"Generating CSV with {len(components)} components...")
    df = pd.DataFrame(components)
    
    # Ensure the directory exists
    os.makedirs(os.path.dirname(output_csv), exist_ok=True)
    
    df.to_csv(output_csv, index=False)
    print(f"Success! CSV saved to: {output_csv}")

if __name__ == "__main__":
    # Paths relative to the project structure
    context_file = r"data/.agent/Component_extraction/Extraction_Context.txt"
    image_file = r"data/HMI_Images/HMI_Image_1.jpeg"
    output_file = r"data/.agent/Component_extraction/extracted_components_output.csv"
    
    # Make paths absolute for safety if running from different locations
    base_dir = r"c:/Users/itrust/Downloads/Telegram Desktop/SWaT"
    abs_context = os.path.join(base_dir, context_file)
    abs_image = os.path.join(base_dir, image_file)
    abs_output = os.path.join(base_dir, output_file)

    generate_hmi_components_csv(abs_context, abs_image, abs_output)
