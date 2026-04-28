import type { MetadataRoute } from "next";

import { NICHE_PACKS } from "@/lib/pricing";

const SITE_URL = (
  process.env.NEXT_PUBLIC_SITE_URL ||
  process.env.NEXTAUTH_URL ||
  "https://assistent-cf91.onrender.com"
).replace(/\/$/, "");

export default function sitemap(): MetadataRoute.Sitemap {
  const lastModified = new Date();

  const root: MetadataRoute.Sitemap = [
    {
      url: `${SITE_URL}/`,
      lastModified,
      changeFrequency: "weekly",
      priority: 1,
    },
    {
      url: `${SITE_URL}/studio`,
      lastModified,
      changeFrequency: "monthly",
      priority: 0.7,
    },
  ];

  const niches: MetadataRoute.Sitemap = NICHE_PACKS.map((p) => ({
    url: `${SITE_URL}/n/${p.slug}`,
    lastModified,
    changeFrequency: "monthly",
    priority: 0.8,
  }));

  return [...root, ...niches];
}
