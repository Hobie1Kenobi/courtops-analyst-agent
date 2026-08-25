/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  eslint: {
    // Do not fail the production build on lint errors/config resolution issues.
    ignoreDuringBuilds: true,
  },
};

export default nextConfig;

