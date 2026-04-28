"use client";

import Link from "next/link";
import { useState } from "react";
import { ArrowRight, Shield } from "lucide-react";

import { NICHE_PACKS } from "@/lib/pricing";

export function NichePacks() {
  const [active, setActive] = useState(NICHE_PACKS[0]?.id ?? "");
  const current = NICHE_PACKS.find((n) => n.id === active) ?? NICHE_PACKS[0];

  return (
    <div className="grid grid-cols-1 gap-6 lg:grid-cols-[1fr_2fr]">
      <ul className="space-y-2" role="tablist" aria-label="Ниши">
        {NICHE_PACKS.map((p) => (
          <li key={p.id}>
            <button
              type="button"
              role="tab"
              aria-selected={active === p.id}
              onClick={() => setActive(p.id)}
              className={`flex w-full items-center justify-between rounded-lg border px-4 py-3 text-left text-sm transition ${
                active === p.id
                  ? "border-gray-900 bg-gray-900 text-white shadow-sm"
                  : "border-gray-200 bg-white text-gray-800 hover:border-gray-300"
              }`}
            >
              <span className="flex items-center gap-2">
                <span className="text-base" aria-hidden>
                  {p.emoji}
                </span>
                {p.name}
              </span>
              {p.compliance && (
                <Shield
                  className={`h-3.5 w-3.5 ${
                    active === p.id ? "text-amber-300" : "text-amber-500"
                  }`}
                  aria-label="Compliance"
                />
              )}
            </button>
          </li>
        ))}
      </ul>

      <div
        role="tabpanel"
        className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm"
      >
        <div className="flex items-baseline justify-between gap-3">
          <h3 className="text-lg font-semibold text-gray-900">
            {current.emoji} {current.name}
          </h3>
          {current.compliance && (
            <span className="inline-flex items-center gap-1 rounded-full bg-amber-50 px-2.5 py-0.5 text-xs font-medium text-amber-800">
              <Shield className="h-3 w-3" />
              нужна Compliance Pack
            </span>
          )}
        </div>

        <p className="mt-2 text-sm text-gray-600">
          Подходит для:
        </p>
        <div className="mt-2 flex flex-wrap gap-1.5">
          {current.professions.map((prof) => (
            <span
              key={prof}
              className="rounded-full border border-gray-200 bg-gray-50 px-2.5 py-1 text-xs text-gray-700"
            >
              {prof}
            </span>
          ))}
        </div>

        <dl className="mt-5 space-y-3 text-sm">
          <div>
            <dt className="font-medium text-gray-700">Голос по умолчанию</dt>
            <dd className="mt-1 text-gray-700">{current.exampleVoice}</dd>
          </div>
          <div>
            <dt className="font-medium text-gray-700">Пример марафона</dt>
            <dd className="mt-1 text-gray-700">«{current.exampleMarathon}»</dd>
          </div>
          <div>
            <dt className="font-medium text-gray-700">
              AI не пишет про это
            </dt>
            <dd className="mt-1 text-gray-700">{current.forbidden}</dd>
          </div>
        </dl>

        <p className="mt-6 rounded-md border border-dashed border-gray-300 bg-gray-50 px-4 py-3 text-xs text-gray-600">
          Niche Pack подключается к любому тарифу: <strong>+990 ₽/мес</strong>{" "}
          или <strong>4 990 ₽</strong> единоразово.
          {current.compliance && (
            <>
              {" "}
              Для регулируемых ниш дополнительно нужен{" "}
              <strong>Compliance Pack</strong> (+5 000 ₽/мес).
            </>
          )}
        </p>

        <Link
          href={`/n/${current.slug}`}
          className="mt-4 inline-flex items-center gap-1.5 text-sm font-medium text-primary hover:underline"
        >
          Подробнее о решении для «{current.name}»
          <ArrowRight className="h-3.5 w-3.5" aria-hidden />
        </Link>
      </div>
    </div>
  );
}
