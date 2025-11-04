from pydantic2ts import generate_typescript_defs

generate_typescript_defs("../knapsack_bnb/visualization.py", "./src/types/apiTypes.ts")