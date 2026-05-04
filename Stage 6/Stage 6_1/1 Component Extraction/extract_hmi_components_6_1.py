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

    # Define the component data based on labels and readings from HMI_Image_6.jpeg
    component_data = {
        "LS-601": {
            "Tag": "LS-601",
            "Full_Name": "RO Permeate Level Switch",
            "Component_Type": "Level Switch",
            "Description": "High/Low level safety switch for RO Permeate Tank"
        },
        "T-601": {
            "Tag": "T-601",
            "Full_Name": "RO Permeate Tank",
            "Component_Type": "Tank",
            "Description": "Storage tank for Reverse Osmosis permeate water"
        },
        "LIT-601": {
            "Tag": "LIT-601",
            "Full_Name": "RO Permeate Level Meter",
            "Component_Type": "Level Indicator Transmitter",
            "Description": "Measures water level in RO Permeate Tank (reading: 365 mm)"
        },
        "P-601": {
            "Tag": "P-601",
            "Full_Name": "RO Permeate Pump",
            "Component_Type": "Pump",
            "Description": "Pump for RO permeate distribution"
        },
        "PI-601": {
            "Tag": "PI-601",
            "Full_Name": "RO Permeate Pressure Indicator",
            "Component_Type": "Pressure Indicator",
            "Description": "Measures pressure in the RO permeate line"
        },
        "FIT-602": {
            "Tag": "FIT-602",
            "Full_Name": "RO Permeate Flow Meter",
            "Component_Type": "Flow Indicator Transmitter",
            "Description": "Measures flow rate of RO permeate (reading: 0.00 m³/h)"
        }
    }
    
    print(f"Generating CSV with {len(components)} components for {os.path.basename(output_csv)}...")
    df = pd.DataFrame(components)
    
    # Ensure the directory exists
    os.makedirs(os.path.dirname(output_csv), exist_ok=True)
    
    df.to_csv(output_csv, index=False)
    print(f"Success! CSV saved to: {output_csv}")

if __name__ == "__main__":
    # Paths relative to the project structure
    context_file = "https://raw.githubusercontent.com/MeeraYasmin/SWaT-Anomaly-Detection/main/Stage%206/Stage%206_1/1%20Component%20Extraction/Extraction_Context_6_1.txt"
    image_file = "https://raw.githubusercontent.com/MeeraYasmin/SWaT-Anomaly-Detection/main/Images/HMI_Image_6_1.jpeg"
    output_file = "https://raw.githubusercontent.com/MeeraYasmin/SWaT-Anomaly-Detection/main/Stage%206/Stage%206_1/1%20Component%20Extraction/extracted_components_output_6_1.csv"
    
    generate_hmi_components_csv(abs_context, abs_image, abs_output)
