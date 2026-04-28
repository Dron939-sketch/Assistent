import type { Metadata, Viewport } from "next";
import { Inter } from "next/font/google";
import Script from "next/script";

import "./globals.css";
import { Providers } from "@/components/providers";
import { Toaster } from "react-hot-toast";

const inter = Inter({ subsets: ["latin", "cyrillic"], display: "swap" });

const SITE_URL = (
  process.env.NEXT_PUBLIC_SITE_URL ||
  process.env.NEXTAUTH_URL ||
  "https://assistent-cf91.onrender.com"
).replace(/\/$/, "");

const PLAUSIBLE_DOMAIN = process.env.NEXT_PUBLIC_PLAUSIBLE_DOMAIN;

const TITLE = "FishFlow — AI-ассистент эксперта";
const DESCRIPTION =
  "AI-ассистент для 65+ экспертных профессий. Приводим клиентов из ВКонтакте и Telegram, пишем посты в вашем голосе, ведём марафоны и подсказываем точки роста.";

export const metadata: Metadata = {
  metadataBase: new URL(SITE_URL),
  title: {
    default: TITLE,
    template: "%s · FishFlow",
  },
  description: DESCRIPTION,
  applicationName: "FishFlow",
  keywords: [
    "AI-ассистент эксперта",
    "автоворонка ВКонтакте",
    "генератор постов",
    "марафоны под ключ",
    "FishFlow",
    "психолог онлайн",
    "нутрициолог онлайн",
    "AI для тарологов",
  ],
  authors: [{ name: "FishFlow" }],
  alternates: {
    canonical: "/",
  },
  openGraph: {
    type: "website",
    siteName: "FishFlow",
    title: TITLE,
    description: DESCRIPTION,
    url: "/",
    locale: "ru_RU",
  },
  twitter: {
    card: "summary_large_image",
    title: TITLE,
    description: DESCRIPTION,
  },
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
    },
  },
  icons: {
    icon: "/favicon.ico",
  },
};

export const viewport: Viewport = {
  themeColor: [
    { media: "(prefers-color-scheme: light)", color: "#ffffff" },
    { media: "(prefers-color-scheme: dark)", color: "#0f172a" },
  ],
  width: "device-width",
  initialScale: 1,
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="ru" suppressHydrationWarning>
      <body className={inter.className}>
        <Providers>
          {children}
          <Toaster position="top-right" />
        </Providers>
        {PLAUSIBLE_DOMAIN ? (
          <Script
            strategy="afterInteractive"
            src="https://plausible.io/js/script.js"
            data-domain={PLAUSIBLE_DOMAIN}
          />
        ) : null}
      </body>
    </html>
  );
}
