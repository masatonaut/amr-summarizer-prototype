export function amrToGraph(amrString) {
  const nodes = [];
  const edges = [];

  // Split the AMR string into lines, ignoring comments and empty lines
  const lines = amrString
    .split("\n")
    .filter((line) => !line.startsWith("#") && line.trim() !== "");

  let currentNodeId = 0;
  const nodeMap = {}; // variableName -> nodeId

  lines.forEach((line) => {
    const trimmed = line.trim();
    if (trimmed.startsWith("(")) {
      // e.g., (s / summarize-01)
      const match = trimmed.match(/\(([^/\s]+)\s*\/\s*([^\s)]+)/);
      if (match) {
        const [, varName, concept] = match;
        if (!nodeMap[varName]) {
          nodeMap[varName] = currentNodeId++;
          nodes.push({
            id: nodeMap[varName],
            label: `${varName} / ${concept}`,
          });
        }
      }
    } else if (trimmed.startsWith(":")) {
      // e.g., :ARG1 (t / test-01)
      const match = trimmed.match(/^:([^(\s]+)\s*\(([^/\s]+)\s*\/\s*([^\s)]+)/);
      if (match) {
        const [, relation, varName, concept] = match;
        if (!nodeMap[varName]) {
          nodeMap[varName] = currentNodeId++;
          nodes.push({
            id: nodeMap[varName],
            label: `${varName} / ${concept}`,
          });
        }
        // Naively assume the source is the last node in 'nodes'
        if (nodes.length > 0) {
          const sourceId = nodes[nodes.length - 1].id;
          const targetId = nodeMap[varName];
          edges.push({ from: sourceId, to: targetId, label: relation });
        }
      }
    }
  });

  return { nodes, edges };
}
