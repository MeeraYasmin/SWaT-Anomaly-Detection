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

    # List of components for HMI 1
    hmi_1_tags = ["LS-601", "T-601", "LIT-601", "P-601", "PI-601", "FIT-602"]

    # Local directory for output
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Generate the output CSV file
    generate_hmi_components_csv(
        os.path.join(base_dir, "extracted_components_output_6_1.csv"),
        [component_data[tag] for tag in hmi_1_tags]
    )
