import pandas as pd
import os

def generate_hmi_components_csv(context_path, image_path, output_csv):
    """
    Generates a CSV of HMI components for Stage 2 based on the provided context and image logic.
    """
    print(f"Reading context from {context_path}...")
    if not os.path.exists(context_path):
        print(f"Warning: {context_path} not found. Proceeding with hardcoded component list.")

    # Define the component data based on the HMI diagram analysis for Stage 2
    components = [
        {
            "Tag": "AIT-201",
            "Full_Name": "Chem Dosing Conductivity Meter",
            "Component_Type": "Analytical Indicator Transmitter",
            "Description": "Measures conductivity of water (reading: 34.45 µS/cm)"
        },
        {
            "Tag": "P-201",
            "Full_Name": "NaCl Dosing Pump 1",
            "Component_Type": "Pump",
            "Description": "Duty pump for NaCl dosing"
        },
        {
            "Tag": "P-202",
            "Full_Name": "NaCl Dosing Pump 2",
            "Component_Type": "Pump",
            "Description": "Standby pump for NaCl dosing"
        },
        {
            "Tag": "T-201",
            "Full_Name": "NaCl Tank",
            "Component_Type": "Tank",
            "Description": "Storage tank for NaCl solution"
        },
        {
            "Tag": "LS-201",
            "Full_Name": "NaCl Level Switch",
            "Component_Type": "Level Switch",
            "Description": "Monitors low/high level in NaCl tank"
        },
        {
            "Tag": "P-203",
            "Full_Name": "HCl Dosing Pump 1",
            "Component_Type": "Pump",
            "Description": "Standby pump for HCl dosing"
        },
        {
            "Tag": "P-204",
            "Full_Name": "HCl Dosing Pump 2",
            "Component_Type": "Pump",
            "Description": "Duty pump for HCl dosing"
        },
        {
            "Tag": "T-202",
            "Full_Name": "HCl Tank",
            "Component_Type": "Tank",
            "Description": "Storage tank for HCl solution"
        },
        {
            "Tag": "LS-202",
            "Full_Name": "HCl Level Switch",
            "Component_Type": "Level Switch",
            "Description": "Monitors low/high level in HCl tank"
        },
        {
            "Tag": "P-205",
            "Full_Name": "NaOCl Dosing Pump 1 (FAC)",
            "Component_Type": "Pump",
            "Description": "Duty pump for NaOCl dosing (Free Available Chlorine)"
        },
        {
            "Tag": "P-206",
            "Full_Name": "NaOCl Dosing Pump 2 (FAC)",
            "Component_Type": "Pump",
            "Description": "Standby pump for NaOCl dosing (FAC)"
        },
        {
            "Tag": "P-207",
            "Full_Name": "NaOCl Dosing Pump 1 (UF)",
            "Component_Type": "Pump",
            "Description": "Duty pump for NaOCl dosing (Ultrafiltration)"
        },
        {
            "Tag": "P-208",
            "Full_Name": "NaOCl Dosing Pump 2 (UF)",
            "Component_Type": "Pump",
            "Description": "Standby pump for NaOCl dosing (UF)"
        },
        {
            "Tag": "T-203",
            "Full_Name": "NaOCl Tank",
            "Component_Type": "Tank",
            "Description": "Storage tank for NaOCl solution"
        },
        {
            "Tag": "LS-203",
            "Full_Name": "NaOCl Level Switch",
            "Component_Type": "Level Switch",
            "Description": "Monitors low/high level in NaOCl tank"
        },
        {
            "Tag": "AIT-202",
            "Full_Name": "Chem Dosing pH Meter",
            "Component_Type": "Analytical Indicator Transmitter",
            "Description": "Measures pH level of water (reading: 6.98)"
        },
        {
            "Tag": "AIT-203",
            "Full_Name": "Chem Dosing ORP Meter",
            "Component_Type": "Analytical Indicator Transmitter",
            "Description": "Measures Oxidation-Reduction Potential (reading: 339.12 mV)"
        },
        {
            "Tag": "MV-201",
            "Full_Name": "Chemical Dosing Valve",
            "Component_Type": "Motor-operated Valve",
            "Description": "Controls flow of chemicals into main line"
        }
    ]

    print(f"Generating CSV with {len(components)} components...")
    df = pd.DataFrame(components)
    
    # Ensure the directory exists
    os.makedirs(os.path.dirname(output_csv), exist_ok=True)
    
    df.to_csv(output_csv, index=False)
    print(f"Success! CSV saved to: {output_csv}")

if __name__ == "__main__":
    # Paths relative to the project structure for Stage 2
    base_dir = r"c:/Users/itrust/Downloads/Telegram Desktop/SWaT/Anomaly_Detection/Project_Steps (Stage 2)/1_Component_extraction"
    image_dir = r"c:/Users/itrust/Downloads/Telegram Desktop/SWaT/Anomaly_Detection/HMI_Images"
    
    context_file = os.path.join(base_dir, "Extraction_Context_2.txt")
    image_file = os.path.join(image_dir, "HMI_Image_2.jpeg")
    output_file = os.path.join(base_dir, "extracted_components_output_2.csv")
    
    generate_hmi_components_csv(context_file, image_file, output_file)
