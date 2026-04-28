import Link from "next/link";

import { EarlyAccessDialog } from "@/components/landing/EarlyAccessDialog";
import { FeaturesAccordion } from "@/components/landing/FeaturesAccordion";

export default function LandingPage() {
  return (
    <main className="min-h-screen bg-gray-50 text-gray-900">
      <header className="mx-auto flex max-w-5xl items-center justify-between px-6 py-6">
        <span className="text-lg font-semibold">FishFlow</span>
        <span className="text-xs uppercase tracking-wider text-gray-500">
          закрытое бета-тестирование
        </span>
      </header>

      <section className="mx-auto max-w-3xl px-6 pb-16 pt-12 text-center">
        <h1 className="text-4xl font-bold tracking-tight sm:text-5xl">
          AI-ассистент для эксперта
        </h1>
        <p className="mt-4 text-lg text-gray-600">
          Приводим клиентов из ВКонтакте, помогаем с контентом, ведём марафоны
          и подсказываем точки роста — в одном кабинете.
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
            href="#features"
            className="inline-flex items-center justify-center rounded-md border border-gray-300 bg-white px-5 py-3 text-sm font-medium text-gray-700 hover:bg-gray-100"
          >
            Что умеет
          </Link>
        </div>

        <p className="mt-6 text-xs text-gray-500">
          Регистрация и вход для пилотных пользователей пока выключены — мы
          подключаем доступ вручную.
        </p>
      </section>

      <section id="features" className="mx-auto max-w-5xl px-6 pb-20">
        <h2 className="mb-8 text-center text-2xl font-semibold">
          Что внутри
        </h2>
        <FeaturesAccordion />
      </section>

      <footer className="border-t border-gray-200 bg-white">
        <div className="mx-auto flex max-w-5xl flex-col items-center gap-2 px-6 py-8 text-xs text-gray-500 sm:flex-row sm:justify-between">
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
