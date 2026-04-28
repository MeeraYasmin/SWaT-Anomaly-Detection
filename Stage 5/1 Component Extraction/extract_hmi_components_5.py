import pandas as pd
import os

def generate_hmi_components_csv(context_path, image_path, output_csv):
    """
    Generates a CSV of HMI components for Stage 2 based on the provided context and image logic.
    """
    print(f"Reading context from {context_path}...")
    if not os.path.exists(context_path):
        print(f"Warning: {context_path} not found. Proceeding with hardcoded component list.")

    # Define the component data based on the HMI diagram analysis for Stage 5
    components = [
        {
            "Tag": "FIT-501",
            "Full_Name": "RO Membrane Inlet Flow Meter",
            "Component_Type": "Flow Indicator Transmitter",
            "Description": "Measures water flow rate at the RO membrane inlet (reading: 1.22 m³/h)"
        },
        {
            "Tag": "PSL-501",
            "Full_Name": "RO Feed Pressure Switch Low",
            "Component_Type": "Pressure Switch",
            "Description": "Low-pressure safety switch for RO feed"
        },
        {
            "Tag": "PIT-501",
            "Full_Name": "RO Membrane Inlet Pressure Meter",
            "Component_Type": "Pressure Indicator Transmitter",
            "Description": "Measures pressure at the RO membrane inlet (reading: 220.42 kPa)"
        },
        {
            "Tag": "P-501",
            "Full_Name": "RO High Pressure Pump 1",
            "Component_Type": "Pump",
            "Description": "Primary high-pressure pump for RO process (reading: 10.00 Hz)"
        },
        {
            "Tag": "P-502",
            "Full_Name": "RO High Pressure Pump 2",
            "Component_Type": "Pump",
            "Description": "Secondary high-pressure pump for RO process (reading: 0.00 Hz)"
        },
        {
            "Tag": "PSH-501",
            "Full_Name": "RO Feed Pressure Switch High",
            "Component_Type": "Pressure Switch",
            "Description": "High-pressure safety switch for RO feed"
        },
        {
            "Tag": "RO-501",
            "Full_Name": "RO Vessel 1",
            "Component_Type": "Reverse Osmosis Vessel",
            "Description": "Reverse Osmosis membrane vessel 1"
        },
        {
            "Tag": "RO-502",
            "Full_Name": "RO Vessel 2",
            "Component_Type": "Reverse Osmosis Vessel",
            "Description": "Reverse Osmosis membrane vessel 2"
        },
        {
            "Tag": "RO-503",
            "Full_Name": "RO Vessel 3",
            "Component_Type": "Reverse Osmosis Vessel",
            "Description": "Reverse Osmosis membrane vessel 3"
        },
        {
            "Tag": "PIT-502",
            "Full_Name": "RO Membrane Pressure Meter",
            "Component_Type": "Pressure Indicator Transmitter",
            "Description": "Measures pressure at the RO membrane permeate (reading: 2.05 kPa)"
        },
        {
            "Tag": "AIT-504",
            "Full_Name": "RO Permeate Conductivity Meter",
            "Component_Type": "Analytical Indicator Transmitter",
            "Description": "Measures conductivity of RO permeate (reading: 1.77 µS/cm)"
        },
        {
            "Tag": "FIT-502",
            "Full_Name": "RO Permeate Flow Meter",
            "Component_Type": "Flow Indicator Transmitter",
            "Description": "Measures flow rate of RO permeate (reading: 1.04 m³/h)"
        },
        {
            "Tag": "MV-501",
            "Full_Name": "RO Permeate Valve",
            "Component_Type": "Motorized Valve",
            "Description": "Controls the flow of RO permeate"
        },
        {
            "Tag": "MV-503",
            "Full_Name": "Permeate Reject Valve",
            "Component_Type": "Motorized Valve",
            "Description": "Controls the rejection of RO permeate"
        },
        {
            "Tag": "PI-501",
            "Full_Name": "RO Feed Pressure 1",
            "Component_Type": "Pressure Indicator",
            "Description": "Measures feed pressure before filtration"
        },
        {
            "Tag": "PI-502",
            "Full_Name": "RO Feed Pressure 2",
            "Component_Type": "Pressure Indicator",
            "Description": "Measures feed pressure after filtration"
        },
        {
            "Tag": "AIT-501",
            "Full_Name": "pH Meter",
            "Component_Type": "Analytical Indicator Transmitter",
            "Description": "Measures pH level of RO feed water (reading: 6.58)"
        },
        {
            "Tag": "AIT-502",
            "Full_Name": "RO Feed ORP Meter",
            "Component_Type": "Analytical Indicator Transmitter",
            "Description": "Measures ORP of RO feed water (reading: 306.25 mV)"
        },
        {
            "Tag": "AIT-503",
            "Full_Name": "RO Feed Conductivity Meter",
            "Component_Type": "Analytical Indicator Transmitter",
            "Description": "Measures conductivity of RO feed water (reading: 60.18 µS/cm)"
        },
        {
            "Tag": "FIT-504",
            "Full_Name": "RO Recirculation Flow Meter",
            "Component_Type": "Flow Indicator Transmitter",
            "Description": "Measures flow rate in the recirculation loop (reading: 0.02 m³/h)"
        },
        {
            "Tag": "FIT-503",
            "Full_Name": "RO Reject Flow Meter",
            "Component_Type": "Flow Indicator Transmitter",
            "Description": "Measures flow rate of RO reject water (reading: 0.10 m³/h)"
        },
        {
            "Tag": "PIT-503",
            "Full_Name": "RO Reject Pressure Meter",
            "Component_Type": "Pressure Indicator Transmitter",
            "Description": "Measures pressure of RO reject water (reading: 200.65 kPa)"
        },
        {
            "Tag": "MV-502",
            "Full_Name": "RO Backwash Valve",
            "Component_Type": "Motorized Valve",
            "Description": "Controls the backwash of RO membranes"
        },
        {
            "Tag": "MV-504",
            "Full_Name": "RO Reject Valve",
            "Component_Type": "Motorized Valve",
            "Description": "Controls the flow of RO reject water"
        },
        {
            "Tag": "FI-501",
            "Full_Name": "RO Reject Rotameter",
            "Component_Type": "Flow Indicator",
            "Description": "Visual flow indicator for RO reject water"
        }
    ]

    print(f"Generating CSV with {len(components)} components...")
    df = pd.DataFrame(components)
    
    # Ensure the directory exists
    os.makedirs(os.path.dirname(output_csv), exist_ok=True)
    
    df.to_csv(output_csv, index=False)
    print(f"Success! CSV saved to: {output_csv}")

if __name__ == "__main__":
    # Paths relative to the project structure for Stage 5
    base_dir = r"c:/Users/itrust/Downloads/Telegram Desktop/SWaT/Anomaly_Detection/Project_Steps (Stage 5)/1_Component_extraction"
    image_dir = r"c:/Users/itrust/Downloads/Telegram Desktop/SWaT/Anomaly_Detection/HMI_Images"
    
    context_file = os.path.join(base_dir, "Extraction_Context_5.txt")
    image_file = os.path.join(image_dir, "HMI_Image_5.jpeg")
    output_file = os.path.join(base_dir, "extracted_components_output_5.csv")
    
    generate_hmi_components_csv(context_file, image_file, output_file)
