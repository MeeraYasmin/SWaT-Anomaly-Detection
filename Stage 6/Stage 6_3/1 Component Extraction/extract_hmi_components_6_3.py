import pandas as pd
import os

def generate_hmi_components_csv(output_csv, components):
    """
    Generates a CSV of HMI components for Stage 6 including readings.
    """
    print(f"Generating CSV with {len(components)} components for {os.path.basename(output_csv)}...")
    df = pd.DataFrame(components)
    
    # Ensure the directory exists
    os.makedirs(os.path.dirname(output_csv), exist_ok=True)
    
    df.to_csv(output_csv, index=False)
    print(f"Success! CSV saved to: {output_csv}")

if __name__ == "__main__":
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

    # List of components for HMI 3
    hmi_3_tags = ["LS-603", "T-603", "P-603", "PI-601_HMI3", "PI-602_HMI3", "FI-601"]

    # Local directory for output
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Generate the output CSV file
    generate_hmi_components_csv(
        os.path.join(base_dir, "extracted_components_output_6_3.csv"),
        [component_data[tag] for tag in hmi_3_tags]
    )
