declare module "tablesort" {
  /** options for the constructor or init() */
  export interface TablesortOptions {
    sortAttribute?: string;
    descending?: boolean;
  }
  /** the live instance returned by new Tablesort(...) */
  export interface TablesortInstance {
    init(el: HTMLTableElement, options?: TablesortOptions): void;
    sortTable(header: HTMLTableCellElement, update?: boolean): void;
    refresh(): void;
    table: HTMLTableElement;
    thead: boolean;
    options: TablesortOptions;
    current?: HTMLTableCellElement;
    col?: number;
  }
  /** the constructor + .extend API */
  export interface TablesortStatic {
    new (el: HTMLTableElement, options?: TablesortOptions): TablesortInstance;
    extend(name: string, pattern: (cellText: string) => boolean, sortFn: (a: string, b: string) => number): void;
  }
  const Tablesort: TablesortStatic;
  export default Tablesort;
}
