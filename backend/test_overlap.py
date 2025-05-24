from amr2nx import load_amr_graph
from annotate import annotate_overlap
import json
import networkx as nx

# 1) Load two AMR graphs
g1 = load_amr_graph(open("backend/sample1.amr").read())
g2 = load_amr_graph(open("backend/sample2.amr").read())

# 2) (For now) supply a dummy alignment.json
#    You can hand-craft this file or generate it with Smatchpp (see below).
annotate_overlap(g1, g2, "backend/alignment.json")

# 3) Print out which nodes/edges got marked overlap=True
print("Graph1 overlap nodes:", [n for n, d in g1.nodes(data=True) if d["overlap"]])
print(
    "Graph1 overlap edges:", [(u, v) for u, v, d in g1.edges(data=True) if d["overlap"]]
)
