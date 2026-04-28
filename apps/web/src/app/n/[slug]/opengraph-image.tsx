import { ImageResponse } from "next/og";

import { NICHE_PACKS } from "@/lib/pricing";

export const runtime = "edge";
export const size = { width: 1200, height: 630 };
export const contentType = "image/png";

export function generateImageMetadata({
  params,
}: {
  params: { slug: string };
}) {
  const niche = NICHE_PACKS.find((p) => p.slug === params.slug);
  return [
    {
      id: params.slug,
      contentType,
      size,
      alt: niche?.seo.title ?? "FishFlow",
    },
  ];
}

export default function NicheOG({ params }: { params: { slug: string } }) {
  const niche = NICHE_PACKS.find((p) => p.slug === params.slug);
  const title = niche?.seo.h1 ?? "FishFlow";
  const subhead =
    niche?.seo.subhead ?? "AI-ассистент для 65+ экспертных профессий";
  const emoji = niche?.emoji ?? "✨";
  const tags = niche?.professions.slice(0, 4) ?? [];

  return new ImageResponse(
    (
      <div
        style={{
          width: "100%",
          height: "100%",
          display: "flex",
          flexDirection: "column",
          justifyContent: "space-between",
          padding: "64px 72px",
          background:
            "linear-gradient(135deg, #0f172a 0%, #1e293b 60%, #2563eb 100%)",
          color: "#f8fafc",
          fontFamily: "Inter, system-ui, sans-serif",
        }}
      >
        <div
          style={{
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
          }}
        >
          <div style={{ display: "flex", alignItems: "center", gap: 16 }}>
            <div
              style={{
                width: 56,
                height: 56,
                borderRadius: 16,
                background: "#22d3ee",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                fontSize: 32,
                fontWeight: 700,
                color: "#0f172a",
              }}
            >
              FF
            </div>
            <span style={{ fontSize: 32, fontWeight: 600 }}>FishFlow</span>
          </div>
          <span
            style={{
              fontSize: 64,
              lineHeight: 1,
            }}
          >
            {emoji}
          </span>
        </div>

        <div style={{ display: "flex", flexDirection: "column", gap: 18 }}>
          <span
            style={{
              fontSize: 60,
              fontWeight: 700,
              lineHeight: 1.1,
            }}
          >
            {title}
          </span>
          <span
            style={{
              fontSize: 26,
              color: "#cbd5f5",
              lineHeight: 1.4,
              maxWidth: 1000,
            }}
          >
            {subhead}
          </span>
        </div>

        <div
          style={{
            display: "flex",
            flexWrap: "wrap",
            gap: 10,
            fontSize: 22,
            color: "#0f172a",
          }}
        >
          {tags.map((t) => (
            <span
              key={t}
              style={{
                background: "#22d3ee",
                padding: "8px 16px",
                borderRadius: 999,
                fontWeight: 600,
              }}
            >
              {t}
            </span>
          ))}
        </div>
      </div>
    ),
    size,
  );
}
