import Link from "next/link";

const FEATURES = [
  {
    title: "Аудит ВКонтакте",
    body:
      "AI разбирает страницу эксперта по 10 категориям, считает балл доверия и даёт конкретные шаги, что починить в первую очередь.",
  },
  {
    title: "Контент-генератор",
    body:
      "Посты, кейсы, ответы на возражения и сценарии для Reels — в стиле автора, с учётом ниши и аудитории.",
  },
  {
    title: "Авто-воронка",
    body:
      "Триггеры по ключевым словам в комментариях и личке: ИИ-ответ, сбор лидов, эскалация эксперту, аналитика конверсий.",
  },
  {
    title: "Марафоны под ключ",
    body:
      "Структура, ежедневные задания, проверка домашек, мотивационные сообщения и отчёт по результатам участников.",
  },
  {
    title: "Бренд-помощник",
    body:
      "Позиционирование, личная история, аудит доверия, поиск зоны уникальности и копирайт лендинга.",
  },
  {
    title: "Аналитика и точки роста",
    body:
      "Один дашборд с лидами, ROI и подсказками, какое одно действие сегодня даст максимум результата.",
  },
];

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
          <a
            href="https://t.me/fishflow_bot"
            target="_blank"
            rel="noreferrer"
            className="inline-flex items-center justify-center rounded-md bg-primary px-5 py-3 text-sm font-medium text-white hover:bg-primary/90"
          >
            Получить ранний доступ
          </a>
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
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {FEATURES.map((f) => (
            <div
              key={f.title}
              className="rounded-lg border border-gray-200 bg-white p-6 shadow-sm"
            >
              <h3 className="text-base font-semibold">{f.title}</h3>
              <p className="mt-2 text-sm text-gray-600">{f.body}</p>
            </div>
          ))}
        </div>
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
