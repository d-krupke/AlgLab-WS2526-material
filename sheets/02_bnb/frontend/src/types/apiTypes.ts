/* tslint:disable */
/* eslint-disable */
/**
/* This file was automatically generated from pydantic models by running pydantic2ts.
/* Do not modify it by hand - just update the pydantic models and then re-run the script
*/

/**
 * Provides a structure for the branch-and-bound tree. Because of its recursive nature,
 * every node is a BnBTree object, and the children of a node are stored in a list of BnBTree objects.
 */
export interface BnBTree {
  /**
   * The ID of the root node.
   */
  node_id: number;
  /**
   * The lower bound of the node from the heuristic solution. May also be None if it got pruned.
   */
  lb?: number | null;
  /**
   * The upper bound from the relaxed solution. May also be None if it got pruned.
   */
  ub?: number | null;
  /**
   * The time when the node was created.
   */
  created_at: number;
  /**
   * The time when the node was processed. This may be later than its creation time. It may also be None if it got pruned.
   */
  processed_at?: number | null;
  /**
   * Label of the node in the visualization.
   */
  label: string;
  /**
   * Status of the node in the visualization.
   */
  status: "integral" | "infeasible" | "feasible";
  /**
   * Color of the node in the visualization.
   */
  color: string;
  /**
   * Children of the node.
   */
  children?: BnBTree[];
}
/**
 * Represents an instance with a list of items and capacity of the knapsack problem.
 */
export interface Instance {
  /**
   * List of items in the knapsack problem instance
   */
  items?: Item[];
  /**
   * Capacity of the knapsack problem instance
   */
  capacity: number;
  /**
   * Id of the instance
   */
  id?: number;
}
/**
 * Represents an item with a weight and a value for the knapsack problem.
 */
export interface Item {
  /**
   * Weight of the item
   */
  weight: number;
  /**
   * Value of the item
   */
  value: number;
}
