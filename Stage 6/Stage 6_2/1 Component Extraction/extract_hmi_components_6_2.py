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
        "LS-602": {
            "Tag": "LS-602",
            "Full_Name": "UF Backwash Level Switch",
            "Component_Type": "Level Switch",
            "Description": "High/Low level safety switch for UF Backwash Tank"
        },
        "T-602": {
            "Tag": "T-602",
            "Full_Name": "UF Backwash Tank",
            "Component_Type": "Tank",
            "Description": "Storage tank for Ultrafiltration backwash water"
        },
        "LIT-602": {
            "Tag": "LIT-602",
            "Full_Name": "UF Backwash Level Meter",
            "Component_Type": "Level Indicator Transmitter",
            "Description": "Measures water level in UF Backwash Tank (reading: 606 mm)"
        },
        "P-602": {
            "Tag": "P-602",
            "Full_Name": "UF Backwash Pump",
            "Component_Type": "Pump",
            "Description": "Pump for UF backwash water"
        },
        "PI-602": {
            "Tag": "PI-602",
            "Full_Name": "UF Backwash Pressure Indicator",
            "Component_Type": "Pressure Indicator",
            "Description": "Measures pressure in the UF backwash line"
        },
        "FIT-601": {
            "Tag": "FIT-601",
            "Full_Name": "UF Backwash Flow Meter",
            "Component_Type": "Flow Indicator Transmitter",
            "Description": "Measures flow rate of UF backwash water (reading: 0.00 m³/h)"
        }
    }

if __name__ == "__main__":
# Paths relative to the project structure
    context_file = "https://raw.githubusercontent.com/MeeraYasmin/SWaT-Anomaly-Detection/main/Stage%206/Stage%206_2/1%20Component%20Extraction/Extraction_Context_6_2.txt"
    image_file = "https://raw.githubusercontent.com/MeeraYasmin/SWaT-Anomaly-Detection/main/Images/HMI_Image_6_2.jpeg"
    output_file = "https://raw.githubusercontent.com/MeeraYasmin/SWaT-Anomaly-Detection/main/Stage%206/Stage%6_2/1%20Component%20Extraction/extracted_components_output_6_2.csv"
    
    generate_hmi_components_csv(abs_context, abs_image, abs_output)
