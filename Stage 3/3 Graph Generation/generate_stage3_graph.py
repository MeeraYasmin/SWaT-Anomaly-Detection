import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import networkx as nx
import pandas as pd
import csv
import os
import kaggle
import requests


def load_csv_from_github(url):
    """Fetch CSV from GitHub raw link"""
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception("Failed to fetch CSV from GitHub")
    return pd.read_csv(pd.io.common.StringIO(response.text))


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
    # Step 1 & 2: Physical connections traced from the HMI diagram for Stage 3.
    #
    # Stage 3 — Ultrafiltration (UF) Feed:
    #   - Water from UF Feed Tank (LIT-301) pumped by P-301/P-302 to FIT-301.
    #   - From FIT-301, water flows through DPIT-301 and the UF membrane (UF-301).
    #   - Both paths converge at MV-302.
    #
    # Special Rules:
    #   - UF-301 is not shown (per rule 48).
    #   - MV-301, 303, 304 are for backwashing and excluded (Rule 46).
    #   - AIT-301, 302, 303 are analytical sensors, NOT part of flow path (Rule 48).
    # -----------------------------------------------------------------------
    raw_edges = [
        ("LIT-301", "P-301"),
        ("LIT-301", "P-302"),
        ("P-301",   "FIT-301"),
        ("P-302",   "FIT-301"),
        ("FIT-301", "MV-302"), # Representation of flow through UF-301
    ]

    # Step 1: Filter — both endpoints must exist in whitelist
    valid_edges = [(u, v) for u, v in raw_edges if u in whitelist and v in whitelist]
    
    # Step 2: Construct the directed graph
    G = nx.DiGraph()
    G.add_edges_from(valid_edges)

    pos = {
        "LIT-301":  (2,  0),
        "P-301":    (4,  0.5),
        "P-302":    (4, -0.5),
        "FIT-301":  (6,  0),
        "DPIT-301": (8,  0.5),
        "MV-302":   (10, 0),
    }

    TYPE_COLORS = {
        "FIT":  "#4FC3F7",
        "MV":   "#81C784",
        "LIT":  "#FFD54F",
        "P":    "#EF9A9A",
        "DPIT": "#FFAB91",
    }

    def get_color(tag):
        for prefix, color in TYPE_COLORS.items():
            if tag.startswith(prefix):
                return color
        return "#B0BEC5"

    # Step 3: Dataset filtering
    print(f"Step 3 - Loading dataset from {dataset_path}...")
    df = pd.read_csv(dataset_path, low_memory=False)

    nodes = list(G.nodes())
    columns_to_keep = ['t_stamp'] + [col for col in nodes if col in df.columns]
    
    # DPIT column can be kept on stage_3_components.csv even though it's not on the graph
    if "DPIT-301" in df.columns and "DPIT-301" not in columns_to_keep:
        # Maintain order: Insert DPIT-301 after FIT-301 if FIT-301 exists
        if "FIT-301" in columns_to_keep:
            idx = columns_to_keep.index("FIT-301") + 1
            columns_to_keep.insert(idx, "DPIT-301")
        else:
            columns_to_keep.append("DPIT-301")
        
    print(f"Extracting columns: {columns_to_keep}")
    df_stage3 = df[columns_to_keep]

    # Step 4: Pumps checking
    print("Step 4 - Checking pump activity...")
    pumps = [col for col in df_stage3.columns if col.startswith('P-')]
    inactive_pumps = []
    for pump in pumps:
        if df_stage3[pump].nunique() < 2:
            print(f"Pump {pump} is inactive (unique values < 2). Removing...")
            inactive_pumps.append(pump)
    
    # Remove inactive pumps from dataset
    if inactive_pumps:
        df_stage3 = df_stage3.drop(columns=inactive_pumps)
        # Remove inactive pumps from graph
        for pump in inactive_pumps:
            if pump in G:
                G.remove_node(pump)
    
    os.makedirs(os.path.dirname(output_csv), exist_ok=True)
    df_stage3.to_csv(output_csv, index=False)
    print(f"Success! Filtered dataset saved to: {output_csv}")

    # Step 5: Save raw edges (remaining after filtering) as connections_3.csv
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
    
    fig, ax = plt.subplots(figsize=(14, 7))
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
        "HMI Stage 3 — Directed Flow Graph\nFiltered by Whitelist & Pump Activity",
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

    # Download Kaggle dataset
    kaggle.api.dataset_download_files(
        "meera0405/swat-dataset",
        path="data/",
        unzip=True
    )

    base_dir = "data"

    # Local dataset (downloaded)
    dataset_path = os.path.join(base_dir, "preprocessed_dataset.csv")

    # GitHub RAW whitelist
    whitelist_path = "https://raw.githubusercontent.com/MeeraYasmin/SWaT-Anomaly-Detection/main/Stage%203/2%20Dataset%20Preprocessing/column_names.csv"

    # Image (optional, unused here)
    image_path = None

    # Local outputs
    output_csv = "https://raw.githubusercontent.com/MeeraYasmin/SWaT-Anomaly-Detection/main/Stage%203/3%20Graph%20Generation/stage_3_components.csv"
    graph_img = "https://raw.githubusercontent.com/MeeraYasmin/SWaT-Anomaly-Detection/main/Stage%203/3%20Graph%20Generation/HMI_Stage3_Graph.png"
    connections_csv = "https://raw.githubusercontent.com/MeeraYasmin/SWaT-Anomaly-Detection/main/Stage%203/3%20Graph%20Generation/connections_3.csv"

    generate_hmi_graph_and_dataset(
        image_path,
        whitelist_path,
        dataset_path,
        output_csv,
        graph_img,
        connections_csv
    )
