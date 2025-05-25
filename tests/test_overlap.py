import os
import pytest
from amrsummarizer.amr2nx import load_amr_graph
from amrsummarizer.annotate import annotate_overlap

BASE_PATH_TO_SAMPLES = "src/amrsummarizer/sample_amrs"
SAMPLE1_AMR_PATH = os.path.join(BASE_PATH_TO_SAMPLES, "sample1.amr")
SAMPLE2_AMR_PATH = os.path.join(BASE_PATH_TO_SAMPLES, "sample2.amr")
ALIGNMENT_JSON_PATH = os.path.join(BASE_PATH_TO_SAMPLES, "alignment.json") # backend/alignment.json から修正

def test_annotate_and_check_overlap():
    # 1) Load two AMR graphs
    if not os.path.exists(SAMPLE1_AMR_PATH):
        pytest.skip(f"Test data file not found: {SAMPLE1_AMR_PATH}")
    with open(SAMPLE1_AMR_PATH, "r", encoding="utf-8") as f1:
        g1_string = f1.read()
    g1 = load_amr_graph(g1_string)
    assert g1 is not None, f"Failed to load graph from {SAMPLE1_AMR_PATH}"

    if not os.path.exists(SAMPLE2_AMR_PATH):
        pytest.skip(f"Test data file not found: {SAMPLE2_AMR_PATH}")
    with open(SAMPLE2_AMR_PATH, "r", encoding="utf-8") as f2:
        g2_string = f2.read()
    g2 = load_amr_graph(g2_string)
    assert g2 is not None, f"Failed to load graph from {SAMPLE2_AMR_PATH}"

    # 2) Supply the alignment.json path
    #    Ensure alignment.json exists in src/amrsummarizer/sample_amrs/
    if not os.path.exists(ALIGNMENT_JSON_PATH):
        pytest.skip(f"Alignment file not found: {ALIGNMENT_JSON_PATH}")

    # annotate_overlap はグラフを直接変更する可能性があります
    try:
        annotate_overlap(g1, g2, ALIGNMENT_JSON_PATH)
    except Exception as e:
        pytest.fail(f"annotate_overlap raised an exception: {e} with path {ALIGNMENT_JSON_PATH}")

    # 3) Print out which nodes/edges got marked overlap=True
    #    (これらの print 文はデバッグ用です。実際のテストではアサーションを使用します)
    
    g1_overlap_nodes = [n for n, d in g1.nodes(data=True) if d.get("overlap")]
    g1_overlap_edges = [(u, v) for u, v, d in g1.edges(data=True) if d.get("overlap")]

    print(f"\nGraph1 overlap nodes: {g1_overlap_nodes}")
    print(f"Graph1 overlap edges: {g1_overlap_edges}")

    # 必要に応じて g2 に対するチェックも追加
    g2_overlap_nodes = [n for n, d in g2.nodes(data=True) if d.get("overlap")]
    g2_overlap_edges = [(u, v) for u, v, d in g2.edges(data=True) if d.get("overlap")]
    print(f"Graph2 overlap nodes: {g2_overlap_nodes}")
    print(f"Graph2 overlap edges: {g2_overlap_edges}")