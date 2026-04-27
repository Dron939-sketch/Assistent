"use client";

export function ActiveMarathonCard() {
  return (
    <section className="rounded-lg border bg-white p-6 shadow-sm">
      <h2 className="text-base font-semibold text-gray-900">Марафон</h2>
      <p className="mt-1 text-sm text-gray-500">
        Активный марафон и его прогресс.
      </p>
      <div className="mt-4 text-sm text-gray-400">марафон не запущен</div>
    </section>
  );
}
