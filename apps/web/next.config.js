/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'standalone',
  reactStrictMode: true,
  swcMinify: true,
  images: {
    domains: ['vk.com', 'sun9-*.userapi.com', 'localhost'],
  },
  experimental: {
    serverActions: true,
  },
};

module.exports = nextConfig;
