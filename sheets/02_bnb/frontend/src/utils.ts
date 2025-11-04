/**
 * Returns the first element that is a descendant of `container` that matches `selectors`.
 */
export function getElement<T extends HTMLElement>(selectors: string, container: ParentNode = document): T {
  const element = container.querySelector<T>(selectors);
  if (!element) {
    throw new Error(`HTML Element with selector ${selectors} not found`);
  }
  return element;
}