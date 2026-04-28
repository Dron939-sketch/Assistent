"use client";

import * as Accordion from "@radix-ui/react-accordion";
import { ChevronDown } from "lucide-react";

interface FeatureItem {
  id: string;
  title: string;
  short: string;
  details: string[];
}

const FEATURES: FeatureItem[] = [
  {
    id: "audit",
    title: "Аудит ВКонтакте",
    short:
      "Балл доверия страницы и список того, что починить в первую очередь.",
    details: [
      "AI разбирает страницу по 10 категориям: обложка, аватар, закреп, описание, контент, вовлечение, комментарии, разнообразие, регулярность, сигналы доверия.",
      "Каждая категория получает балл от 0 до max, общий итог 0–100.",
      "Возвращаем приоритезированный план: топ-3 quick wins на 5 минут и долгосрочные правки.",
    ],
  },
  {
    id: "content",
    title: "Контент-генератор",
    short:
      "Посты, кейсы, ответы на возражения и сценарии — в стиле автора.",
    details: [
      "Генерация постов 500–1500 знаков с заголовком, хэштегами и вопросом-вовлекателем.",
      "Кейсы по структуре «проблема → попытки → решение → результат» с блоком «было/стало».",
      "Ответы на сообщения подписчиков: учитывает возражения «дорого», «подумаю» и не ставит диагнозов.",
    ],
  },
  {
    id: "funnel",
    title: "Авто-воронка",
    short:
      "Триггеры в комментариях/личке, сбор лидов, эскалация эксперту.",
    details: [
      "Триггеры по ключевым словам и интентам в комментариях ВК и личных сообщениях.",
      "AI-ответ в стиле автора, сбор контакта в карточку лида.",
      "Лента лидов со статусами new → consulted → client, метрики конверсии.",
    ],
  },
  {
    id: "marathons",
    title: "Марафоны под ключ",
    short:
      "Структура, задания, проверка домашек, мотивашки, отчёт по результатам.",
    details: [
      "Генерация программы 3–30 дней с заданиями, чек-листами и бонусами.",
      "Авто-проверка домашек: формальная сверка с критериями, эскалация на ручную проверку.",
      "Отчёт после марафона: вовлечённость, конверсия в платный продукт, NPS.",
    ],
  },
  {
    id: "brand",
    title: "Бренд-помощник",
    short:
      "Позиционирование, история, аудит доверия, поиск зоны уникальности.",
    details: [
      "Генерация УТП и elevator pitch на основе данных о вашем опыте и аудитории.",
      "Личная история по структуре «было → перелом → понял → помогаю» — длинная, короткая, видео-сценарий.",
      "Анализ зоны уникальности относительно конкурентов и рекомендации фокуса.",
    ],
  },
  {
    id: "analytics",
    title: "Аналитика и точки роста",
    short:
      "Один дашборд: лиды, ROI и подсказка дня, что сделать сегодня.",
    details: [
      "Метрики за 30 дней: подписчики, охват, ER, лиды, клиенты, выручка.",
      "Точка роста дня: одно конкретное действие на 15 минут с прогнозом эффекта.",
      "ROI по типам контента: какой формат приносит больше всего платящих.",
    ],
  },
];

export function FeaturesAccordion() {
  return (
    <Accordion.Root
      type="single"
      collapsible
      className="grid grid-cols-1 gap-4 lg:grid-cols-2"
    >
      {FEATURES.map((f) => (
        <Accordion.Item
          key={f.id}
          value={f.id}
          className="rounded-lg border border-gray-200 bg-white shadow-sm"
        >
          <Accordion.Header>
            <Accordion.Trigger className="group flex w-full items-start justify-between gap-4 p-6 text-left">
              <div>
                <h3 className="text-base font-semibold text-gray-900">
                  {f.title}
                </h3>
                <p className="mt-2 text-sm text-gray-600">{f.short}</p>
              </div>
              <ChevronDown
                className="h-5 w-5 shrink-0 text-gray-400 transition-transform duration-200 group-data-[state=open]:rotate-180"
                aria-hidden
              />
            </Accordion.Trigger>
          </Accordion.Header>
          <Accordion.Content className="overflow-hidden text-sm text-gray-700 data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:fade-out data-[state=open]:fade-in">
            <ul className="space-y-2 px-6 pb-6">
              {f.details.map((d) => (
                <li key={d} className="flex gap-2">
                  <span className="mt-1 h-1.5 w-1.5 shrink-0 rounded-full bg-primary" />
                  <span>{d}</span>
                </li>
              ))}
            </ul>
          </Accordion.Content>
        </Accordion.Item>
      ))}
    </Accordion.Root>
  );
}
