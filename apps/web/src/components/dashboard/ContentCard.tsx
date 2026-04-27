"use client";

export function ContentCard() {
  return (
    <section className="rounded-lg border bg-white p-6 shadow-sm">
      <h2 className="text-base font-semibold text-gray-900">Контент</h2>
      <p className="mt-1 text-sm text-gray-500">
        Краткий обзор последних постов и календаря публикаций.
      </p>
      <div className="mt-4 text-sm text-gray-400">нет данных</div>
    </section>
  );
}
