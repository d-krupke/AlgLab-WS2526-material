import type { BnBTree } from "./apiTypes";

/* Type aliases */
export type BnBNode = d3.HierarchyNode<BnBTree>;
export type BnBLink = d3.HierarchyLink<BnBTree>;
export type nodeRelaxedStatus = BnBTree["status"];

export interface Dimensions {
  /** The inner width of the SVG. */
  width: number;
  /** The inner height of the SVG. */
  height: number;
}
export interface TemplateMap {
  /** Mapping from iteration index of a node to an HTML string for that iteration. */
  [index: number]: string;
}
