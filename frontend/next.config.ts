import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Minimal self-contained server output for production Docker images —
  // avoids shipping the full node_modules tree in the runtime image.
  output: "standalone",
};

export default nextConfig;
