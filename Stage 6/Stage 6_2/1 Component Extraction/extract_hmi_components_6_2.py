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

    # List of components for HMI 2
    hmi_2_tags = ["LS-602", "T-602", "LIT-602", "P-602", "PI-602", "FIT-601"]

    # Local directory for output
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Generate the output CSV file
    generate_hmi_components_csv(
        os.path.join(base_dir, "extracted_components_output_6_2.csv"),
        [component_data[tag] for tag in hmi_2_tags]
    )
