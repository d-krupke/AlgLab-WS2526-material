import type { nodeRelaxedStatus } from "./types/customTypes";

export const radius = 7; // circle r=6;
/**
 * Margins around the SVG content
 */
export const margin = { top: 10, right: 90, bottom: 30, left: 90 } as const;

/**
 * Mapping from node relaxed status to the node color.
 */
export const nodeColorsDict = {
  feasible: "#adb5bd",
  "feasible+integral": "#20c997",
  infeasible: "#dc3545",
} as const satisfies Record<nodeRelaxedStatus, string>;
