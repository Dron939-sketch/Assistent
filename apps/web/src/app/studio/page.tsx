import Link from "next/link";
import { Check } from "lucide-react";

import { EarlyAccessDialog } from "@/components/landing/EarlyAccessDialog";
import { SiteFooter } from "@/components/landing/SiteFooter";
import { STUDIO_PLANS, STUDIO_SETUP_FEE } from "@/lib/pricing";

export const metadata = {
  title: "FishFlow Studio — White-label платформа для нишевых операторов",
  description:
    "Запустите свой AI-ассистент под брендом для психологов, нутрициологов, тарологов или любой другой ниши. Готовый движок, ваш домен, ваши клиенты.",
};

const VALUE = [
  "Готовый движок под вашим брендом и доменом",
  "Кастомный нишевый Pack: голос, словарь, шаблоны",
  "Биллинг и подписки берём на себя — или интегрируемся с вашим",
  "Месячная отчётность по экспертам, выручке, оттоку",
  "Запуск за 2–4 недели",
];

const HOW = [
  {
    title: "Брифинг 30 минут",
    body: "Вы рассказываете про нишу, идею бренда и целевого эксперта.",
  },
  {
    title: "Настройка тенанта",
    body: "Мы собираем поддомен, лого, цветовую схему, голос AI и нишевые шаблоны.",
  },
  {
    title: "Пилот 30 дней",
    body: "Подключаем 5–10 первых экспертов. Вы видите метрики и LTV в реальном времени.",
  },
  {
    title: "Масштабирование",
    body: "Подключаете маркетинг и рост. Мы держим инфраструктуру и AI-стек.",
  },
];

export default function StudioPage() {
  return (
    <main className="min-h-screen bg-gray-50 text-gray-900">
      <header className="sticky top-0 z-30 border-b border-gray-200 bg-white/90 backdrop-blur">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
          <Link href="/" className="text-lg font-semibold">
            FishFlow
          </Link>
          <nav className="hidden gap-6 text-sm text-gray-600 sm:flex">
            <Link href="/" className="hover:text-gray-900">
              Для эксперта
            </Link>
            <a href="#plans" className="hover:text-gray-900">
              Тарифы Studio
            </a>
            <a href="#how" className="hover:text-gray-900">
              Как запускаем
            </a>
          </nav>
          <EarlyAccessDialog
            trigger={
              <button
                type="button"
                className="rounded-md bg-primary px-4 py-2 text-sm font-medium text-white hover:bg-primary/90"
              >
                Получить демо
              </button>
            }
          />
        </div>
      </header>

      <section className="mx-auto max-w-3xl px-6 pb-20 pt-16 text-center">
        <span className="inline-flex items-center gap-2 rounded-full border border-gray-200 bg-white px-3 py-1 text-xs font-medium text-gray-700 shadow-sm">
          FishFlow Studio · White-label
        </span>
        <h1 className="mt-4 text-4xl font-bold tracking-tight sm:text-5xl">
          Запустите свой AI-ассистент
          <span className="block text-primary">для вашей ниши</span>
        </h1>
        <p className="mx-auto mt-4 max-w-xl text-lg text-gray-600">
          Берёте готовый движок FishFlow, настраиваете под нишу и бренд,
          запускаете за 2–4 недели. Биллинг, AI-инфраструктура, поддержка —
          на нас.
        </p>

        <div className="mt-8 flex flex-col items-center gap-3 sm:flex-row sm:justify-center">
          <EarlyAccessDialog
            trigger={
              <button
                type="button"
                className="inline-flex items-center justify-center rounded-md bg-primary px-5 py-3 text-sm font-medium text-white hover:bg-primary/90"
              >
                Поговорить с командой
              </button>
            }
          />
          <a
            href="#plans"
            className="inline-flex items-center justify-center rounded-md border border-gray-300 bg-white px-5 py-3 text-sm font-medium text-gray-700 hover:bg-gray-100"
          >
            Посмотреть тарифы
          </a>
        </div>
      </section>

      <section className="mx-auto max-w-4xl px-6 pb-20">
        <header className="mb-8 text-center">
          <h2 className="text-2xl font-semibold">Что вы получаете</h2>
        </header>
        <ul className="mx-auto max-w-2xl space-y-3">
          {VALUE.map((v) => (
            <li
              key={v}
              className="flex items-start gap-3 rounded-lg border border-gray-200 bg-white p-4 shadow-sm"
            >
              <Check className="mt-0.5 h-5 w-5 shrink-0 text-emerald-600" />
              <span className="text-sm text-gray-800">{v}</span>
            </li>
          ))}
        </ul>
      </section>

      <section id="how" className="mx-auto max-w-4xl scroll-mt-24 px-6 pb-20">
        <header className="mb-8 text-center">
          <h2 className="text-2xl font-semibold">Как запускаем</h2>
          <p className="mt-2 text-sm text-gray-600">
            Простой и предсказуемый процесс — без подвешенных пилотов на
            полгода.
          </p>
        </header>
        <ol className="grid grid-cols-1 gap-4 sm:grid-cols-2">
          {HOW.map((step, i) => (
            <li
              key={step.title}
              className="rounded-lg border border-gray-200 bg-white p-5 shadow-sm"
            >
              <span className="inline-flex h-7 w-7 items-center justify-center rounded-full bg-gray-900 text-xs font-semibold text-white">
                {i + 1}
              </span>
              <h3 className="mt-3 text-base font-semibold text-gray-900">
                {step.title}
              </h3>
              <p className="mt-2 text-sm text-gray-700">{step.body}</p>
            </li>
          ))}
        </ol>
      </section>

      <section id="plans" className="mx-auto max-w-6xl scroll-mt-24 px-6 pb-20">
        <header className="mb-8 text-center">
          <h2 className="text-2xl font-semibold">Тарифы Studio</h2>
          <p className="mx-auto mt-2 max-w-2xl text-sm text-gray-600">
            Setup fee {STUDIO_SETUP_FEE.toLocaleString("ru-RU")} ₽ — оплата
            кастомизации и онбординга. Окупается с первого месяца.
          </p>
        </header>

        <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
          {STUDIO_PLANS.map((p) => (
            <article
              key={p.id}
              className="flex flex-col rounded-xl border border-gray-200 bg-white p-6 shadow-sm"
            >
              <h3 className="text-lg font-semibold text-gray-900">{p.name}</h3>
              <p className="mt-2 text-2xl font-bold text-gray-900">{p.price}</p>
              <ul className="mt-5 flex-1 space-y-2 text-sm text-gray-800">
                {p.details.map((d) => (
                  <li key={d} className="flex items-start gap-2">
                    <Check className="mt-0.5 h-4 w-4 shrink-0 text-emerald-600" />
                    <span>{d}</span>
                  </li>
                ))}
              </ul>
              <EarlyAccessDialog
                trigger={
                  <button
                    type="button"
                    className="mt-6 w-full rounded-md bg-gray-900 px-4 py-2 text-sm font-medium text-white hover:bg-gray-800"
                  >
                    Запросить условия
                  </button>
                }
              />
            </article>
          ))}
        </div>
      </section>

      <section className="bg-gray-900 py-16 text-center text-white">
        <div className="mx-auto max-w-2xl px-6">
          <h2 className="text-2xl font-semibold">Думаете о своей нише?</h2>
          <p className="mt-2 text-sm text-gray-300">
            Расскажите о ней — за 30 минут поймём, подходит ли движок, и
            вернёмся со сметой и сроками.
          </p>
          <div className="mt-6 flex justify-center">
            <EarlyAccessDialog
              trigger={
                <button
                  type="button"
                  className="rounded-md bg-white px-5 py-3 text-sm font-medium text-gray-900 hover:bg-gray-100"
                >
                  Написать команде
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
