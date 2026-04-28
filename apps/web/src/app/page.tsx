import Link from "next/link";

import { Addons } from "@/components/landing/Addons";
import { EarlyAccessDialog } from "@/components/landing/EarlyAccessDialog";
import { FAQ } from "@/components/landing/FAQ";
import { ModulesByTier } from "@/components/landing/ModulesByTier";
import { NichePacks } from "@/components/landing/NichePacks";
import { Roadmap } from "@/components/landing/Roadmap";
import { Scenarios } from "@/components/landing/Scenarios";
import { SiteFooter } from "@/components/landing/SiteFooter";
import { Testimonials } from "@/components/landing/Testimonials";
import { Tiers } from "@/components/landing/Tiers";

export default function LandingPage() {
  return (
    <main className="min-h-screen bg-gray-50 text-gray-900">
      <header className="sticky top-0 z-30 border-b border-gray-200 bg-white/90 backdrop-blur">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
          <span className="text-lg font-semibold">FishFlow</span>
          <nav className="hidden gap-6 text-sm text-gray-600 sm:flex">
            <a href="#niches" className="hover:text-gray-900">
              Ниши
            </a>
            <a href="#tiers" className="hover:text-gray-900">
              Тарифы
            </a>
            <a href="#modules" className="hover:text-gray-900">
              Модули
            </a>
            <a href="#scenarios" className="hover:text-gray-900">
              Сценарии
            </a>
            <a href="#faq" className="hover:text-gray-900">
              FAQ
            </a>
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

      <section className="mx-auto max-w-3xl px-6 pb-20 pt-16 text-center">
        <span className="inline-flex items-center gap-2 rounded-full border border-gray-200 bg-white px-3 py-1 text-xs font-medium text-gray-700 shadow-sm">
          <span className="h-1.5 w-1.5 rounded-full bg-emerald-500" />
          AI-ассистент для 65+ экспертных профессий
        </span>
        <h1 className="mt-4 text-4xl font-bold tracking-tight sm:text-5xl">
          Ваша экспертиза. Наш ассистент.
          <span className="block text-primary">Клиенты — каждый день.</span>
        </h1>
        <p className="mx-auto mt-4 max-w-2xl text-lg text-gray-600">
          FishFlow приводит заявки из ВКонтакте и Telegram, пишет посты в
          вашем голосе, ведёт марафоны и подсказывает, что делать сегодня
          для роста выручки.
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
            href="#niches"
            className="inline-flex items-center justify-center rounded-md border border-gray-300 bg-white px-5 py-3 text-sm font-medium text-gray-700 hover:bg-gray-100"
          >
            Найти свою нишу
          </Link>
        </div>

        <p className="mt-6 text-xs text-gray-500">
          14 дней бесплатно. Без карты. Можно отменить в один клик.
        </p>
      </section>

      <section
        id="niches"
        className="mx-auto max-w-6xl scroll-mt-24 px-6 pb-20"
      >
        <header className="mb-8 text-center">
          <h2 className="text-2xl font-semibold">
            Найдите себя — и увидите готовый набор
          </h2>
          <p className="mx-auto mt-2 max-w-2xl text-sm text-gray-600">
            Семь нишевых пресетов покрывают 65+ профессий: словарь, голос,
            шаблоны постов и марафонов, дисклеймеры. Подключаются к любому
            тарифу.
          </p>
        </header>
        <NichePacks />
        <p className="mt-6 text-center text-sm text-gray-600">
          Не нашли свою? Пишите —{" "}
          <a
            href="mailto:hello@fishflow.ru"
            className="text-primary hover:underline"
          >
            hello@fishflow.ru
          </a>{" "}
          — соберём пресет за 5 рабочих дней.
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
        <p className="mt-6 text-center text-xs text-gray-500">
          Годовая подписка — скидка 20%. Бесплатные первые 14 дней. Первые
          30 дней разница при апгрейде — за наш счёт.
        </p>
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

      <section className="mx-auto max-w-6xl scroll-mt-24 px-6 pb-20">
        <header className="mb-8 text-center">
          <h2 className="text-2xl font-semibold">Опции и расширения</h2>
          <p className="mt-2 text-sm text-gray-600">
            Подключаются к любому тарифу — добивают именно то, что нужно
            вашей нише.
          </p>
        </header>
        <Addons />
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

      <section className="mx-auto max-w-6xl scroll-mt-24 px-6 pb-20">
        <header className="mb-8 text-center">
          <h2 className="text-2xl font-semibold">Что говорят пилотные пользователи</h2>
          <p className="mt-2 text-sm text-gray-600">
            Первые отзывы из закрытой беты.
          </p>
        </header>
        <Testimonials />
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

      <section id="faq" className="mx-auto max-w-3xl scroll-mt-24 px-6 pb-20">
        <header className="mb-8 text-center">
          <h2 className="text-2xl font-semibold">Частые вопросы</h2>
        </header>
        <FAQ />
      </section>

      <section className="bg-gray-900 py-16 text-center text-white">
        <div className="mx-auto max-w-2xl px-6">
          <h2 className="text-2xl font-semibold">Готовы попробовать?</h2>
          <p className="mt-2 text-sm text-gray-300">
            Места в пилоте ограничены. Оставьте заявку — ответим в течение
            суток.
          </p>
          <div className="mt-6 flex justify-center gap-3">
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
            <Link
              href="/studio"
              className="rounded-md border border-white/30 px-5 py-3 text-sm font-medium text-white hover:bg-white/10"
            >
              Я хочу запустить свою нишу
            </Link>
          </div>
        </div>
      </section>

      <SiteFooter />
    </main>
  );
}
