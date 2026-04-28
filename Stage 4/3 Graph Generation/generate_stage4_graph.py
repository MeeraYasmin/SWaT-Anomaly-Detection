import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import networkx as nx
import pandas as pd
import csv
import os

def generate_hmi_graph_and_dataset(image_path, whitelist_path, dataset_path, output_csv, graph_img_path, connections_csv_path):
    print(f"Loading whitelist from {whitelist_path}...")
    whitelist = set()
    with open(whitelist_path, newline='') as f:
        reader = csv.reader(f)
        next(reader)  # skip header
        for row in reader:
            if row and row[0].strip():
                whitelist.add(row[0].strip())

    # -----------------------------------------------------------------------
    # Step 1 & 2: Physical connections traced from the HMI diagram for Stage 4.
    #
    # Stage 4 — Reverse Osmosis (RO) Feed:
    #   - Water from RO Feed Tank (LIT-401) pumped by P-401/P-402 to FIT-401.
    #   - From FIT-401, water flows through UV lamp (UV-401) to Static Mixer.
    #   - Sodium Bisulfite (NaHSO3) is pumped by P-403/P-404 to the Static Mixer.
    #
    # Special Rules:
    #   - Tanks (T-401, T-402) are excluded; LIT-401 is the proxy.
    #   - Analytical sensors (AIT-401, AIT-402) and pressure indicators (PI-401, 402) 
    #     are local indicators and NOT part of the flow path (Rule 45, 48).
    #   - Static Mixer is not in the whitelist and thus excluded as a node.
    # -----------------------------------------------------------------------
    raw_edges = [
        ("LIT-401", "P-401"),
        ("LIT-401", "P-402"),
        ("P-401",   "FIT-401"),
        ("P-402",   "FIT-401"),
        # Note: From FIT-401, flow goes through UV-401 to Static Mixer.
        # But per Special Rules 42 & 44, both UV-401 and Static Mixer are NOT to be shown.
        # Thus, FIT-401, P-403, and P-404 will be sink nodes in this graph.
        ("FIT-401", "Static Mixer"),
        ("P-403", "Static Mixer"),
        ("P-404", "Static Mixer"),
    ]

    # Step 1: Filter against whitelist
    # Step 2: Special Rules for Stage 4 (Rule 42: UV-401 and AITs need not be shown)
    excluded_nodes = {"UV-401", "AIT-401", "AIT-402"}
    
    valid_edges = []
    for u, v in raw_edges:
        # Both endpoints whitelisted OR one is Static Mixer (visual node)
        u_valid = u in whitelist and u not in excluded_nodes
        v_valid = v in whitelist and v not in excluded_nodes
        
        if u_valid and (v_valid or v == "Static Mixer"):
            valid_edges.append((u, v))
        elif u == "Static Mixer" and v_valid:
            valid_edges.append((u, v))
    
    # Step 2: Construct the directed graph
    G = nx.DiGraph()
    G.add_edges_from(valid_edges)
    
    # Add any remaining whitelisted nodes that should be in the graph but were not in edges
    # (e.g. isolated pumps)
    for node in whitelist:
        # Only include Stage 4 components
        if any(prefix in node for prefix in ["40", "4-"]):
            if node not in excluded_nodes and node not in G:
                G.add_node(node)

    pos = {
        "LIT-401": (2,  0),
        "P-401":   (4,  1),
        "P-402":   (4, -1),
        "FIT-401": (6,  0),
        "P-403":   (8,  2),
        "P-404":   (8, -2),
        "Static Mixer": (11, 0),
    }

    TYPE_COLORS = {
        "FIT":  "#4FC3F7",
        "UV":   "#CE93D8",
        "LIT":  "#FFD54F",
        "P":    "#EF9A9A",
        "AIT":  "#81C784",
        "Static Mixer": "#9E9E9E",
    }

    def get_color(tag):
        for prefix, color in TYPE_COLORS.items():
            if tag.startswith(prefix):
                return color
        return "#B0BEC5"

    # Step 3: Dataset filtering
    print(f"Step 3 - Loading dataset from {dataset_path}...")
    df = pd.read_csv(dataset_path, low_memory=False)

    nodes = sorted(list(G.nodes()))
    columns_to_keep = ['t_stamp'] + [col for col in nodes if col in df.columns]
    print(f"Extracting columns: {columns_to_keep}")
    df_stage4 = df[columns_to_keep]

    # Step 4: Pumps checking
    print("Step 4 - Checking pump activity...")
    pumps = [col for col in df_stage4.columns if col.startswith('P-')]
    inactive_pumps = []
    for pump in pumps:
        if df_stage4[pump].nunique() < 2:
            print(f"Pump {pump} is inactive (unique values < 2). Removing...")
            inactive_pumps.append(pump)
    
    # Remove inactive pumps from dataset
    if inactive_pumps:
        df_stage4 = df_stage4.drop(columns=inactive_pumps)
        # Remove inactive pumps from graph
        for pump in inactive_pumps:
            if pump in G:
                G.remove_node(pump)
    
    os.makedirs(os.path.dirname(output_csv), exist_ok=True)
    df_stage4.to_csv(output_csv, index=False)
    print(f"Success! Filtered dataset saved to: {output_csv}")

    # Step 5: Save connections (remaining after filtering) as connections_4.csv
    os.makedirs(os.path.dirname(connections_csv_path), exist_ok=True)
    with open(connections_csv_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["source", "destination"])
        for u, v in G.edges():
            if u != "Static Mixer" and v != "Static Mixer":
                writer.writerow([u, v])
    print(f"Connections saved to: {connections_csv_path}")

    # Step 6: Plotting the graph
    node_colors = [get_color(n) for n in G.nodes()]
    
    fig, ax = plt.subplots(figsize=(14, 8))
    fig.patch.set_facecolor("#0D1B2A")
    ax.set_facecolor("#1A2B3C")

    label_dict = {n: n for n in G.nodes()}
    
    nx.draw_networkx_edges(
        G, pos, ax=ax,
        edge_color="#90CAF9",
        arrows=True, arrowstyle="-|>", arrowsize=25,
        width=2.5, connectionstyle="arc3,rad=0.05",
        min_source_margin=30, min_target_margin=30,
    )

    # Use a safe draw—only nodes in G.nodes() that are in pos
    active_pos = {n: pos[n] for n in G.nodes() if n in pos}
    
    nx.draw_networkx_nodes(
        G, active_pos, ax=ax,
        node_color=node_colors, node_size=3200,
        edgecolors="#FFFFFF", linewidths=2,
    )

    nx.draw_networkx_labels(
        G, active_pos, labels=label_dict, ax=ax,
        font_size=9, font_weight="bold", font_color="#1E2A3A",
    )

    legend_items = [
        mpatches.Patch(color="#4FC3F7", label="FIT – Flow Meter"),
        mpatches.Patch(color="#FFD54F", label="LIT – Level Sensor"),
        mpatches.Patch(color="#EF9A9A", label="P   – Pump"),
        mpatches.Patch(color="#9E9E9E", label="Static Mixer (Terminal)"),
    ]
    ax.legend(handles=legend_items, loc="upper left", framealpha=0.3,
              facecolor="#263545", labelcolor="#E3F2FD")

    ax.set_title(
        "HMI Stage 4 — Directed Flow Graph\nFiltered by Whitelist & Pump Activity (with Static Mixer)",
        color="#E3F2FD", fontsize=14, fontweight="bold", pad=20,
    )
    ax.set_xlim(0, 13)
    ax.set_ylim(-3, 3)
    ax.axis("off")
    plt.tight_layout()

    os.makedirs(os.path.dirname(graph_img_path), exist_ok=True)
    plt.savefig(graph_img_path, dpi=160, facecolor=fig.get_facecolor())
    plt.close()
    print(f"Graph image saved to: {graph_img_path}")

if __name__ == "__main__":
    base_dir = r"c:/Users/itrust/Downloads/Telegram Desktop/SWaT"
    stage1_dir = os.path.join(base_dir, "Anomaly_Detection/Project_Steps (Stage 1)")
    stage4_dir = os.path.join(base_dir, "Anomaly_Detection/Project_Steps (Stage 4)")
    graph_dir  = os.path.join(stage4_dir, "3_Graph_Generation")

    wl = os.path.join(stage4_dir, "2_Dataset_Preprocessing/column_names.csv")
    ds = os.path.join(stage4_dir, "2_Dataset_Preprocessing/preprocessed_dataset.csv")

    out_csv         = os.path.join(graph_dir, "stage_4_components.csv")
    out_img         = os.path.join(graph_dir, "HMI_Stage4_Graph.png")
    out_connections = os.path.join(graph_dir, "connections_4.csv")

    generate_hmi_graph_and_dataset(None, wl, ds, out_csv, out_img, out_connections)
