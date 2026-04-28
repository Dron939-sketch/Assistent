"use client";

import { Check } from "lucide-react";

type Tier = {
  id: "start" | "pro" | "expert";
  name: string;
  price: string;
  tagline: string;
  promise: string;
  audience: string;
  replaces: string;
  accent: string;
  highlights: string[];
};

const TIERS: Tier[] = [
  {
    id: "start",
    name: "FishFlow Start",
    price: "1 490 ₽/мес",
    tagline: "Бот в директ",
    promise: "«Начните получать заявки уже сегодня»",
    audience: "Новичок, нет контента, нет времени",
    replaces: "Администратора чатов",
    accent: "border-emerald-200 bg-emerald-50",
    highlights: [
      "Автоворонка в Direct и сообщения",
      "Шаблоны ответов на возражения",
      "Сбор заявок в CRM / Google Sheets / Telegram",
      "Уведомления о новых лидах в Telegram",
      "Генератор крючка-оффера",
    ],
  },
  {
    id: "pro",
    name: "FishFlow Pro",
    price: "3 490 ₽/мес",
    tagline: "Автопилот маркетинга",
    promise: "«Ваша страница работает на вас 24/7»",
    audience: "Есть база, но нет системы",
    replaces: "SMM-менеджера + копирайтера",
    accent: "border-sky-200 bg-sky-50",
    highlights: [
      "Всё из Start",
      "Аудит страницы ВКонтакте: 20+ чек-пунктов",
      "Контент-план на 2–4 недели",
      "Голосовая → 5 постов и 3 карусели",
      "Автопостинг по расписанию",
      "Точка приложения усилий: одно действие с максимальным ROI",
    ],
  },
  {
    id: "expert",
    name: "FishFlow Expert",
    price: "7 990 ₽/мес",
    tagline: "Цифровой COO",
    promise: "«Вы — бренд. Масштабируйтесь без команды»",
    audience: "Уже продаёт, хочет расти",
    replaces: "Команду из 3–5 человек",
    accent: "border-amber-200 bg-amber-50",
    highlights: [
      "Всё из Pro",
      "Конструктор марафонов под ключ",
      "Автопроверка домашних заданий",
      "Генератор личной истории",
      "Анализ уникальности vs конкуренты",
      "Аудит доверия по 30 параметрам",
      "Конструктор лендинга",
      "Прогноз дохода + калькулятор ROI",
    ],
  },
];

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
          <p className="text-2xl font-bold text-gray-900">{t.price}</p>
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
