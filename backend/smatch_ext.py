import json
from penman import decode
from smatchpp import Smatchpp, solvers
from smatchpp.formalism.generic import tools as generictools
from smatchpp import data_helpers


def compare_amr(amr1: str, amr2: str) -> dict:
    """
    Align two AMR graphs (Penman strings) using SMATCH++ ILP,
    and return a dict with common_nodes and common_edges lists.

    common_nodes: [[var1, var2], …]
    common_edges: [[[src1, tgt1, role], [src2, tgt2, role]], …]
    """
    # --- Setup SMATCH++ ---
    reader = data_helpers.PenmanReader()
    standardizer = generictools.GenericStandardizer()
    ilp_solver = solvers.ILP()
    measure = Smatchpp(
        alignmentsolver=ilp_solver, graph_standardizer=standardizer, graph_reader=reader
    )

    # --- Standardize & prepare graphs ---
    g1 = standardizer.standardize(reader.string2graph(amr1))
    g2 = standardizer.standardize(reader.string2graph(amr2))
    g1p, g2p, v1, v2 = measure.graph_pair_preparer.prepare_get_vars(g1, g2)

    # --- Compute alignment ---
    alignment, var_index, _ = measure.graph_aligner.align(g1p, g2p, v1, v2)
    var_map = measure.graph_aligner._get_var_map(alignment, var_index)
    interp = measure.graph_aligner._interpretable_mapping(var_map, g1p, g2p)[0]
    # interp is a list of (var_in_1, var_in_2) pairs

    # --- Build node & edge lists from the raw Penman graphs ---
    p1 = decode(amr1)
    p2 = decode(amr2)
    triples1 = set(p1.triples)
    triples2 = set(p2.triples)

    common_nodes = [[a, b] for a, b in interp]

    mapping = dict(interp)
    common_edges = []
    for src, role, tgt in p1.triples:
        if role == ":instance":
            continue
        if src in mapping and tgt in mapping:
            ms = mapping[src]
            mt = mapping[tgt]
            if (ms, role, mt) in triples2:
                common_edges.append([[src, tgt, role], [ms, mt, role]])

    return {"common_nodes": common_nodes, "common_edges": common_edges}
