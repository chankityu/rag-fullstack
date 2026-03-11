/** @type {import('next').NextConfig} */
const nextConfig = {
  async rewrites() {
    return [
      {
        source: "/chat",
        destination: "http://localhost:8000/chat",
      },
    ];
  },
};

module.exports = nextConfig;