import Link from "next/link";

import { EarlyAccessDialog } from "@/components/landing/EarlyAccessDialog";
import { ModulesByTier } from "@/components/landing/ModulesByTier";
import { Roadmap } from "@/components/landing/Roadmap";
import { Scenarios } from "@/components/landing/Scenarios";
import { Tiers } from "@/components/landing/Tiers";

export default function LandingPage() {
  return (
    <main className="min-h-screen bg-gray-50 text-gray-900">
      <header className="sticky top-0 z-30 border-b border-gray-200 bg-white/90 backdrop-blur">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
          <span className="text-lg font-semibold">FishFlow</span>
          <nav className="hidden gap-6 text-sm text-gray-600 sm:flex">
            <a href="#tiers" className="hover:text-gray-900">
              Тарифы
            </a>
            <a href="#modules" className="hover:text-gray-900">
              Модули
            </a>
            <a href="#scenarios" className="hover:text-gray-900">
              Сценарии
            </a>
            <a href="#roadmap" className="hover:text-gray-900">
              План
            </a>
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

      <section className="mx-auto max-w-3xl px-6 pb-20 pt-16 text-center">
        <span className="text-xs font-semibold uppercase tracking-wider text-gray-500">
          закрытое бета-тестирование
        </span>
        <h1 className="mt-3 text-4xl font-bold tracking-tight sm:text-5xl">
          AI-ассистент эксперта
        </h1>
        <p className="mx-auto mt-4 max-w-xl text-lg text-gray-600">
          Уровень 1 — бот приводит заявки. Уровень 2 — бот плюс контент и
          аналитика. Уровень 3 — полная система: клиенты, бренд, марафоны,
          масштабирование.
        </p>
        <p className="mt-4 text-base text-gray-700">
          Вы просто помогаете людям. Остальное делает AI.
        </p>

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
            href="#tiers"
            className="inline-flex items-center justify-center rounded-md border border-gray-300 bg-white px-5 py-3 text-sm font-medium text-gray-700 hover:bg-gray-100"
          >
            Посмотреть тарифы
          </Link>
        </div>

        <p className="mt-6 text-xs text-gray-500">
          Регистрация и вход для пилотных пользователей пока выключены — мы
          подключаем доступ вручную.
        </p>
      </section>

      <section id="tiers" className="mx-auto max-w-6xl scroll-mt-24 px-6 pb-20">
        <header className="mb-8 text-center">
          <h2 className="text-2xl font-semibold">
            Три уровня — три продукта в одном
          </h2>
          <p className="mt-2 text-sm text-gray-600">
            Платите только за то, чем пользуетесь сегодня. Апгрейд прозрачный
            и обратимый.
          </p>
        </header>
        <Tiers />
      </section>

      <section
        id="modules"
        className="mx-auto max-w-6xl scroll-mt-24 px-6 pb-20"
      >
        <header className="mb-8 text-center">
          <h2 className="text-2xl font-semibold">Модули по уровням</h2>
          <p className="mt-2 text-sm text-gray-600">
            Выберите уровень — увидите состав. Каждый блок раскрывается на
            подробности.
          </p>
        </header>
        <ModulesByTier />
      </section>

      <section className="mx-auto max-w-3xl scroll-mt-24 px-6 pb-20">
        <header className="mb-6 text-center">
          <h2 className="text-2xl font-semibold">Прозрачный апгрейд</h2>
          <p className="mt-2 text-sm text-gray-600">
            Каждый недоступный модуль внутри кабинета сам объясняет, на каком
            тарифе он откроется. Никаких сюрпризов.
          </p>
        </header>
        <pre className="overflow-x-auto rounded-lg border border-gray-200 bg-white p-5 text-xs leading-relaxed text-gray-700 shadow-sm">{`Ваш тариф: FishFlow Start

🟢 Start    🔵 Pro    🟠 Expert
████████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░

Доступно:
✅ Автоворонка в Direct
✅ Автоответы на возражения
✅ Сбор заявок

Недоступно (для перехода на Pro):
❌ Аудит страницы
❌ Генератор постов
❌ Автоматический постинг

[ Перейти на Pro ]  3490 ₽/мес вместо 1490 ₽/мес
(первые 30 дней — разница бесплатно)`}</pre>
      </section>

      <section
        id="scenarios"
        className="mx-auto max-w-6xl scroll-mt-24 px-6 pb-20"
      >
        <header className="mb-8 text-center">
          <h2 className="text-2xl font-semibold">Как это работает на людях</h2>
          <p className="mt-2 text-sm text-gray-600">
            Три истории Марии-нутрициолога — по одной на тариф.
          </p>
        </header>
        <Scenarios />
      </section>

      <section
        id="roadmap"
        className="mx-auto max-w-3xl scroll-mt-24 px-6 pb-20"
      >
        <header className="mb-8 text-center">
          <h2 className="text-2xl font-semibold">Дорожная карта</h2>
          <p className="mt-2 text-sm text-gray-600">
            Что мы строим и в каком порядке. Сегодня готов уровень Start.
          </p>
        </header>
        <Roadmap />
      </section>

      <section className="bg-gray-900 py-16 text-center text-white">
        <div className="mx-auto max-w-2xl px-6">
          <h2 className="text-2xl font-semibold">Готовы попробовать?</h2>
          <p className="mt-2 text-sm text-gray-300">
            Места в пилоте ограничены. Оставьте заявку — ответим в течение
            суток.
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

      <footer className="border-t border-gray-200 bg-white">
        <div className="mx-auto flex max-w-6xl flex-col items-center gap-2 px-6 py-8 text-xs text-gray-500 sm:flex-row sm:justify-between">
          <span>© FishFlow. Все права защищены.</span>
          <span>
            Связь:{" "}
            <a
              href="mailto:hello@fishflow.ru"
              className="text-primary hover:underline"
            >
              hello@fishflow.ru
            </a>
          </span>
        </div>
      </footer>
    </main>
  );
}
