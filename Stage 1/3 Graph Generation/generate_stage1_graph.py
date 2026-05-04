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


def generate_hmi_graph_and_dataset(image_path, whitelist_path, dataset_path,
                                   output_csv, graph_img_path, connections_csv_path):

    print(f"Loading whitelist from {whitelist_path}...")

    # Handle GitHub RAW
    if whitelist_path.startswith("http"):
        df_wl = load_csv_from_github(whitelist_path)
        whitelist = set(df_wl.iloc[:, 0].dropna().astype(str).str.strip())
    else:
        whitelist = set()
        with open(whitelist_path, newline='') as f:
            reader = csv.reader(f)
            next(reader)
            for row in reader:
                if row and row[0].strip():
                    whitelist.add(row[0].strip())

    # ------------------- GRAPH EDGES -------------------
    raw_edges = [
        ("FIT-101", "MV-101"),
        ("MV-101",  "LIT-101"),
        ("LIT-101", "P-101"),
        ("LIT-101", "P-102"),
        ("P-101",   "FIT-201"),
        ("P-102",   "FIT-201"),
    ]

    valid_edges = [(u, v) for u, v in raw_edges if u in whitelist and v in whitelist]
    print(f"Filtered components: {valid_edges}")

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

    # ------------------- DATASET -------------------
    print(f"Loading dataset from {dataset_path}...")
    df = pd.read_csv(dataset_path, low_memory=False)

    nodes = list(G.nodes())
    columns_to_keep = ['t_stamp'] + [col for col in nodes if col in df.columns]

    df_stage1 = df[columns_to_keep]

    # Pump filtering
    pumps = [col for col in df_stage1.columns if col.startswith('P-')]
    inactive_pumps = []

    for pump in pumps:
        if df_stage1[pump].nunique() < 2:
            inactive_pumps.append(pump)

    if inactive_pumps:
        df_stage1 = df_stage1.drop(columns=inactive_pumps)
        for pump in inactive_pumps:
            if pump in G:
                G.remove_node(pump)

    # ------------------- SAVE OUTPUTS -------------------
    os.makedirs(os.path.dirname(output_csv), exist_ok=True)
    df_stage1.to_csv(output_csv, index=False)

    # Save edges
    os.makedirs(os.path.dirname(connections_csv_path), exist_ok=True)
    with open(connections_csv_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["source", "destination"])
        for u, v in G.edges():
            writer.writerow([u, v])

    # ------------------- GRAPH -------------------
    fig, ax = plt.subplots(figsize=(14, 6))
    fig.patch.set_facecolor("#0D1B2A")
    ax.set_facecolor("#1A2B3C")

    nx.draw_networkx_edges(G, pos, ax=ax, arrows=True)
    nx.draw_networkx_nodes(G, pos, node_color=[get_color(n) for n in G.nodes()])
    nx.draw_networkx_labels(G, pos)

    plt.tight_layout()
    os.makedirs(os.path.dirname(graph_img_path), exist_ok=True)
    plt.savefig(graph_img_path)
    plt.close()

    print(" Graph + dataset generated!")


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
    output_csv = "https://raw.githubusercontent.com/MeeraYasmin/SWaT-Anomaly-Detection/main/Stage%201/3%20Graph%20Generation/stage_1_components.csv"
    graph_img = "https://raw.githubusercontent.com/MeeraYasmin/SWaT-Anomaly-Detection/main/Stage%201/3%20Graph%20Generation/HMI_Stage1_Graph.png"
    connections_csv = "https://raw.githubusercontent.com/MeeraYasmin/SWaT-Anomaly-Detection/main/Stage%201/3%20Graph%20Generation/connections.csv"

    generate_hmi_graph_and_dataset(
        image_path,
        whitelist_path,
        dataset_path,
        output_csv,
        graph_img,
        connections_csv
    )
