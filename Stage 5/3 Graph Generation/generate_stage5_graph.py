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
    # Step 1 & 2: Physical connections traced from the HMI diagram for Stage 5.
    #
    # Stage 5 — Reverse Osmosis (RO):
    #   - Water from FIT-501 flows through high-pressure pumps P-501/P-502.
    #   - From the pumps, water flows to FIT-502 (Permeate) and FIT-503 (Reject).
    #   - FIT-502 is followed by motorized valve MV-501.
    #   - FIT-503 is followed by motorized valve MV-502.
    #
    # Special Rules:
    #   - Analytical sensors (AIT-501-504) and pressure indicators/transmitters (PIT-501-503)
    #     are local indicators and NOT part of the flow path.
    #   - Recirculation (FIT-504) and reject valves (MV-503, MV-504) are excluded.
    #   - Protective switches (PSL-501, PSH-501) and local indicators (PI-501, PI-502, FI-501)
    #     are excluded.
    #   - Membranes (RO-501, RO-502, RO-503) are excluded as they are not in the dataset.
    # -----------------------------------------------------------------------
    raw_edges = [
        ("FIT-501", "P-501"),
        ("FIT-501", "P-502"),
        ("P-501",   "FIT-502"),
        ("P-502",   "FIT-502"),
        ("P-501",   "FIT-503"),
        ("P-502",   "FIT-503"),
        ("FIT-502", "MV-501"),
        ("FIT-503", "MV-502"),
    ]

    # Step 1: Filter against whitelist
    # Step 2: Special Rules for Stage 5 (Excluded nodes)
    excluded_nodes = {
        "AIT-501", "AIT-502", "AIT-503", "AIT-504",
        "PIT-501", "PIT-502", "PIT-503",
        "FIT-504", "MV-503", "MV-504",
        "PSL-501", "PSH-501", "PI-501", "PI-502", "FI-501",
        "RO-501", "RO-502", "RO-503"
    }
    
    valid_edges = []
    for u, v in raw_edges:
        if u in whitelist and u not in excluded_nodes:
            if v in whitelist and v not in excluded_nodes:
                valid_edges.append((u, v))
    
    # Step 2: Construct the directed graph
    G = nx.DiGraph()
    G.add_edges_from(valid_edges)
    
    # Add any remaining whitelisted nodes that should be in the graph but were not in edges
    for node in whitelist:
        # Only include Stage 5 components
        if "50" in node and "-5" in node:
            if node not in excluded_nodes and node not in G and ".Speed" not in node:
                # Basic check for tag format to avoid non-component nodes
                if any(node.startswith(prefix) for prefix in ["FIT", "P-", "MV", "AIT", "PIT", "PI", "FI", "PS"]):
                    G.add_node(node)

    pos = {
        "FIT-501": (2,  0),
        "P-501":   (4,  1),
        "P-502":   (4, -1),
        "FIT-502": (7,  1),
        "FIT-503": (7, -1),
        "MV-501":  (9,  1),
        "MV-502":  (9, -1),
    }

    TYPE_COLORS = {
        "FIT":  "#4FC3F7",
        "MV":   "#CE93D8",
        "P":    "#EF9A9A",
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
    df_stage5 = df[columns_to_keep]

    # Step 4: Pumps checking
    print("Step 4 - Checking pump activity...")
    pumps = [col for col in df_stage5.columns if col.startswith('P-')]
    inactive_pumps = []
    for pump in pumps:
        if df_stage5[pump].nunique() < 2:
            print(f"Pump {pump} is inactive (unique values < 2). Removing...")
            inactive_pumps.append(pump)
    
    # Remove inactive pumps from dataset
    if inactive_pumps:
        df_stage5 = df_stage5.drop(columns=inactive_pumps)
        # Remove inactive pumps from graph
        for pump in inactive_pumps:
            if pump in G:
                G.remove_node(pump)
    
    os.makedirs(os.path.dirname(output_csv), exist_ok=True)
    df_stage5.to_csv(output_csv, index=False)
    print(f"Success! Filtered dataset saved to: {output_csv}")

    # Step 5: Save connections (remaining after filtering) as connections_5.csv
    os.makedirs(os.path.dirname(connections_csv_path), exist_ok=True)
    with open(connections_csv_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["source", "destination"])
        for u, v in G.edges():
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
        mpatches.Patch(color="#EF9A9A", label="P   – Pump"),
        mpatches.Patch(color="#CE93D8", label="MV  – Valve"),
    ]
    ax.legend(handles=legend_items, loc="upper left", framealpha=0.3,
              facecolor="#263545", labelcolor="#E3F2FD")

    ax.set_title(
        "HMI Stage 5 — Directed Flow Graph\nFiltered by Whitelist & Pump Activity",
        color="#E3F2FD", fontsize=14, fontweight="bold", pad=20,
    )
    ax.set_xlim(0, 11)
    ax.set_ylim(-3, 3)
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
    whitelist_path = "https://raw.githubusercontent.com/MeeraYasmin/SWaT-Anomaly-Detection/main/Stage%201/2%20Dataset%20Preprocessing/column_names.csv"

    # Image (optional, unused here)
    image_path = None

    # Local outputs
    output_csv = "https://raw.githubusercontent.com/MeeraYasmin/SWaT-Anomaly-Detection/main/Stage%205/3%20Graph%20Generation/stage_5_components.csv"
    graph_img = "https://raw.githubusercontent.com/MeeraYasmin/SWaT-Anomaly-Detection/main/Stage%205/3%20Graph%20Generation/HMI_Stage5_Graph.png"
    connections_csv = "https://raw.githubusercontent.com/MeeraYasmin/SWaT-Anomaly-Detection/main/Stage%205/3%20Graph%20Generation/connections_5.csv"

    generate_hmi_graph_and_dataset(
        image_path,
        whitelist_path,
        dataset_path,
        output_csv,
        graph_img,
        connections_csv
    )
