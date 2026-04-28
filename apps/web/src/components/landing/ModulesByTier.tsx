"use client";

import * as Tabs from "@radix-ui/react-tabs";
import * as Accordion from "@radix-ui/react-accordion";
import { ChevronDown } from "lucide-react";

type TierKey = "start" | "pro" | "expert";

type Module = { id: string; title: string; body: string };

const MODULES: Record<TierKey, Module[]> = {
  start: [
    {
      id: "start.1",
      title: "Автоворонка в Direct",
      body:
        "Бот отвечает на «дорого», «подумаю», собирает контакты, записывает на консультацию.",
    },
    {
      id: "start.2",
      title: "Автоответы на возражения",
      body:
        "50+ шаблонов под нишу, обучаются под стиль эксперта по уже опубликованным постам.",
    },
    {
      id: "start.3",
      title: "Генератор крючка",
      body:
        "По нише и боли клиента — 5 вариантов оффера для шапки профиля и stories.",
    },
    {
      id: "start.4",
      title: "Сбор заявок",
      body:
        "Авто-сохранение в CRM, Google Sheets или Telegram — выберите свой канал.",
    },
    {
      id: "start.5",
      title: "Уведомления о новых заявках",
      body: "Мгновенно в Telegram эксперта с краткой карточкой лида.",
    },
  ],
  pro: [
    {
      id: "pro.1",
      title: "Аудит страницы ВКонтакте",
      body: "Подробный отчёт из 20+ чек-пунктов: визуал, контент, доверие, активность.",
    },
    {
      id: "pro.2",
      title: "Контент-план на 2–4 недели",
      body: "Темы, форматы, даты — с учётом ниши и сезонности.",
    },
    {
      id: "pro.3",
      title: "Генератор постов по голосу",
      body: "Наговорили 2 минуты — получили 5 постов и 3 карусели в своём стиле.",
    },
    {
      id: "pro.4",
      title: "Автоматический постинг",
      body: "Интеграция с VK: публикация по расписанию из календаря.",
    },
    {
      id: "pro.5",
      title: "Генератор кейса (базовый)",
      body: "По шаблону «фото + текст + результат» с блоком «было/стало».",
    },
    {
      id: "pro.6",
      title: "Анализ комментариев",
      body: "Кластеризует топ-3 вопроса и возражения, предлагает темы для постов.",
    },
    {
      id: "pro.7",
      title: "Точка приложения усилий",
      body: "Одно действие сегодня с максимальным ROI и прогнозом эффекта.",
    },
  ],
  expert: [
    {
      id: "expert.1",
      title: "Конструктор марафонов под ключ",
      body: "5–10 дней: структура, контент, бот-ведущий, продажа в конце.",
    },
    {
      id: "expert.2",
      title: "Автопроверка домашек",
      body: "Участники присылают задания — ИИ проверяет по критериям, эскалирует спорные.",
    },
    {
      id: "expert.3",
      title: "Генератор личной истории",
      body: "Из 15-минутного интервью — текст «Почему вам можно верить» и видео-сценарий.",
    },
    {
      id: "expert.4",
      title: "Анализ уникальности",
      body: "Сравнение с 5 конкурентами и зона дифференциации.",
    },
    {
      id: "expert.5",
      title: "Аудит доверия",
      body: "Оценка страницы по 30 параметрам и приоритезированный план изменений.",
    },
    {
      id: "expert.6",
      title: "Конструктор лендинга",
      body: "AI-тексты под любую услугу: hero, проблема, решение, кейсы, тариф, CTA.",
    },
    {
      id: "expert.7",
      title: "Анализ лучших практик ниши",
      body: "Ежемесячный отчёт: что делают топ-3 эксперта в нише.",
    },
    {
      id: "expert.8",
      title: "Прогноз дохода + калькулятор ROI",
      body: "«Если сделаете X → получите Y заявок через Z дней».",
    },
  ],
};

const TAB_LABELS: { value: TierKey; label: string }[] = [
  { value: "start", label: "🟢 Start" },
  { value: "pro", label: "🔵 Pro" },
  { value: "expert", label: "🟠 Expert" },
];

export function ModulesByTier() {
  return (
    <Tabs.Root defaultValue="start" className="w-full">
      <Tabs.List
        aria-label="Уровни"
        className="mx-auto mb-6 flex w-fit gap-1 rounded-md border border-gray-200 bg-white p-1 shadow-sm"
      >
        {TAB_LABELS.map((t) => (
          <Tabs.Trigger
            key={t.value}
            value={t.value}
            className="rounded px-4 py-2 text-sm font-medium text-gray-600 data-[state=active]:bg-gray-900 data-[state=active]:text-white"
          >
            {t.label}
          </Tabs.Trigger>
        ))}
      </Tabs.List>

      {TAB_LABELS.map((t) => (
        <Tabs.Content key={t.value} value={t.value}>
          <Accordion.Root
            type="single"
            collapsible
            className="grid grid-cols-1 gap-3 lg:grid-cols-2"
          >
            {MODULES[t.value].map((m) => (
              <Accordion.Item
                key={m.id}
                value={m.id}
                className="rounded-lg border border-gray-200 bg-white shadow-sm"
              >
                <Accordion.Header>
                  <Accordion.Trigger className="group flex w-full items-center justify-between gap-4 p-5 text-left">
                    <span className="text-sm font-semibold text-gray-900">
                      {m.title}
                    </span>
                    <ChevronDown
                      className="h-4 w-4 shrink-0 text-gray-400 transition-transform duration-200 group-data-[state=open]:rotate-180"
                      aria-hidden
                    />
                  </Accordion.Trigger>
                </Accordion.Header>
                <Accordion.Content className="overflow-hidden text-sm text-gray-700 data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:fade-out data-[state=open]:fade-in">
                  <p className="px-5 pb-5">{m.body}</p>
                </Accordion.Content>
              </Accordion.Item>
            ))}
          </Accordion.Root>
        </Tabs.Content>
      ))}
    </Tabs.Root>
  );
}
