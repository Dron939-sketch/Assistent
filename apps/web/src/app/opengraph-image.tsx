import { ImageResponse } from "next/og";

export const runtime = "edge";
export const size = { width: 1200, height: 630 };
export const contentType = "image/png";
export const alt = "FishFlow — AI-ассистент эксперта";

export default function OpenGraphImage() {
  return new ImageResponse(
    (
      <div
        style={{
          width: "100%",
          height: "100%",
          display: "flex",
          flexDirection: "column",
          justifyContent: "space-between",
          padding: "72px 80px",
          background:
            "linear-gradient(135deg, #0f172a 0%, #1e293b 60%, #2563eb 100%)",
          color: "#f8fafc",
          fontFamily: "Inter, system-ui, sans-serif",
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

        <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
          <span
            style={{
              fontSize: 24,
              color: "#22d3ee",
              fontWeight: 600,
              letterSpacing: 1,
              textTransform: "uppercase",
            }}
          >
            AI-ассистент для 65+ экспертных профессий
          </span>
          <span
            style={{
              fontSize: 80,
              fontWeight: 700,
              lineHeight: 1.1,
            }}
          >
            Ваша экспертиза.
            <br />
            Наш ассистент.
            <br />
            <span style={{ color: "#22d3ee" }}>Клиенты — каждый день.</span>
          </span>
        </div>

        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            fontSize: 22,
            color: "#cbd5f5",
          }}
        >
          <span>Заявки · Контент · Марафоны · Аналитика</span>
          <span>fishflow.ru</span>
        </div>
      </div>
    ),
    size,
  );
}
