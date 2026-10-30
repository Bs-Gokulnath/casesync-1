import type { NextConfig } from "next";

// Cache Components (Next 16's opt-in PPR model) is deliberately left off:
// every route in this app is behind auth and reads per-request DB state, so
// there is no meaningfully static shell to gain from it, and it would force
// a Suspense boundary around nearly every data read for no benefit. We use
// the previous/stable model instead: reading cookies()/headers() already
// opts a route into dynamic rendering with no extra ceremony.
const nextConfig: NextConfig = {
  turbopack: {
    rules: {
      "*.css": {
        loaders: ["@tailwindcss/turbopack"],
        as: "*.css",
      },
    },
  },
  async rewrites() {
    const apiUrl = process.env.API_INTERNAL_URL ?? "http://localhost:8000";
    return [
      {
        source: "/api/:path*",
        destination: `${apiUrl}/api/:path*`,
      },
    ];
  },
};

export default nextConfig;
