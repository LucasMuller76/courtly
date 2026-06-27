import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  async rewrites() {
    // Redireciona /api/* para o backend FastAPI
    // O browser vê tudo como localhost:3000, então cookies funcionam normalmente
    const apiUrl = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
    return [
      {
        source: "/api/:path*",
        destination: `${apiUrl}/api/:path*`,
      },
    ];
  },
};

export default nextConfig;