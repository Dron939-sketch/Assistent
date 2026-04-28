import Link from "next/link";
import { notFound } from "next/navigation";
import type { Metadata } from "next";
import { Check, Lock, Shield } from "lucide-react";

import { Addons } from "@/components/landing/Addons";
import { EarlyAccessDialog } from "@/components/landing/EarlyAccessDialog";
import { FAQ } from "@/components/landing/FAQ";
import { SiteFooter } from "@/components/landing/SiteFooter";
import { Tiers } from "@/components/landing/Tiers";
import { NICHE_PACKS } from "@/lib/pricing";

interface PageParams {
  params: { slug: string };
}

export function generateStaticParams() {
  return NICHE_PACKS.map((p) => ({ slug: p.slug }));
}

export function generateMetadata({ params }: PageParams): Metadata {
  const niche = NICHE_PACKS.find((p) => p.slug === params.slug);
  if (!niche) return {};

  return {
    title: niche.seo.title,
    description: niche.seo.description,
    alternates: { canonical: `/n/${niche.slug}` },
    openGraph: {
      type: "website",
      siteName: "FishFlow",
      title: niche.seo.title,
      description: niche.seo.description,
      url: `/n/${niche.slug}`,
      locale: "ru_RU",
    },
    twitter: {
      card: "summary_large_image",
      title: niche.seo.title,
      description: niche.seo.description,
    },
  };
}

export default function NichePage({ params }: PageParams) {
  const niche = NICHE_PACKS.find((p) => p.slug === params.slug);
  if (!niche) notFound();

  return (
    <main className="min-h-screen bg-gray-50 text-gray-900">
      <header className="sticky top-0 z-30 border-b border-gray-200 bg-white/90 backdrop-blur">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
          <Link href="/" className="text-lg font-semibold">
            FishFlow
          </Link>
          <nav className="hidden gap-6 text-sm text-gray-600 sm:flex">
            <Link href="/" className="hover:text-gray-900">
              Главная
            </Link>
            <Link href="/#tiers" className="hover:text-gray-900">
              Тарифы
            </Link>
            <Link href="/studio" className="hover:text-gray-900">
              White-label
            </Link>
          </nav>
          <EarlyAccessDialog
            trigger={
              <button
                type="button"
                className="rounded-md bg-primary px-4 py-2 text-sm font-medium text-white hover:bg-primary/90"
              >
                Ранний доступ
              </button>
            }
          />
        </div>
      </header>

      <section className="mx-auto max-w-3xl px-6 pb-16 pt-16 text-center">
        <div className="mb-4 inline-flex items-center gap-2 rounded-full border border-gray-200 bg-white px-3 py-1 text-xs font-medium text-gray-700 shadow-sm">
          <span className="text-base" aria-hidden>
            {niche.emoji}
          </span>
          {niche.name}
          {niche.compliance && (
            <span className="inline-flex items-center gap-1 text-amber-700">
              <Shield className="h-3 w-3" />
              compliance
            </span>
          )}
        </div>
        <h1 className="text-4xl font-bold tracking-tight sm:text-5xl">
          {niche.seo.h1}
        </h1>
        <p className="mx-auto mt-4 max-w-2xl text-lg text-gray-600">
          {niche.seo.subhead}
        </p>

        <div className="mt-6 flex flex-wrap justify-center gap-1.5">
          {niche.professions.map((p) => (
            <span
              key={p}
              className="rounded-full border border-gray-200 bg-white px-2.5 py-1 text-xs text-gray-700 shadow-sm"
            >
              {p}
            </span>
          ))}
        </div>

        <div className="mt-8 flex flex-col items-center gap-3 sm:flex-row sm:justify-center">
          <EarlyAccessDialog
            trigger={
              <button
                type="button"
                className="inline-flex items-center justify-center rounded-md bg-primary px-5 py-3 text-sm font-medium text-white hover:bg-primary/90"
              >
                Получить ранний доступ
              </button>
            }
          />
          <Link
            href="#value"
            className="inline-flex items-center justify-center rounded-md border border-gray-300 bg-white px-5 py-3 text-sm font-medium text-gray-700 hover:bg-gray-100"
          >
            Что мы делаем для этой ниши
          </Link>
        </div>
      </section>

      <section className="mx-auto max-w-5xl scroll-mt-24 px-6 pb-20">
        <header className="mb-8 text-center">
          <h2 className="text-2xl font-semibold">Как это болит сейчас</h2>
          <p className="mt-2 text-sm text-gray-600">
            Мы слышали это от десятков специалистов в нише — и сделали ассистент,
            который снимает каждую боль.
          </p>
        </header>
        <ul className="grid grid-cols-1 gap-4 sm:grid-cols-2">
          {niche.painPoints.map((p) => (
            <li
              key={p}
              className="flex items-start gap-3 rounded-lg border border-gray-200 bg-white p-5 shadow-sm"
            >
              <Lock className="mt-0.5 h-5 w-5 shrink-0 text-rose-500" />
              <span className="text-sm text-gray-800">{p}</span>
            </li>
          ))}
        </ul>
      </section>

      <section
        id="value"
        className="mx-auto max-w-5xl scroll-mt-24 px-6 pb-20"
      >
        <header className="mb-8 text-center">
          <h2 className="text-2xl font-semibold">Что вы получаете</h2>
          <p className="mt-2 text-sm text-gray-600">
            Готовый набор, заточенный именно под вашу нишу — а не общий
            «AI-ассистент для всех».
          </p>
        </header>
        <ul className="grid grid-cols-1 gap-4 sm:grid-cols-2">
          {niche.keyValue.map((v) => (
            <li
              key={v}
              className="flex items-start gap-3 rounded-lg border border-gray-200 bg-white p-5 shadow-sm"
            >
              <Check className="mt-0.5 h-5 w-5 shrink-0 text-emerald-600" />
              <span className="text-sm text-gray-800">{v}</span>
            </li>
          ))}
        </ul>

        <div className="mt-6 rounded-lg border border-dashed border-gray-300 bg-white p-5 text-sm text-gray-700 shadow-sm">
          <p>
            <span className="font-medium">Голос по умолчанию:</span>{" "}
            {niche.exampleVoice}.
          </p>
          <p className="mt-2">
            <span className="font-medium">Пример марафона под ключ:</span>{" "}
            «{niche.exampleMarathon}».
          </p>
          <p className="mt-2 text-gray-600">
            <span className="font-medium">AI не пишет про:</span>{" "}
            {niche.forbidden}.
          </p>
          {niche.compliance && (
            <p className="mt-3 inline-flex items-center gap-2 rounded-md bg-amber-50 px-3 py-1.5 text-xs font-medium text-amber-800">
              <Shield className="h-3.5 w-3.5" />
              Регулируемая ниша — рекомендуем подключить Compliance Pack
            </p>
          )}
        </div>
      </section>

      <section className="mx-auto max-w-6xl scroll-mt-24 px-6 pb-20">
        <header className="mb-8 text-center">
          <h2 className="text-2xl font-semibold">Тарифы</h2>
          <p className="mt-2 text-sm text-gray-600">
            Никакого специального прайса для ниши — обычные Start / Pro /
            Expert. Niche Pack и Compliance Pack — отдельными аддонами.
          </p>
        </header>
        <Tiers />
        <p className="mt-6 text-center text-xs text-gray-500">
          14 дней бесплатно. Годовая подписка — скидка 20%.
        </p>
      </section>

      <section className="mx-auto max-w-6xl scroll-mt-24 px-6 pb-20">
        <header className="mb-8 text-center">
          <h2 className="text-2xl font-semibold">Полезные расширения</h2>
        </header>
        <Addons />
      </section>

      <section className="mx-auto max-w-3xl scroll-mt-24 px-6 pb-20">
        <header className="mb-8 text-center">
          <h2 className="text-2xl font-semibold">Частые вопросы</h2>
        </header>
        <FAQ />
      </section>

      <section className="bg-gray-900 py-16 text-center text-white">
        <div className="mx-auto max-w-2xl px-6">
          <h2 className="text-2xl font-semibold">Готовы попробовать?</h2>
          <p className="mt-2 text-sm text-gray-300">
            Расскажем, как настроить под вашу практику за 30 минут.
          </p>
          <div className="mt-6 flex justify-center">
            <EarlyAccessDialog
              trigger={
                <button
                  type="button"
                  className="rounded-md bg-white px-5 py-3 text-sm font-medium text-gray-900 hover:bg-gray-100"
                >
                  Получить ранний доступ
                </button>
              }
            />
          </div>
        </div>
      </section>

      <SiteFooter />
    </main>
  );
}
