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
    # Step 1: Physical connections traced from the HMI diagram (HMI_Image_1).
    #
    # Stage 1 — Raw Water Intake:
    #   Water enters via FIT-101 (flow meter), passes through MV-101 (inlet
    #   valve) and fills Tank T-101.  LIT-101 is the proxy for T-101.
    #   P-101 and P-102 draw from the tank and push water to Stage 2.
    #
    # NOTE: PI-101 and PI-102 are pressure gauges visible on the diagram but
    #       absent from the whitelist → excluded per Step 1 rules.
    #       T-101 is not a tracked component; LIT-101 represents it.
    # -----------------------------------------------------------------------
    raw_edges = [
        # Stage 1
        ("FIT-101", "MV-101"),
        ("MV-101",  "LIT-101"),
        ("LIT-101", "P-101"),
        ("LIT-101", "P-102"),
        ("P-101",   "FIT-201"),
        ("P-102",   "FIT-201"),
    ]

    # Step 1: Filter — both endpoints must exist in whitelist
    valid_edges = [(u, v) for u, v in raw_edges if u in whitelist and v in whitelist]
    all_nodes_in_graph = sorted(set([u for u, v in valid_edges] + [v for u, v in valid_edges]))
    print(f"Step 1 - Filtered components: {all_nodes_in_graph}")

    # Step 2: Construct the directed graph
    G = nx.DiGraph()
    G.add_edges_from(valid_edges)

    pos = {
        "FIT-101": (2,  0),
        "MV-101":  (4,  0),
        "LIT-101": (6,  0),
        "P-101":   (8,  1),
        "P-102":   (8, -1),
        "FIT-201": (10, 0),
    }

    TYPE_COLORS = {
        "FIT": "#4FC3F7",
        "MV":  "#81C784",
        "LIT": "#FFD54F",
        "P":   "#EF9A9A",
    }

    def get_color(tag):
        for prefix, color in TYPE_COLORS.items():
            if tag.startswith(prefix):
                return color
        return "#B0BEC5"

    node_colors = [get_color(n) for n in G.nodes()]


    # Step 3: Dataset filtering
    print(f"Step 3 - Loading dataset from {dataset_path}...")
    df = pd.read_csv(dataset_path, low_memory=False)

    nodes = list(G.nodes())
    columns_to_keep = ['t_stamp'] + [col for col in nodes if col in df.columns]
    print(f"Extracting columns: {columns_to_keep}")
    df_stage1 = df[columns_to_keep]

    # Step 4: Pumps checking
    print("Step 4 - Checking pump activity...")
    pumps = [col for col in df_stage1.columns if col.startswith('P-')]
    inactive_pumps = []
    for pump in pumps:
        if df_stage1[pump].nunique() < 2:
            print(f"Pump {pump} is inactive (unique values < 2). Removing...")
            inactive_pumps.append(pump)
    
    # Remove inactive pumps from dataset
    if inactive_pumps:
        df_stage1 = df_stage1.drop(columns=inactive_pumps)
        # Remove inactive pumps from graph
        for pump in inactive_pumps:
            if pump in G:
                G.remove_node(pump)
    
    os.makedirs(os.path.dirname(output_csv), exist_ok=True)
    df_stage1.to_csv(output_csv, index=False)
    print(f"Success! Filtered dataset saved to: {output_csv}")

    # Step 5: Save raw edges (remaining after filtering) as connections.csv
    valid_edges_after_filtering = list(G.edges())
    os.makedirs(os.path.dirname(connections_csv_path), exist_ok=True)
    with open(connections_csv_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["source", "destination"])
        for u, v in valid_edges_after_filtering:
            writer.writerow([u, v])
    print(f"Connections saved to: {connections_csv_path}")

    # Step 6: Plotting the graph
    node_colors = [get_color(n) for n in G.nodes()]
    
    fig, ax = plt.subplots(figsize=(14, 6))
    fig.patch.set_facecolor("#0D1B2A")
    ax.set_facecolor("#1A2B3C")

    # Re-generate labels and positions for existing nodes only
    label_dict = {n: n for n in G.nodes()}
    
    nx.draw_networkx_edges(
        G, pos, ax=ax,
        edge_color="#90CAF9",
        arrows=True, arrowstyle="-|>", arrowsize=25,
        width=2.5, connectionstyle="arc3,rad=0.08",
        min_source_margin=30, min_target_margin=30,
    )

    nx.draw_networkx_nodes(
        G, pos, ax=ax,
        node_color=node_colors, node_size=3200,
        edgecolors="#FFFFFF", linewidths=2,
    )

    nx.draw_networkx_labels(
        G, pos, labels=label_dict, ax=ax,
        font_size=9, font_weight="bold", font_color="#1E2A3A",
    )

    legend_items = [
        mpatches.Patch(color="#4FC3F7", label="FIT – Flow Meter"),
        mpatches.Patch(color="#81C784", label="MV  – Motorised Valve"),
        mpatches.Patch(color="#FFD54F", label="LIT – Level Sensor"),
        mpatches.Patch(color="#EF9A9A", label="P   – Pump"),
    ]
    ax.legend(handles=legend_items, loc="upper left", framealpha=0.3,
              facecolor="#263545", labelcolor="#E3F2FD")

    ax.set_title(
        "HMI Stage 1 — Directed Flow Graph\nFiltered by Whitelist & Pump Activity",
        color="#E3F2FD", fontsize=14, fontweight="bold", pad=20,
    )
    ax.set_xlim(0, 12)
    ax.axis("off")
    plt.tight_layout()

    os.makedirs(os.path.dirname(graph_img_path), exist_ok=True)
    plt.savefig(graph_img_path, dpi=160, facecolor=fig.get_facecolor())
    plt.close()
    print(f"Graph image saved to: {graph_img_path}")

if __name__ == "__main__":
    base_dir = r"c:/Users/itrust/Downloads/Telegram Desktop/SWaT"
    stage1_dir = os.path.join(base_dir, "Anomaly_Detection/Project_Steps (Stage 1)")
    graph_dir = os.path.join(stage1_dir, "3_Graph_Generation")

    img   = os.path.join(base_dir, "Anomaly_Detection/HMI_Images/HMI_Image_1.jpeg")
    wl    = os.path.join(stage1_dir, "2_Dataset_Preprocessing/column_names.csv")
    ds    = os.path.join(stage1_dir, "2_Dataset_Preprocessing/preprocessed_dataset.csv")

    out_csv         = os.path.join(graph_dir, "stage_1_components.csv")
    out_img         = os.path.join(graph_dir, "HMI_Stage1_Graph.png")
    out_connections = os.path.join(graph_dir, "connections.csv")

    generate_hmi_graph_and_dataset(img, wl, ds, out_csv, out_img, out_connections)
