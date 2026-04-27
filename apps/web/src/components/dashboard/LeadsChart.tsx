"use client";

export function LeadsChart() {
  return (
    <section className="rounded-lg border bg-white p-6 shadow-sm">
      <h2 className="text-base font-semibold text-gray-900">Лиды</h2>
      <p className="mt-1 text-sm text-gray-500">
        Здесь будет график динамики лидов. Подключение к API произойдёт после
        реализации фронтенда.
      </p>
      <div className="mt-4 flex h-40 items-center justify-center rounded bg-gray-50 text-sm text-gray-400">
        нет данных
      </div>
    </section>
  );
}
