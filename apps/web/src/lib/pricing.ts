/**
 * Single source of truth for product packaging shown on the landing.
 * Anything user-visible (tier prices, niche packs, studio plans, add-ons,
 * compliance pricing) lives here so we keep marketing copy and the eventual
 * billing layer consistent.
 */

export type Tier = "start" | "pro" | "expert";

export interface TierSpec {
  id: Tier;
  name: string;
  price: number; // RUB / month
  tagline: string;
  promise: string;
  audience: string;
  replaces: string;
  highlights: string[];
  accent: string;
}

export const TIERS: TierSpec[] = [
  {
    id: "start",
    name: "FishFlow Start",
    price: 1490,
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
    price: 3490,
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
    price: 7990,
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

export interface ModuleSpec {
  id: string;
  title: string;
  body: string;
}

export const MODULES_BY_TIER: Record<Tier, ModuleSpec[]> = {
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

export interface NichePackSpec {
  id: string;
  name: string;
  emoji: string;
  professions: string[];
  exampleMarathon: string;
  exampleVoice: string;
  forbidden: string;
  compliance?: "medical" | "legal" | "financial";
}

export const NICHE_PACKS: NichePackSpec[] = [
  {
    id: "health",
    name: "Здоровье и тело",
    emoji: "🥗",
    professions: [
      "Нутрициолог",
      "Диетолог",
      "Сомнолог",
      "Реабилитолог",
      "Остеопат",
      "Массажист",
      "Аюрведа-специалист",
    ],
    exampleMarathon: "5 дней без вздутия",
    exampleVoice: "Заботливый, без жёсткой дисциплины, с юмором про сладости",
    forbidden:
      "Медицинские диагнозы, лекарства, лечебные диеты без образования",
    compliance: "medical",
  },
  {
    id: "fitness",
    name: "Фитнес и движение",
    emoji: "💪",
    professions: [
      "Фитнес-тренер",
      "Инструктор йоги",
      "ЛФК-инструктор",
      "Pilates-инструктор",
    ],
    exampleMarathon: "Месяц к идеальной спине",
    exampleVoice: "Энергичный, мотивирующий, конкретные техники",
    forbidden: "Травмоопасные упражнения без предупреждения, диагнозы",
  },
  {
    id: "psychology",
    name: "Психика и отношения",
    emoji: "🧠",
    professions: [
      "Психолог",
      "Психотерапевт",
      "Коуч",
      "Семейный консультант",
      "Сексолог",
      "Карьерный консультант",
    ],
    exampleMarathon: "7 дней личных границ",
    exampleVoice: "Эмпатичный, поддерживающий, без оценок",
    forbidden:
      "Диагнозы, лекарства, экстренные состояния — направление на горячую линию",
    compliance: "medical",
  },
  {
    id: "mystics",
    name: "Эзотерика и духовное",
    emoji: "🔮",
    professions: [
      "Таролог",
      "Астролог",
      "Нумеролог",
      "Рунолог",
      "Хиромант",
      "Фэн-шуй консультант",
    ],
    exampleMarathon: "Карта дня: 14 дней самопознания",
    exampleVoice: "Тёплый, образный, без категоричных предсказаний",
    forbidden: "Конкретные даты событий, диагнозы, замена медицины",
  },
  {
    id: "education",
    name: "Образование",
    emoji: "📚",
    professions: [
      "Репетитор",
      "Преподаватель языков",
      "Автор онлайн-курса",
      "Ментор",
      "Профориентолог",
    ],
    exampleMarathon: "10 дней живого английского",
    exampleVoice: "Структурный, дружелюбный, поощряющий",
    forbidden: "Гарантии результата экзамена, чужие материалы без согласия",
  },
  {
    id: "business",
    name: "Бизнес и консалтинг",
    emoji: "💼",
    professions: [
      "Бизнес-коуч",
      "Маркетолог / SMM",
      "Финансовый советник",
      "Юрист",
      "Бухгалтер-консультант",
      "HR-консультант",
    ],
    exampleMarathon: "5 дней для запуска воронки",
    exampleVoice: "Деловой, конкретный, с цифрами и кейсами",
    forbidden:
      "Конкретные инвест-рекомендации, юр. ответы вне обозначенной квалификации",
    compliance: "legal",
  },
  {
    id: "lifestyle",
    name: "Творчество и хобби",
    emoji: "🎨",
    professions: ["Фотограф", "Дизайнер интерьеров", "Стилист", "Блогер"],
    exampleMarathon: "Неделя контента, который продаёт себя",
    exampleVoice: "Лёгкий, визуальный, вдохновляющий",
    forbidden: "Чужие работы без указания авторства",
  },
];

export interface AddonSpec {
  id: string;
  name: string;
  price: string;
  description: string;
}

export const ADDONS: AddonSpec[] = [
  {
    id: "niche_pack",
    name: "Niche Pack",
    price: "+990 ₽/мес или 4 990 ₽ единоразово",
    description:
      "Готовая настройка под нишу: словарь, шаблоны, голос, дисклеймеры. Подключается к любому тарифу.",
  },
  {
    id: "compliance",
    name: "Compliance Pack",
    price: "+5 000 ₽/мес",
    description:
      "Усиленные гард-рейлы для медицины, юриспруденции и финансов: human-in-the-loop, аудит-трейл, шаблоны дисклеймеров.",
  },
  {
    id: "voice_clone",
    name: "Voice cloning",
    price: "+990 ₽/мес",
    description:
      "Клонируем ваш голос для аудио-постов и подкастов из текстов.",
  },
  {
    id: "video_script",
    name: "Видео-сценарии",
    price: "+1 490 ₽/мес",
    description:
      "Сценарий + раскадровка для Reels, Shorts и YouTube. С хуком, развитием и CTA.",
  },
  {
    id: "extra_tokens",
    name: "Дополнительные AI-токены",
    price: "по факту, маржа 30%",
    description:
      "Если вы публикуете больше 100 постов в неделю — снимаем потолок.",
  },
];

export interface StudioPlan {
  id: string;
  name: string;
  price: string;
  details: string[];
}

export const STUDIO_PLANS: StudioPlan[] = [
  {
    id: "starter",
    name: "Studio Starter",
    price: "49 900 ₽/мес",
    details: [
      "1 ниша",
      "до 50 экспертов",
      "Поддомен и брендинг под вас",
      "Базовый отчёт раз в месяц",
    ],
  },
  {
    id: "growth",
    name: "Studio Growth",
    price: "99 900 ₽/мес",
    details: [
      "До 3 ниш",
      "До 250 экспертов",
      "Кастомный домен",
      "Приоритетная поддержка",
    ],
  },
  {
    id: "enterprise",
    name: "Studio Enterprise",
    price: "от 199 900 ₽ + revenue share 20%",
    details: [
      "Свой регион / страна",
      "Кастомные модули и интеграции",
      "SLA, отдельный success-менеджер",
    ],
  },
];

export const STUDIO_SETUP_FEE = 99000;
