import { Check } from "lucide-react";

import { TIERS } from "@/lib/pricing";

const formatPrice = (rub: number) =>
  `${rub.toLocaleString("ru-RU")} ₽/мес`;

export function Tiers() {
  return (
    <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
      {TIERS.map((t) => (
        <article
          key={t.id}
          className={`flex flex-col rounded-xl border p-6 shadow-sm ${t.accent}`}
        >
          <div className="mb-4 flex items-center justify-between">
            <h3 className="text-lg font-semibold text-gray-900">{t.name}</h3>
            <span className="rounded-full bg-white px-2.5 py-0.5 text-xs font-medium uppercase tracking-wide text-gray-700">
              {t.tagline}
            </span>
          </div>
          <p className="text-2xl font-bold text-gray-900">
            {formatPrice(t.price)}
          </p>
          <p className="mt-2 text-sm italic text-gray-700">{t.promise}</p>

          <dl className="mt-4 space-y-1 text-sm text-gray-700">
            <div>
              <dt className="inline font-medium">Для кого: </dt>
              <dd className="inline">{t.audience}</dd>
            </div>
            <div>
              <dt className="inline font-medium">Заменяет: </dt>
              <dd className="inline">{t.replaces}</dd>
            </div>
          </dl>

          <ul className="mt-5 flex-1 space-y-2 text-sm text-gray-800">
            {t.highlights.map((h) => (
              <li key={h} className="flex items-start gap-2">
                <Check className="mt-0.5 h-4 w-4 shrink-0 text-emerald-600" />
                <span>{h}</span>
              </li>
            ))}
          </ul>
        </article>
      ))}
    </div>
  );
}
