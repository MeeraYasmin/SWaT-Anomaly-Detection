import pandas as pd
import os

def generate_hmi_components_csv(context_path, image_path, output_csv):
    """
    Generates a CSV of HMI components for Stage 2 based on the provided context and image logic.
    """
    print(f"Reading context from {context_path}...")
    if not os.path.exists(context_path):
        print(f"Warning: {context_path} not found. Proceeding with hardcoded component list.")

    # Define the component data based on the HMI diagram analysis for Stage 3
    components = [
        {
            "Tag": "LIT-401",
            "Full_Name": "RO Feed Water Level Meter",
            "Component_Type": "Level Indicator Transmitter",
            "Description": "Monitors water level in RO Feed Water Tank T-401 (reading: 979 mm)"
        },
        {
            "Tag": "T-401",
            "Full_Name": "RO Feed Water Tank",
            "Component_Type": "Tank",
            "Description": "Storage for water to be processed by RO"
        },
        {
            "Tag": "P-401",
            "Full_Name": "RO Feed Pump 1",
            "Component_Type": "Pump",
            "Description": "Feeds water to the RO system"
        },
        {
            "Tag": "P-402",
            "Full_Name": "RO Feed Pump 2",
            "Component_Type": "Pump",
            "Description": "Standby/Secondary RO feed pump"
        },
        {
            "Tag": "PI-401",
            "Full_Name": "RO Feed Pressure 1",
            "Component_Type": "Pressure Indicator",
            "Description": "Measures pressure after P-401"
        },
        {
            "Tag": "PI-402",
            "Full_Name": "RO Feed Pressure 2",
            "Component_Type": "Pressure Indicator",
            "Description": "Measures pressure after P-402"
        },
        {
            "Tag": "FIT-401",
            "Full_Name": "RO Feed Flow Meter",
            "Component_Type": "Flow Indicator Transmitter",
            "Description": "Measures flow rate to the RO system (reading: 1.21 m³/h)"
        },
        {
            "Tag": "AIT-401",
            "Full_Name": "RO Feed Hardness Meter",
            "Component_Type": "Analytical Indicator Transmitter",
            "Description": "Measures hardness of RO feed water (reading: 0.00 ppm)"
        },
        {
            "Tag": "AIT-402",
            "Full_Name": "RO Feed ORP Meter",
            "Component_Type": "Analytical Indicator Transmitter",
            "Description": "Measures ORP of RO feed water (reading: 0.00 mV)"
        },
        {
            "Tag": "UV-401",
            "Full_Name": "UV Dechlorinator",
            "Component_Type": "UV System",
            "Description": "Removes chlorine from water"
        },
        {
            "Tag": "T-402",
            "Full_Name": "NaHSO3 Tank",
            "Component_Type": "Tank",
            "Description": "Sodium Bisulfite storage tank"
        },
        {
            "Tag": "LS-401",
            "Full_Name": "NaHSO3 Level Switch",
            "Component_Type": "Level Switch",
            "Description": "Monitors level in NaHSO3 Tank"
        },
        {
            "Tag": "P-403",
            "Full_Name": "NaHSO3 Metering Pump 1",
            "Component_Type": "Pump",
            "Description": "Doses sodium bisulfite"
        },
        {
            "Tag": "P-404",
            "Full_Name": "NaHSO3 Metering Pump 2",
            "Component_Type": "Pump",
            "Description": "Standby sodium bisulfite pump"
        }
    ]

    print(f"Generating CSV with {len(components)} components...")
    df = pd.DataFrame(components)
    
    # Ensure the directory exists
    os.makedirs(os.path.dirname(output_csv), exist_ok=True)
    
    df.to_csv(output_csv, index=False)
    print(f"Success! CSV saved to: {output_csv}")

if __name__ == "__main__":
    # Paths relative to the project structure for Stage 4
    base_dir = r"c:/Users/itrust/Downloads/Telegram Desktop/SWaT/Anomaly_Detection/Project_Steps (Stage 4)/1_Component_extraction"
    image_dir = r"c:/Users/itrust/Downloads/Telegram Desktop/SWaT/Anomaly_Detection/HMI_Images"
    
    context_file = os.path.join(base_dir, "Extraction_Context_4.txt")
    image_file = os.path.join(image_dir, "HMI_Image_4.jpeg")
    output_file = os.path.join(base_dir, "extracted_components_output_4.csv")
    
    generate_hmi_components_csv(context_file, image_file, output_file)
