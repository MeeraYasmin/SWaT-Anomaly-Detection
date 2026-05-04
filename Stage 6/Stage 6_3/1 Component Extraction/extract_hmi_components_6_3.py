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
    if context_path.startswith("http"):
        response = requests.get(context_path)
        if response.status_code != 200:
            print("Error: Unable to fetch context file.")
            return
        context = response.text
    else:
        if not os.path.exists(context_path):
        print(f"Error: {context_path} not found.")
        return

    with open(context_path, 'r', encoding='utf-8') as f:
        context = f.read()
    """
    Generates a CSV of HMI components for Stage 6 including readings.
    """
    print(f"Generating CSV with {len(components)} components for {os.path.basename(output_csv)}...")
    df = pd.DataFrame(components)
    
    # Ensure the directory exists
    os.makedirs(os.path.dirname(output_csv), exist_ok=True)
    
    df.to_csv(output_csv, index=False)
    print(f"Success! CSV saved to: {output_csv}")

    # Define the component data based on labels and readings from HMI_Image_6.jpeg
    component_data = {
        "LS-603": {
            "Tag": "LS-603",
            "Full_Name": "RO / UF CIP Level Switch",
            "Component_Type": "Level Switch",
            "Description": "Level switch for the CIP (Clean-In-Place) Tank"
        },
        "T-603": {
            "Tag": "T-603",
            "Full_Name": "CIP Tank",
            "Component_Type": "Tank",
            "Description": "Storage tank for CIP cleaning chemicals"
        },
        "P-603": {
            "Tag": "P-603",
            "Full_Name": "CIP Pump",
            "Component_Type": "Pump",
            "Description": "Pump for CIP cleaning process"
        },
        "PI-601_HMI3": {
            "Tag": "PI-601",
            "Full_Name": "RO / UF CIP Pressure 1",
            "Component_Type": "Pressure Indicator",
            "Description": "Pressure indicator 1 for the CIP distribution line"
        },
        "PI-602_HMI3": {
            "Tag": "PI-602",
            "Full_Name": "RO / UF CIP Pressure 2",
            "Component_Type": "Pressure Indicator",
            "Description": "Pressure indicator 2 for the CIP distribution line"
        },
        "FI-601": {
            "Tag": "FI-601",
            "Full_Name": "RO/UF CIP Rotameter",
            "Component_Type": "Flow Indicator",
            "Description": "Visual flow rotameter for the CIP process"
        }
    }

if __name__ == "__main__":
    # Paths relative to the project structure
    context_file = "https://raw.githubusercontent.com/MeeraYasmin/SWaT-Anomaly-Detection/main/Stage%206/Stage%206_3/1%20Component%20Extraction/Extraction_Context_6_3.txt"
    image_file = "https://raw.githubusercontent.com/MeeraYasmin/SWaT-Anomaly-Detection/main/Images/HMI_Image_6_3.jpeg"
    output_file = "https://raw.githubusercontent.com/MeeraYasmin/SWaT-Anomaly-Detection/main/Stage%206/Stage%206_3/1%20Component%20Extraction/extracted_components_output_6_3.csv"
    
    generate_hmi_components_csv(abs_context, abs_image, abs_output)
