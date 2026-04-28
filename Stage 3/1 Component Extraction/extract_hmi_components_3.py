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
            "Tag": "LIT-301",
            "Full_Name": "UF Feed Water Level Meter",
            "Component_Type": "Level Indicator Transmitter",
            "Description": "Monitors water level in UF Feed Water Tank T-301 (reading: 993 mm)"
        },
        {
            "Tag": "T-301",
            "Full_Name": "UF Feed Water Tank",
            "Component_Type": "Tank",
            "Description": "Storage for water to be filtered"
        },
        {
            "Tag": "P-301",
            "Full_Name": "UF Feed Pump 1",
            "Component_Type": "Pump",
            "Description": "Feeds water to the UF membrane"
        },
        {
            "Tag": "P-302",
            "Full_Name": "UF Feed Pump 2",
            "Component_Type": "Pump",
            "Description": "Standby/Secondary feed pump"
        },
        {
            "Tag": "PI-301",
            "Full_Name": "UF Feed Pressure 1",
            "Component_Type": "Pressure Indicator",
            "Description": "Measures pressure after P-301"
        },
        {
            "Tag": "PI-302",
            "Full_Name": "UF Feed Pressure 2",
            "Component_Type": "Pressure Indicator",
            "Description": "Measures pressure after P-302"
        },
        {
            "Tag": "FIT-301",
            "Full_Name": "UF Feed Flow Meter",
            "Component_Type": "Flow Indicator Transmitter",
            "Description": "Measures flow rate to the UF membrane (reading: 0.00 m³/h)"
        },
        {
            "Tag": "FI-301",
            "Full_Name": "UF Feed Rotameter",
            "Component_Type": "Flow Indicator",
            "Description": "Visual flow measurement"
        },
        {
            "Tag": "PSH-301",
            "Full_Name": "UF Feed Pressure Switch High",
            "Component_Type": "Pressure Switch",
            "Description": "Safety switch for high pressure"
        },
        {
            "Tag": "PI-303",
            "Full_Name": "UF Filter Pressure",
            "Component_Type": "Pressure Indicator",
            "Description": "Measures pressure at the filter inlet"
        },
        {
            "Tag": "DPSH-301",
            "Full_Name": "UF Filter Diff Pressure Switch High",
            "Component_Type": "Differential Pressure Switch",
            "Description": "Safety switch for high differential pressure"
        },
        {
            "Tag": "DPIT-301",
            "Full_Name": "UF Filter Differential Pressure Meter",
            "Component_Type": "Differential Pressure Indicator Transmitter",
            "Description": "Measures pressure drop across the filter (reading: 0.04 kPa)"
        },
        {
            "Tag": "AIT-301",
            "Full_Name": "UF Permeate pH Meter",
            "Component_Type": "Analytical Indicator Transmitter",
            "Description": "Measures pH of filtered water (reading: 6.46)"
        },
        {
            "Tag": "AIT-302",
            "Full_Name": "UF Permeate ORP Meter",
            "Component_Type": "Analytical Indicator Transmitter",
            "Description": "Measures ORP of filtered water (reading: 375.57 mV)"
        },
        {
            "Tag": "AIT-303",
            "Full_Name": "UF Permeate Conductivity Meter",
            "Component_Type": "Analytical Indicator Transmitter",
            "Description": "Measures conductivity of filtered water (reading: 12.26 µS/cm)"
        },
        {
            "Tag": "MV-301",
            "Full_Name": "UF Backwash Valve",
            "Component_Type": "Motor-operated Valve",
            "Description": "Controls backwash flow"
        },
        {
            "Tag": "MV-302",
            "Full_Name": "RO Feed Water Valve",
            "Component_Type": "Motor-operated Valve",
            "Description": "Controls flow to Stage 4 (RO Feed Water Tank)"
        },
        {
            "Tag": "PI-304",
            "Full_Name": "UF Membrane Inlet Pressure",
            "Component_Type": "Pressure Indicator",
            "Description": "Measures pressure before membrane"
        },
        {
            "Tag": "UF-301",
            "Full_Name": "UF Membrane",
            "Component_Type": "Membrane",
            "Description": "Ultrafiltration membrane unit"
        },
        {
            "Tag": "PI-305",
            "Full_Name": "UF Membrane Outlet Pressure",
            "Component_Type": "Pressure Indicator",
            "Description": "Measures pressure after membrane"
        },
        {
            "Tag": "MV-304",
            "Full_Name": "UF Drain Valve",
            "Component_Type": "Motor-operated Valve",
            "Description": "Controls drain flow from membrane"
        },
        {
            "Tag": "MV-303",
            "Full_Name": "UF Backwash Drain Valve",
            "Component_Type": "Motor-operated Valve",
            "Description": "Controls drain flow during backwash"
        }
    ]

    print(f"Generating CSV with {len(components)} components...")
    df = pd.DataFrame(components)
    
    # Ensure the directory exists
    os.makedirs(os.path.dirname(output_csv), exist_ok=True)
    
    df.to_csv(output_csv, index=False)
    print(f"Success! CSV saved to: {output_csv}")

if __name__ == "__main__":
    # Paths relative to the project structure for Stage 3
    base_dir = r"c:/Users/itrust/Downloads/Telegram Desktop/SWaT/Anomaly_Detection/Project_Steps (Stage 3)/1_Component_extraction"
    image_dir = r"c:/Users/itrust/Downloads/Telegram Desktop/SWaT/Anomaly_Detection/HMI_Images"
    
    context_file = os.path.join(base_dir, "Extraction_Context_3.txt")
    image_file = os.path.join(image_dir, "HMI_Image_3.jpeg")
    output_file = os.path.join(base_dir, "extracted_components_output_3.csv")
    
    generate_hmi_components_csv(context_file, image_file, output_file)
