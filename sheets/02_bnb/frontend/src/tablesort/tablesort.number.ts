/*!
 * tablesort v5.6.0 (2025-04-20)
 * http://tristen.ca/tablesort/demo/
 * Copyright (c) 2025 ; Licensed MIT
 *
 * Copied and modified from node_modules/tablesort/dist/tablesort.number.js
 */
import Tablesort from "tablesort";

function cleanNumber(i: string) {
  return i.replace(/[^\-?0-9.]/g, "");
}

function compareNumber(a: string, b: string) {
  let fa = parseFloat(a);
  let fb = parseFloat(b);

  fa = isNaN(fa) ? 0 : fa;
  fb = isNaN(fb) ? 0 : fb;

  return fa - fb;
}

Tablesort.extend(
  "number",
  function (item: string) {
    return (
      item.match(/^[-+]?[£\x24Û¢´€]?\d+\s*([,\.]\d{0,2})/) || // Prefixed currency
      item.match(/^[-+]?\d+\s*([,\.]\d{0,2})?[£\x24Û¢´€]/) || // Suffixed currency
      item.match(/^[-+]?(\d)*-?([,\.]){0,1}-?(\d)+([E,e][\-+][\d]+)?%?$/)
    ); // Number
  },
  function (a: string, b: string) {
    a = cleanNumber(a);
    b = cleanNumber(b);

    return compareNumber(b, a);
  }
);
