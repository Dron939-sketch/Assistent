/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  swcMinify: true,
  images: {
    remotePatterns: [
      { protocol: 'https', hostname: 'vk.com' },
      { protocol: 'https', hostname: '**.userapi.com' },
    ],
  },
};

module.exports = nextConfig;
