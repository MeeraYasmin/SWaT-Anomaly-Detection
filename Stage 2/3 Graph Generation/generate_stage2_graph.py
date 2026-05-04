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
    # Step 1 & 2: Physical connections traced from the HMI diagram for Stage 2.
    #
    # Stage 2 — Pre-treatment / Ultrafiltration Feed:
    #   According to the user request for isolation, only pumps and valves
    #   present in the Stage 2 HMI are included.
    #   - P-201 to P-206 are connected directly to the Static Mixer.
    #   - Static Mixer is connected downstream to MV-201.
    #
    # Special Rules:
    #   - P-207 and P-208 are excluded (Rule 42).
    #   - AIT-201, 202, 203 are chemical sensors, NOT part of flow path (Rule 44).
    #   - Static Mixer is not in the whitelist and thus excluded as a node in CSVs.
    # -----------------------------------------------------------------------
    raw_edges = [
        ("P-201", "Static Mixer"), ("P-202", "Static Mixer"), ("P-203", "Static Mixer"),
        ("P-204", "Static Mixer"), ("P-205", "Static Mixer"), ("P-206", "Static Mixer"),
        ("Static Mixer", "MV-201")
    ]

    # Step 1: Filter — both endpoints must exist in whitelist (OR be Static Mixer)
    valid_edges = []
    for u, v in raw_edges:
        u_valid = u in whitelist or u == "Static Mixer"
        v_valid = v in whitelist or v == "Static Mixer"
        if u_valid and v_valid:
            valid_edges.append((u, v))
    
    # Step 2: Construct the directed graph
    G = nx.DiGraph()
    G.add_edges_from(valid_edges)

    pos = {
        "P-201": (4,  2.5),
        "P-202": (4,  1.5),
        "P-203": (4,  0.5),
        "P-204": (4, -0.5),
        "P-205": (4, -1.5),
        "P-206": (4, -2.5),
        "Static Mixer": (8, 0),
        "MV-201": (11, 0),
    }

    TYPE_COLORS = {
        "FIT": "#4FC3F7",
        "MV":  "#81C784",
        "LIT": "#FFD54F",
        "P":   "#EF9A9A",
        "Static Mixer": "#9E9E9E",
    }

    def get_color(tag):
        if tag == "Static Mixer":
            return TYPE_COLORS["Static Mixer"]
        for prefix, color in TYPE_COLORS.items():
            if tag.startswith(prefix):
                return color
        return "#B0BEC5"

    # Step 3: Dataset filtering
    print(f"Step 3 - Loading dataset from {dataset_path}...")
    df = pd.read_csv(dataset_path, low_memory=False)

    nodes = list(G.nodes())
    # Note: 'Static Mixer' is not in df but we ignore it for filtering
    columns_to_keep = ['t_stamp'] + [col for col in nodes if col in df.columns]
    print(f"Extracting columns: {columns_to_keep}")
    df_stage2 = df[columns_to_keep]

    # Step 4: Pumps checking
    print("Step 4 - Checking pump activity...")
    pumps = [col for col in df_stage2.columns if col.startswith('P-')]
    inactive_pumps = []
    for pump in pumps:
        if df_stage2[pump].nunique() < 2:
            print(f"Pump {pump} is inactive (unique values < 2). Removing...")
            inactive_pumps.append(pump)
    
    # Remove inactive pumps from dataset
    if inactive_pumps:
        df_stage2 = df_stage2.drop(columns=inactive_pumps)
        # Remove inactive pumps from graph
        for pump in inactive_pumps:
            if pump in G:
                G.remove_node(pump)
    
    os.makedirs(os.path.dirname(output_csv), exist_ok=True)
    df_stage2.to_csv(output_csv, index=False)
    print(f"Success! Filtered dataset saved to: {output_csv}")

    # Step 5: Save raw edges (remaining after filtering) as connections_2.csv
    # Only include nodes that are in the whitelist (exclude Static Mixer)
    # AND translate P -> Static Mixer -> MV to P -> MV for logical consistency if needed,
    # but the user said "without making any changes" so I'll ensure it matches old logic.
    valid_edges_after_filtering = []
    for pump in ["P-201", "P-202", "P-203", "P-204", "P-205", "P-206"]:
        if pump in G and "MV-201" in G:
            valid_edges_after_filtering.append((pump, "MV-201"))

    os.makedirs(os.path.dirname(connections_csv_path), exist_ok=True)
    with open(connections_csv_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["source", "destination"])
        for u, v in valid_edges_after_filtering:
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
        mpatches.Patch(color="#81C784", label="MV  – Motorised Valve"),
        mpatches.Patch(color="#EF9A9A", label="P   – Pump"),
        mpatches.Patch(color="#9E9E9E", label="Static Mixer (Terminal)"),
    ]
    ax.legend(handles=legend_items, loc="upper left", framealpha=0.3,
              facecolor="#263545", labelcolor="#E3F2FD")

    ax.set_title(
        "HMI Stage 2 — Directed Flow Graph\nFiltered by Whitelist & Pump Activity (with Static Mixer)",
        color="#E3F2FD", fontsize=14, fontweight="bold", pad=20,
    )
    ax.set_xlim(0, 13)
    ax.set_ylim(-4, 4)
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
    whitelist_path = "https://raw.githubusercontent.com/MeeraYasmin/SWaT-Anomaly-Detection/main/Stage%202/2%20Dataset%20Preprocessing/column_names.csv"

    # Image (optional, unused here)
    image_path = None

    # Local outputs
    output_csv = "https://raw.githubusercontent.com/MeeraYasmin/SWaT-Anomaly-Detection/main/Stage%202/3%20Graph%20Generation/stage_2_components.csv"
    graph_img = "https://raw.githubusercontent.com/MeeraYasmin/SWaT-Anomaly-Detection/main/Stage%202/3%20Graph%20Generation/HMI_Stage2_Graph.png"
    connections_csv = "https://raw.githubusercontent.com/MeeraYasmin/SWaT-Anomaly-Detection/main/Stage%202/3%20Graph%20Generation/connections_2.csv"

    generate_hmi_graph_and_dataset(
        image_path,
        whitelist_path,
        dataset_path,
        output_csv,
        graph_img,
        connections_csv
    )
