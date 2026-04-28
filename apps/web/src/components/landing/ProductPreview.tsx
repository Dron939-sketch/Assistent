"use client";

import * as Tabs from "@radix-ui/react-tabs";
import {
  ArrowUpRight,
  Calendar,
  CheckCircle2,
  Hash,
  Heart,
  MessageSquare,
  Sparkles,
  TrendingUp,
  Users,
} from "lucide-react";

const TABS = [
  { value: "dashboard", label: "Дашборд" },
  { value: "post", label: "Генератор поста" },
  { value: "lead", label: "Карточка лида" },
  { value: "leverage", label: "Точка дня" },
];

export function ProductPreview() {
  return (
    <Tabs.Root defaultValue="dashboard">
      <Tabs.List
        aria-label="Превью продукта"
        className="mx-auto mb-6 flex w-fit gap-1 rounded-md border border-gray-200 bg-white p-1 shadow-sm"
      >
        {TABS.map((t) => (
          <Tabs.Trigger
            key={t.value}
            value={t.value}
            className="rounded px-3 py-1.5 text-sm font-medium text-gray-600 data-[state=active]:bg-gray-900 data-[state=active]:text-white"
          >
            {t.label}
          </Tabs.Trigger>
        ))}
      </Tabs.List>

      <div className="rounded-2xl border border-gray-200 bg-gradient-to-br from-gray-50 to-gray-100 p-4 shadow-inner sm:p-8">
        <Tabs.Content value="dashboard">
          <DashboardMock />
        </Tabs.Content>
        <Tabs.Content value="post">
          <PostMock />
        </Tabs.Content>
        <Tabs.Content value="lead">
          <LeadMock />
        </Tabs.Content>
        <Tabs.Content value="leverage">
          <LeverageMock />
        </Tabs.Content>
      </div>
    </Tabs.Root>
  );
}

function MockChrome({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div className="overflow-hidden rounded-xl border border-gray-200 bg-white shadow-sm">
      <div className="flex items-center justify-between border-b border-gray-100 bg-gray-50 px-4 py-2 text-xs text-gray-500">
        <div className="flex items-center gap-1.5">
          <span className="h-2.5 w-2.5 rounded-full bg-rose-300" />
          <span className="h-2.5 w-2.5 rounded-full bg-amber-300" />
          <span className="h-2.5 w-2.5 rounded-full bg-emerald-300" />
          <span className="ml-3 font-medium text-gray-700">{title}</span>
        </div>
        <span className="hidden font-mono sm:inline">app.fishflow.ru</span>
      </div>
      <div className="p-5">{children}</div>
    </div>
  );
}

function DashboardMock() {
  const metrics = [
    {
      label: "Заявки",
      value: "47",
      delta: "+22%",
      Icon: Users,
      tone: "text-emerald-600",
    },
    {
      label: "Клиенты",
      value: "12",
      delta: "+8%",
      Icon: CheckCircle2,
      tone: "text-emerald-600",
    },
    {
      label: "Выручка",
      value: "184 200 ₽",
      delta: "+34%",
      Icon: TrendingUp,
      tone: "text-emerald-600",
    },
    {
      label: "Конверсия",
      value: "25,5%",
      delta: "−2%",
      Icon: Sparkles,
      tone: "text-rose-600",
    },
  ];

  return (
    <MockChrome title="Дашборд · последние 30 дней">
      <div className="grid grid-cols-2 gap-3 lg:grid-cols-4">
        {metrics.map((m) => (
          <div
            key={m.label}
            className="rounded-lg border border-gray-100 p-4"
          >
            <div className="flex items-center justify-between text-xs text-gray-500">
              <span>{m.label}</span>
              <m.Icon className="h-3.5 w-3.5" aria-hidden />
            </div>
            <div className="mt-2 text-xl font-semibold text-gray-900">
              {m.value}
            </div>
            <div className={`mt-1 text-xs font-medium ${m.tone}`}>{m.delta}</div>
          </div>
        ))}
      </div>

      <div className="mt-5 grid grid-cols-1 gap-3 lg:grid-cols-3">
        <div className="lg:col-span-2 rounded-lg border border-gray-100 p-4">
          <div className="mb-2 flex items-center justify-between text-xs">
            <span className="font-medium text-gray-700">Лиды по дням</span>
            <span className="text-gray-500">апр</span>
          </div>
          <svg viewBox="0 0 320 80" className="h-20 w-full">
            <defs>
              <linearGradient id="g1" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="#22c55e" stopOpacity="0.4" />
                <stop offset="100%" stopColor="#22c55e" stopOpacity="0" />
              </linearGradient>
            </defs>
            <path
              d="M0,55 L20,50 L40,52 L60,40 L80,46 L100,30 L120,38 L140,28 L160,33 L180,22 L200,30 L220,18 L240,24 L260,12 L280,18 L300,8 L320,14 L320,80 L0,80 Z"
              fill="url(#g1)"
            />
            <path
              d="M0,55 L20,50 L40,52 L60,40 L80,46 L100,30 L120,38 L140,28 L160,33 L180,22 L200,30 L220,18 L240,24 L260,12 L280,18 L300,8 L320,14"
              fill="none"
              stroke="#16a34a"
              strokeWidth="1.5"
              strokeLinejoin="round"
              strokeLinecap="round"
            />
          </svg>
        </div>
        <div className="rounded-lg border border-gray-100 p-4">
          <span className="text-xs font-medium text-gray-700">
            Источники лидов
          </span>
          <ul className="mt-3 space-y-2 text-xs text-gray-700">
            <li className="flex items-center justify-between">
              <span>ВКонтакте · комментарии</span>
              <span className="font-semibold">52%</span>
            </li>
            <li className="flex items-center justify-between">
              <span>Telegram · бот</span>
              <span className="font-semibold">31%</span>
            </li>
            <li className="flex items-center justify-between">
              <span>Прямые сообщения</span>
              <span className="font-semibold">17%</span>
            </li>
          </ul>
        </div>
      </div>
    </MockChrome>
  );
}

function PostMock() {
  return (
    <MockChrome title="Генератор поста">
      <div className="grid grid-cols-1 gap-4 lg:grid-cols-[2fr_3fr]">
        <div className="space-y-3 text-sm">
          <div>
            <span className="block text-xs font-medium text-gray-500">
              Тема
            </span>
            <div className="mt-1 rounded border border-gray-200 px-3 py-2 text-gray-800">
              Как отличить настоящий голод от стресса
            </div>
          </div>
          <div>
            <span className="block text-xs font-medium text-gray-500">
              Голос автора
            </span>
            <div className="mt-1 rounded border border-gray-200 px-3 py-2 text-gray-800">
              Заботливый, без жёсткой дисциплины, с юмором про сладости
            </div>
          </div>
          <div className="flex gap-2">
            <button className="rounded-md bg-gray-900 px-3 py-1.5 text-xs font-medium text-white">
              Сгенерировать
            </button>
            <button className="rounded-md border border-gray-200 px-3 py-1.5 text-xs text-gray-700">
              Перегенерировать
            </button>
          </div>
        </div>

        <div className="rounded-lg border border-gray-100 bg-white p-4 text-sm leading-relaxed text-gray-800">
          <h3 className="text-base font-semibold text-gray-900">
            Голод или стресс? Тест на 60 секунд
          </h3>
          <p className="mt-2">
            Если вы только что поужинали и через 30 минут идёте к холодильнику
            — это вряд ли голод. Тело ещё переваривает. Чаще всего туда тащит
            стресс, скука или усталость.
          </p>
          <p className="mt-2">
            Простой тест: налейте стакан воды и подождите 10 минут. Если
            «голод» исчез — это была не еда, а сигнал поддержки. Если остался
            — добавьте белок и клетчатку, не сладкое.
          </p>
          <div className="mt-3 flex flex-wrap gap-1.5">
            {[
              "#нутрициолог",
              "#питание",
              "#осознанность",
              "#стресс",
            ].map((h) => (
              <span
                key={h}
                className="inline-flex items-center gap-1 rounded-full bg-gray-100 px-2 py-0.5 text-xs text-gray-600"
              >
                <Hash className="h-3 w-3" />
                {h.slice(1)}
              </span>
            ))}
          </div>
          <div className="mt-4 flex items-center gap-4 border-t border-gray-100 pt-3 text-xs text-gray-500">
            <span className="flex items-center gap-1">
              <Heart className="h-3.5 w-3.5" /> 86
            </span>
            <span className="flex items-center gap-1">
              <MessageSquare className="h-3.5 w-3.5" /> 12
            </span>
            <span className="ml-auto inline-flex items-center gap-1 text-emerald-700">
              <Calendar className="h-3.5 w-3.5" /> Опубликуется 28 апреля, 09:00
            </span>
          </div>
        </div>
      </div>
    </MockChrome>
  );
}

function LeadMock() {
  const messages = [
    { side: "client", text: "Сколько стоит консультация?" },
    {
      side: "bot",
      text: "Первая встреча 30 минут — бесплатно. Полная консультация — от 4 000 ₽.",
    },
    { side: "client", text: "А если результата не будет?" },
    {
      side: "bot",
      text: "У меня в работе цель — изменения за 4 недели. Если шага нет, разбираем причины и план меняем без доплаты.",
    },
  ];

  return (
    <MockChrome title="Карточка лида">
      <div className="grid grid-cols-1 gap-4 lg:grid-cols-[1fr_1.4fr]">
        <div className="rounded-lg border border-gray-100 p-4 text-sm">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-full bg-gradient-to-br from-blue-400 to-blue-600 text-sm font-semibold text-white">
              ЕС
            </div>
            <div>
              <div className="font-semibold text-gray-900">Елена С.</div>
              <div className="text-xs text-gray-500">VK · 14 апреля</div>
            </div>
          </div>
          <dl className="mt-4 space-y-2 text-xs text-gray-700">
            <div className="flex justify-between">
              <dt>Источник</dt>
              <dd className="font-medium">Комментарий к посту</dd>
            </div>
            <div className="flex justify-between">
              <dt>Триггер</dt>
              <dd className="font-medium">«сколько стоит»</dd>
            </div>
            <div className="flex justify-between">
              <dt>Статус</dt>
              <dd>
                <span className="inline-flex items-center gap-1 rounded-full bg-amber-100 px-2 py-0.5 text-amber-800">
                  Прогрев
                </span>
              </dd>
            </div>
            <div className="flex justify-between">
              <dt>Тёплость</dt>
              <dd className="font-medium text-emerald-700">8 / 10</dd>
            </div>
          </dl>
          <div className="mt-4 flex gap-2">
            <button className="flex-1 rounded-md bg-gray-900 px-3 py-1.5 text-xs font-medium text-white">
              На консультацию
            </button>
            <button className="flex-1 rounded-md border border-gray-200 px-3 py-1.5 text-xs text-gray-700">
              Передать мне
            </button>
          </div>
        </div>

        <div className="flex flex-col rounded-lg border border-gray-100 p-4">
          <span className="text-xs font-medium text-gray-500">
            Переписка с ботом
          </span>
          <ul className="mt-3 flex flex-1 flex-col gap-2">
            {messages.map((m, i) => (
              <li
                key={i}
                className={`max-w-[85%] rounded-lg px-3 py-2 text-xs ${
                  m.side === "client"
                    ? "self-end bg-blue-50 text-gray-800"
                    : "self-start bg-gray-100 text-gray-800"
                }`}
              >
                {m.text}
              </li>
            ))}
          </ul>
          <p className="mt-3 text-[10px] uppercase tracking-wider text-gray-400">
            Ответ AI — не публикуется без вашего подтверждения
          </p>
        </div>
      </div>
    </MockChrome>
  );
}

function LeverageMock() {
  return (
    <MockChrome title="Точка приложения усилий · сегодня">
      <div className="rounded-lg border border-emerald-200 bg-emerald-50 p-5">
        <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-emerald-700">
          <Sparkles className="h-3.5 w-3.5" />
          Действие на 15 минут
        </div>
        <h3 className="mt-2 text-lg font-semibold text-gray-900">
          Закреплённый пост работает вхолостую
        </h3>
        <p className="mt-2 text-sm text-gray-700">
          В вашем закрепе сейчас приветствие без призыва к действию. Меняем
          на короткий оффер с записью на бесплатную консультацию.
        </p>

        <div className="mt-4 grid grid-cols-1 gap-3 sm:grid-cols-3">
          <div className="rounded border border-emerald-200 bg-white p-3 text-xs">
            <span className="block text-gray-500">Эффект</span>
            <span className="mt-1 block font-semibold text-emerald-700">
              +5–8 заявок / неделя
            </span>
          </div>
          <div className="rounded border border-emerald-200 bg-white p-3 text-xs">
            <span className="block text-gray-500">Усилие</span>
            <span className="mt-1 block font-semibold text-gray-900">
              15 минут
            </span>
          </div>
          <div className="rounded border border-emerald-200 bg-white p-3 text-xs">
            <span className="block text-gray-500">Уверенность</span>
            <span className="mt-1 block font-semibold text-gray-900">
              92%
            </span>
          </div>
        </div>

        <div className="mt-4 flex flex-wrap gap-2">
          <button className="inline-flex items-center gap-1.5 rounded-md bg-gray-900 px-3 py-1.5 text-xs font-medium text-white">
            Сделать сейчас
            <ArrowUpRight className="h-3 w-3" />
          </button>
          <button className="rounded-md border border-gray-200 bg-white px-3 py-1.5 text-xs text-gray-700">
            Отложить на завтра
          </button>
        </div>
      </div>
    </MockChrome>
  );
}
