import json
from smatchpp import Smatchpp, solvers

# 1) read your AMR strings
s1 = open("backend/sample1.amr").read().strip()
s2 = open("backend/sample2.amr").read().strip()

# 2) set up SMATCH++ for optimal alignment
ilp = solvers.ILP()
measure = Smatchpp(alignmentsolver=ilp)

# 3) process the pair
match, status, alignment = measure.process_pair(s1, s2)

# 4) extract an “interpretable” mapping: list of (node1,node2) pairs
node_map = measure.graph_aligner._interpretable_mapping(
    alignment, 
    *measure.graph_pair_preparer.prepare_get_vars(
        *measure.graph_standardizer.standardize(
            *measure.graph_reader.string2graph(s1)
        ),
        *measure.graph_standardizer.standardize(
            *measure.graph_reader.string2graph(s2)
        )
    )[:2]
)

# 5) for simplicity, treat each matched triple as an “edge” match
#    you could also retrieve edge alignments similarly via the aligner internals.
common_nodes = [[n1, n2] for (n1,n2) in node_map]
# (You’ll need custom code to build common_edges in the same spirit.)

out = {
    "common_nodes": common_nodes,
    # "common_edges": [...]
}

with open("backend/alignment.json", "w", encoding="utf-8") as f:
    json.dump(out, f, indent=2)

print("Wrote backend/alignment.json")
