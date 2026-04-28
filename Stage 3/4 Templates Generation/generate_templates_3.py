import csv
import os

def generate_templates():
    # Define components from the Stage 3 directed graph
    # (P-302 is removed as it was identified as inactive)
    components = ['LIT-301', 'P-301', 'FIT-301', 'MV-302']
    
    # Define component types
    sensors = {'FIT', 'LIT'}
    actuators = {'MV', 'P'}
    
    def get_type(comp):
        return comp.split('-')[0]
    
    # Get unique types from components
    all_types = sorted(list(set(get_type(c) for c in components)))
    
    connections = []
    
    # Generate second order connections based on types
    for src_type in all_types:
        for dst_type in all_types:
            # Rule implementation from Template_Context_3.txt:
            # Same sensors and different sensors cannot be connected to each other
            # Same actuators and different actuators cannot be connected to each other
            # An actuator and sensor can be connected to each other
            
            is_valid = True
            
            # Rule: No sensor-sensor connections
            if src_type in sensors and dst_type in sensors:
                is_valid = False
            
            # Rule: No actuator-actuator connections
            if src_type in actuators and dst_type in actuators:
                is_valid = False
            
            # Exception: LIT cannot be connected to MV
            if src_type == 'LIT' and dst_type == 'MV':
                is_valid = False
            
            # Exception: P cannot be connected to LIT
            if src_type == 'P' and dst_type == 'LIT':
                is_valid = False
            
            if is_valid:
                connections.append((src_type, dst_type))
    
    # Save to templates_3.csv in the same directory as the script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_path = os.path.join(script_dir, 'templates_3.csv')
    
    with open(output_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Source', 'Destination'])
        for conn in connections:
            writer.writerow(conn)
    
    print(f"Generated {len(connections)} connections in {output_path}")
    print("\nConnections Summary:")
    for src, dst in connections:
        print(f"{src} -> {dst}")

if __name__ == "__main__":
    generate_templates()
