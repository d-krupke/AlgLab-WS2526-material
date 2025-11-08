import path from "path";
import { defineConfig } from "vite";

// https://vitejs.dev/config/
export default defineConfig({
  // Make all URLs in the built CSS/JS relative instead of absolute. Important for bootstrap icons not finding woff files
  base: "./",

  build: {
    outDir: path.resolve(__dirname, "../knapsack_bnb/static/"),
    emptyOutDir: true,
    rolldownOptions: {
      input: path.resolve(__dirname, "src/bnb.ts"),
      output: {
        entryFileNames: "bnb.js",
        assetFileNames: "[name].[ext]",
      },
    },
  },
});
