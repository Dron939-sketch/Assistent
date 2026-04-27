"use client";

export function LeveragePointCard() {
  return (
    <section className="rounded-lg border bg-white p-6 shadow-sm">
      <h2 className="text-base font-semibold text-gray-900">Точка роста</h2>
      <p className="mt-1 text-sm text-gray-500">
        Рекомендация дня — самое полезное действие, которое стоит сделать
        сегодня.
      </p>
      <div className="mt-4 text-sm text-gray-400">нет рекомендаций</div>
    </section>
  );
}
