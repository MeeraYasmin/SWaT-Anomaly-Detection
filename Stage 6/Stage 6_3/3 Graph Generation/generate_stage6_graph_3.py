import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import networkx as nx
import pandas as pd
import csv
import os

def process_hmi_graph(hmi_num, hmi_name, raw_edges, pos, whitelist, df_full, output_dir):
    print(f"\n--- Processing {hmi_name} (HMI {hmi_num}) ---")
    
    # Step 1: Filter against whitelist
    valid_edges = [(u, v) for u, v in raw_edges if u in whitelist and v in whitelist]
    # Also collect isolated nodes that are in the whitelist but have no valid edges
    all_potential_nodes = set([u for u, v in raw_edges] + [v for u, v in raw_edges])
    whitelisted_nodes = [n for n in all_potential_nodes if n in whitelist]
    
    # Step 2: Construct the directed graph
    G = nx.DiGraph()
    G.add_nodes_from(whitelisted_nodes)
    G.add_edges_from(valid_edges)
    
    print(f"Step 1 & 2 - Whitelisted components: {list(G.nodes())}")

    # Step 3: Dataset filtering
    columns_to_keep = ['t_stamp'] + [col for col in G.nodes() if col in df_full.columns]
    df_hmi = df_full[columns_to_keep].copy()

    # Step 4: Pumps checking
    pumps = [col for col in df_hmi.columns if col.startswith('P-')]
    inactive_pumps = []
    for pump in pumps:
        if df_hmi[pump].nunique() < 2:
            print(f"Step 4 - Pump {pump} is inactive (unique values < 2). Removing...")
            inactive_pumps.append(pump)
    
    if inactive_pumps:
        df_hmi.drop(columns=inactive_pumps, inplace=True)
        for pump in inactive_pumps:
            if pump in G:
                G.remove_node(pump)

    # Save filtered dataset
    output_csv = os.path.join(output_dir, f"stage_6_components_{hmi_num}.csv")
    df_hmi.to_csv(output_csv, index=False)
    print(f"Step 3 & 4 - Filtered dataset saved to: {output_csv}")

    # Step 5: Save raw edges (remaining after filtering)
    connections_csv = os.path.join(output_dir, f"connections_6_{hmi_num}.csv")
    with open(connections_csv, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["source", "destination"])
        for u, v in G.edges():
            writer.writerow([u, v])
    print(f"Step 5 - Connections saved to: {connections_csv}")

    # Step 6: Plotting
    if len(G.nodes()) == 0:
        print("Skipping graph rendering for empty HMI.")
        # Create a blank image to avoid missing file errors if needed
        fig, ax = plt.subplots(figsize=(10, 4))
        fig.patch.set_facecolor("#0D1B2A")
        ax.set_facecolor("#1A2B3C")
        ax.text(0.5, 0.5, f"{hmi_name}\n(No active whitelisted components)", 
                color="white", ha='center', va='center', fontsize=12)
        ax.axis("off")
    else:
        fig, ax = plt.subplots(figsize=(12, 6))
        fig.patch.set_facecolor("#0D1B2A")
        ax.set_facecolor("#1A2B3C")

        TYPE_COLORS = {"FIT": "#4FC3F7", "LIT": "#FFD54F", "P": "#EF9A9A"}
        def get_color(tag):
            for prefix, color in TYPE_COLORS.items():
                if tag.startswith(prefix): return color
            return "#B0BEC5"

        node_colors = [get_color(n) for n in G.nodes()]
        
        # Filter pos to only contain nodes present in G
        current_pos = {n: pos[n] for n in G.nodes() if n in pos}
        
        nx.draw_networkx_edges(G, current_pos, ax=ax, edge_color="#90CAF9",
                               arrows=True, arrowstyle="-|>", arrowsize=25,
                               width=2.5, connectionstyle="arc3,rad=0.05",
                               min_source_margin=30, min_target_margin=30)
        nx.draw_networkx_nodes(G, current_pos, ax=ax, node_color=node_colors, 
                               node_size=3200, edgecolors="#FFFFFF", linewidths=2)
        nx.draw_networkx_labels(G, current_pos, ax=ax, font_size=10, 
                                font_weight="bold", font_color="#1E2A3A")

        legend_items = [
            mpatches.Patch(color="#4FC3F7", label="FIT – Flow Meter"),
            mpatches.Patch(color="#FFD54F", label="LIT – Level Sensor"),
            mpatches.Patch(color="#EF9A9A", label="P   – Pump"),
        ]
        ax.legend(handles=legend_items, loc="upper left", framealpha=0.3,
                  facecolor="#263545", labelcolor="#E3F2FD")

        ax.set_title(f"HMI Stage 6 — {hmi_name}\nDirected Flow Graph",
                     color="#E3F2FD", fontsize=14, fontweight="bold", pad=20)
        
        # Center vertically and horizontally using Stage 5 style limits
        ax.set_xlim(0, 11)
        ax.set_ylim(-3, 3)
        ax.axis("off")

    graph_img = os.path.join(output_dir, f"HMI_Stage6_Graph_{hmi_num}.png")
    plt.tight_layout()
    plt.savefig(graph_img, dpi=160, facecolor=fig.get_facecolor())
    plt.close()
    print(f"Graph image saved to: {graph_img}")

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.dirname(script_dir) # Project_Steps (Stage 6_3)
    
    prep_dir = os.path.join(base_dir, "2_Dataset_Preprocessing")
    graph_dir = script_dir

    wl_path = os.path.join(prep_dir, "column_names.csv")
    ds_path = os.path.join(prep_dir, "preprocessed_dataset.csv")

    # Load whitelist
    whitelist = set()
    with open(wl_path, newline='') as f:
        reader = csv.reader(f)
        next(reader)
        for row in reader:
            if row: whitelist.add(row[0].strip())

    # Load full dataset once
    print(f"Loading full dataset from {ds_path}...")
    df_full = pd.read_csv(ds_path, low_memory=False)

    # HMI 3: RO / UF Cleaning
    # Note: T-603, LS-603, FI-601 are excluded from whitelist. Only P-603 is potentially whitelisted.
    hmi3_edges = [("T-603", "P-603"), ("P-603", "FI-601")]
    hmi3_pos   = {"T-603": (2,0), "P-603": (5,0), "FI-601": (8,0)}
    process_hmi_graph(3, "RO / UF Cleaning", hmi3_edges, hmi3_pos, whitelist, df_full, graph_dir)
