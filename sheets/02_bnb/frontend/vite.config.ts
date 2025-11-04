import path from "path";
import { defineConfig } from "vite";

// https://vitejs.dev/config/
export default defineConfig({
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
