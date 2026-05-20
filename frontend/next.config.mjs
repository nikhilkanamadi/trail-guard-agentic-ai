/** @type {import('next').NextConfig} */
const nextConfig = {
  // Expose the backend API URL to the browser
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000",
  },

  // Proxy /api/v1/* → backend so the browser never hits CORS in production.
  // On Vercel, set NEXT_PUBLIC_API_URL to your deployed backend base URL.
  async rewrites() {
    const backendUrl = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
    return [
      {
        source: "/api/v1/:path*",
        destination: `${backendUrl}/api/v1/:path*`,
      },
    ];
  },
};

export default nextConfig;
