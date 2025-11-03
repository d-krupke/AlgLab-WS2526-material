import { Tooltip } from "bootstrap";
import "bootstrap/dist/css/bootstrap.min.css";
import * as d3 from "d3";
import "./style.css";
import type { BnBTree } from "./types/apiTypes";
import { getElement } from "./utils";

type BnBNode = d3.HierarchyNode<BnBTree>;
type BnBLink = d3.HierarchyLink<BnBTree>;

interface Dimensions {
  /** The inner width of the SVG. */
  width: number;
  /** The inner height of the SVG. */
  height: number;
}
interface TemplateMap {
  /** Mapping from iteration index of a node to an HTML string for that iteration. */
  [index: number]: string;
}

interface DomElements {
  /** The slider input element. */
  indexSlider: HTMLInputElement;
  /** The span displaying the slider value. */
  sliderValue: HTMLSpanElement;
  /** Button to increment the slider. */
  incrementButton: HTMLButtonElement;
  /** Button to decrement the slider. */
  decrementButton: HTMLButtonElement;
  /** The container for displaying iteration info. */
  iterationInfo: HTMLDivElement;
  /** The container for displaying iteration solution details. */
  iterationSolutionDetails: HTMLDivElement;
}

// Global variables -------------------------------------------------------------

const radius = 6; // circle r=6;
/**
 * Margins around the SVG content
 */
const margin = { top: 10, right: 90, bottom: 30, left: 90 };
/**
 * Hierarchical data representing the BnB tree. See class `BnBTree` in `visualization.py`
 */
let treeData: BnBTree;
/**
 * Mapping from iteration index to an HTML string with details for that iteration.
 */
let iterationInfo: TemplateMap;
/**
 * Mapping from iteration index to an HTML string with solution details.
 */
let iterationSolutionDetails: TemplateMap;
/**
 * Mapping from iteration index of a node to an HTML tooltip string for that iteration.
 */
let nodeTooltips: TemplateMap;
/**
 * Array of iteration indices used for mapping slider values to node details.
 */
let iterations: number[] = [];

// -------------------------------------------------------------

/**
 * Initializes and renders an interactive Branch-and-Bound tree using D3.
 * @param tree_data_param - Hierarchical data representing the BnB tree
 * @param node_details_param - Mapping from iteration index to an HTML string with details for that iteration.
 * @param node_tooltips_param - Mapping from iteration index of a node to an HTML tooltip string for that iteration.
 * @param iteration_info_param - Mapping from iteration index to an HTML string with details for that iteration.
 * @param iteration_solutions_param - Mapping from iteration index to an HTML string with solution details for that iteration.
 * @param iterations_param - Array of iteration indices used for mapping slider values to node details.
 */
function initialRender(
  tree_data_param: BnBTree,
  node_tooltips_param: TemplateMap,
  iteration_info_param: TemplateMap,
  iteration_solutions_param: TemplateMap,
  iterations_param: number[],
): void {
  treeData = tree_data_param;
  iterationInfo = iteration_info_param;
  iterationSolutionDetails = iteration_solutions_param;
  nodeTooltips = node_tooltips_param;
  iterations = iterations_param;

  const refs = getDomReferences();
  const dimensions = computeDimensions();

  const svg = createSvg(dimensions);
  const g = svg.append("g").attr("transform", `translate(${margin.left}, 0)`);

  const root = buildTreeLayout(dimensions);
  renderNodesAndLinks(root, g, refs);
  setupZoom(svg, g);

  setupSliderBehavior(refs, svg);
  setupSliderButtons(refs, svg);

  updateSliderDisplay(refs, svg);

  setupEyeIconToggle();
  setupTooltips();
  setupTableSort();
  setupResizePanels();
}

/**
 * Grabs and returns all necessary DOM references.
 */
function getDomReferences(): DomElements {
  return {
    indexSlider: getElement<HTMLInputElement>("#indexSlider"),
    sliderValue: getElement<HTMLSpanElement>("#sliderValue"),
    incrementButton: getElement<HTMLButtonElement>("#incrementButton"),
    decrementButton: getElement<HTMLButtonElement>("#decrementButton"),
    iterationInfo: getElement<HTMLDivElement>("#iteration-info"),
    iterationSolutionDetails: getElement<HTMLDivElement>("#iteration-solution-details"),
  };
}

/**
 * Computes and returns layout dimensions for the SVG.
 */
function computeDimensions(): Dimensions {
  const container = getElement<HTMLDivElement>(".graph-container");
  const width = container.getBoundingClientRect().width - margin.left - margin.right;
  const height = 0.8 * container.getBoundingClientRect().width - margin.bottom - margin.top;
  return { width, height };
}

/**
 * Creates and returns the SVG element with viewBox and size.
 * @param {Dimensions} dimensions - Layout dimensions
 */
function createSvg(dimensions: Dimensions) {
  return d3
    .select<SVGSVGElement, unknown>("#bnb-graph")
    .attr("viewBox", [
      0,
      0,
      dimensions.width + margin.left + margin.right,
      dimensions.height + margin.top + margin.bottom,
    ])
    .attr("width", "100%")
    .attr("height", "100%");
}

/**
 * Builds and returns the D3 tree layout based on the given data.
 * @param {Dimensions} dimensions - SVG layout dimensions
 */
function buildTreeLayout(dimensions: Dimensions) {
  const root = d3.hierarchy<BnBTree>(treeData);
  const treeLayout = d3.tree<BnBTree>().size([dimensions.width, dimensions.height]);
  treeLayout(root);
  return root;
}

/**
 * Renders the nodes and links of the tree.
 * @param {d3.HierarchyNode} root - D3 root node
 * @param {d3.Selection} g - Group container
 * @param {DomElements} refs - DOM references
 */
function renderNodesAndLinks(
  root: BnBNode,
  g: d3.Selection<SVGGElement, unknown, HTMLElement, any>,
  refs: DomElements,
) {
  g.selectAll<SVGPathElement, BnBLink>(".link")
    .data(root.links())
    .enter()
    .append("path")
    .attr("class", "link")
    .attr(
      "d",
      d3
        .linkHorizontal<BnBLink, BnBNode>()
        .x((d) => d.y ?? 0)
        .y((d) => d.x ?? 0),
    );

  const nodes = g
    .selectAll<SVGGElement, BnBNode>(".node")
    .data(root.descendants())
    .enter()
    .append("g")
    .attr("class", "node")
    .attr("transform", (d) => `translate(${d.y},${d.x})`);

  nodes
    .append("circle")
    .attr("r", radius)
    .style("fill", (d) => d.data.color)
    .style("cursor", (d) => {
      const processed_at = d.data.processed_at;
      return processed_at !== null ? "pointer" : "default";
    })
    .on("click", (_: MouseEvent, d) => {
      const processed_at = d.data.processed_at;
      if (processed_at === null) return;

      refs.indexSlider.value = String(processed_at);
      updateSliderDisplay(refs, d3.select("#bnb-graph"));
    })
    // Node tooltip
    .attr("data-bs-toggle", "tooltip")
    .attr("data-bs-custom-class", "node-tooltip")
    .attr("data-bs-title", (d) => {
      return nodeTooltips[d.data.node_id];
    });

  nodes
    .append("text")
    .attr("dy", "0.35em")
    .attr("x", (d) => (d.children ? -13 : 13))
    .style("text-anchor", (d) => (d.children ? "end" : "start"))
    .text((d) => d.data.label);
}

/**
 * Sets up zoom and pan behavior on the SVG.
 * @param {d3.Selection} svg - SVG element
 * @param {d3.Selection} g - Group container to transform
 */
function setupZoom(
  svg: d3.Selection<SVGSVGElement, unknown, HTMLElement, any>,
  g: d3.Selection<SVGGElement, unknown, HTMLElement, any>,
) {
  const zoom = d3
    .zoom<SVGSVGElement, unknown>()
    .scaleExtent([0.5, 8])
    .on("zoom", (event: any) => g.attr("transform", event.transform));
  svg.call(zoom).on("wheel", (event: WheelEvent) => event.preventDefault());
}

/**
 * Makes the node details table sortable using Tablesort.
 */
function setupTableSort() {
  new Tablesort(document.getElementById("instance-table"));
}

/**
 * Updates opacity of nodes, edges, and text based on slider position.
 * @param {HTMLInputElement} indexSlider - Slider input
 * @param {d3.Selection} svg - SVG selection to update
 */
function updateOpacity(indexSlider: HTMLInputElement, svg: d3.Selection<SVGSVGElement, unknown, HTMLElement, any>) {
  function getOpacity(d: BnBNode) {
    if (d.data.created_at > Number(indexSlider.value)) return 0.1;
    if (
      d.data.processed_at === null ||
      d.data.processed_at === undefined ||
      d.data.processed_at > Number(indexSlider.value)
    )
      return 0.5;
    return 1.0;
  }

  svg.selectAll<SVGCircleElement, BnBNode>(".node circle").style("opacity", getOpacity);

  svg.selectAll<SVGTextElement, BnBNode>(".node text").style("opacity", getOpacity);
  svg
    .selectAll<SVGPathElement, BnBLink>(".link")
    .style("opacity", (d) => Math.min(getOpacity(d.source), getOpacity(d.target)));
}

/**
 * Update the nodes after changing the current iteration
 * @param {HTMLInputElement} indexSlider
 * @param {d3.selection} svg
 */
function updateNodes(indexSlider: HTMLInputElement, svg: d3.Selection<SVGSVGElement, unknown, HTMLElement, any>) {
  svg
    .selectAll<SVGCircleElement, BnBNode>(".node circle")
    .attr("r", (d) => (d.data.processed_at === Number(indexSlider.value) ? radius * 1.8 : radius))
    .classed("current-node", (d) => d.data.processed_at === Number(indexSlider.value));

  updateOpacity(indexSlider, svg);
}

/**
 * Updates the slider text and every other element effected by an iteration change
 * @param {DomElements} refs
 * @param {d3.Selection} svg - SVG tree
 */
function updateSliderDisplay(refs: DomElements, svg: d3.Selection<SVGSVGElement, unknown, HTMLElement, any>) {
  const i = iterations[Number(refs.indexSlider.value)];

  refs.sliderValue.textContent = refs.indexSlider.value;

  const iteration_info = iterationInfo[i] || "No iteration info available.";
  refs.iterationInfo.innerHTML = iteration_info;
  new Tablesort(document.getElementById("iteration-table"));

  const iteration_solutions = iterationSolutionDetails[i] || "No iteration solution details available.";
  refs.iterationSolutionDetails.innerHTML = iteration_solutions;

  updateNodes(refs.indexSlider, svg);
}

/**
 * Sets up slider input behavior to trigger display updates.
 * @param {DomElements} refs
 * @param {d3.Selection} svg
 */
function setupSliderBehavior(refs: DomElements, svg: d3.Selection<SVGSVGElement, unknown, HTMLElement, any>) {
  refs.indexSlider.addEventListener("input", () => {
    updateSliderDisplay(refs, svg);
  });
}

/**
 * Configures increment and decrement buttons for the slider.
 * @param {DomElements} refs
 * @param {d3.Selection} svg
 */
function setupSliderButtons(refs: DomElements, svg: d3.Selection<SVGSVGElement, unknown, HTMLElement, any>) {
  refs.incrementButton.addEventListener("click", () => {
    if (Number(refs.indexSlider.value) < Number(refs.indexSlider.max)) {
      refs.indexSlider.value = String(Number(refs.indexSlider.value) + 1);
      updateSliderDisplay(refs, svg);
    }
  });

  refs.decrementButton.addEventListener("click", () => {
    if (Number(refs.indexSlider.value) > Number(refs.indexSlider.min)) {
      refs.indexSlider.value = String(Number(refs.indexSlider.value) - 1);
      updateSliderDisplay(refs, svg);
    }
  });
}

/**
 * Sets up Bootstrap toggle behavior for eye icons on collapsible sections.
 */
function setupEyeIconToggle() {
  document.addEventListener("show.bs.collapse", (event: Event) => {
    const target = event.target as HTMLElement | null;
    const icon = target ? document.querySelector(`.js-eye-icon[data-bs-target="#${target.id}"]`) : null;
    if (icon) {
      icon.classList.remove("bi-eye-slash-fill");
      icon.classList.add("bi-eye-fill");
    }
  });

  document.addEventListener("hide.bs.collapse", (event) => {
    const target = event.target as HTMLElement | null;
    const icon = target ? document.querySelector(`.js-eye-icon[data-bs-target="#${target.id}"]`) : null;
    if (icon) {
      icon.classList.remove("bi-eye-fill");
      icon.classList.add("bi-eye-slash-fill");
    }
  });
}

/**
 * Enables Bootstrap tooltips globally.
 */
function setupTooltips() {
  // Override the private bootstrap tooltip _leave method, so when hovering over the actual tooltip it stil shows
  //! This is just a monkey-patch, might change behavior in future bootstrap versions
  const originalLeave = Tooltip.prototype._leave;
  Tooltip.prototype._leave = function () {
    // Call the original to start the hide timeout
    originalLeave.call(this);

    const tip: HTMLElement = this.tip;
    const timeoutId: number = this._timeout;

    if (tip) {
      // When mouse enters the tooltip, cancel the hide
      tip.addEventListener(
        "mouseenter",
        () => {
          clearTimeout(timeoutId);

          // When mouse leaves tooltip, finally hide the tooltip
          tip.addEventListener(
            "mouseleave",
            () => {
              this.hide();
            },
            { once: true },
          );
        },
        { once: true },
      );
    }
  };

  // Enable Bootstrap tooltips
  const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
  tooltipTriggerList.map((el) => {
    const tooltip = new Tooltip(el, {
      html: true, // Enable HTML Tags in the tooltips
      delay: { show: 50, hide: 200 },
    });

    return tooltip;
  });
}

// Enable drag resizing of horizontal split panels
function setupResizePanels() {
  document.querySelectorAll<HTMLDivElement>(".split-container").forEach((container) => {
    const panelDividerSelector = container.dataset.panelDivider ? container.dataset.panelDivider : ".panel-divider";
    const divider = getElement<HTMLDivElement>(panelDividerSelector, container);
    const left = getElement<HTMLDivElement>(".panel-left", container); // Left Panel

    let isResizing = false;

    // When clicking the divider
    divider.addEventListener("mousedown", (_: MouseEvent) => {
      isResizing = true;
      document.body.style.cursor = "col-resize";
      divider.classList.add("active");

      // Add event listeners
      document.addEventListener("mousemove", onMouseMove);
      document.addEventListener("mouseup", onMouseUp);

      /**
       * Moving mouse -> resizing
       */
      function onMouseMove(event: MouseEvent) {
        if (!isResizing) return;

        // Calculate relative position to the left container-edge
        const rect = container.getBoundingClientRect();
        // If mouse is on the right outside the split container, dont resize. Otherwise the container grows infinitely
        if (rect.right <= event.clientX) return;

        left.style.flexBasis = event.clientX - rect.left + "px";
      }

      /**
       * Mouse up -> resizing done
       */
      function onMouseUp(__: MouseEvent) {
        isResizing = false;
        document.body.style.cursor = "default";
        divider.classList.remove("active");

        // Remove Event-Listeners
        document.removeEventListener("mousemove", onMouseMove);
        document.removeEventListener("mouseup", onMouseUp);
      }
    });
  });
}

document.addEventListener("DOMContentLoaded", () => {
  const data = BNB_DATA;
  initialRender(
    data.treeData,
    data.node_tooltips,
    data.iteration_info,
    data.iteration_solution_details,
    data.iterations,
  );
});
