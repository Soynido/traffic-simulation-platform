/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  swcMinify: true,
  output: 'standalone',
  // experimental options cleaned (appDir is default in app router)
  env: {
    API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1',
  },
  // Proxy pour rediriger les appels API vers le backend
  async rewrites() {
    return [
      {
        source: '/api/v1/:path*',
        destination: process.env.API_URL ? `${process.env.API_URL}/:path*` : 'http://backend:8000/api/v1/:path*',
      },
    ];
  },
  // Autoriser tous les hosts en développement
  experimental: {
    allowedRevalidateHeaderKeys: ['host'],
  },
  // CORS headers for API routes
  async headers() {
    return [
      {
        source: '/api/:path*',
        headers: [
          { key: 'Access-Control-Allow-Origin', value: '*' },
          { key: 'Access-Control-Allow-Methods', value: 'GET, POST, PUT, DELETE, OPTIONS' },
          { key: 'Access-Control-Allow-Headers', value: 'Content-Type, Authorization' },
        ],
      },
    ];
  },
  webpack: (config, { isServer }) => {
    if (!isServer) {
      config.resolve.fallback = {
        ...config.resolve.fallback,
        fs: false,
        net: false,
        tls: false,
      };
    }
    return config;
  },
};

module.exports = nextConfig;
