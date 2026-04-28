type Scenario = {
  tier: string;
  title: string;
  steps: string[];
  outcome: string;
};

const SCENARIOS: Scenario[] = [
  {
    tier: "🟢 Start",
    title: "Мария, нутрициолог, нет времени на ответы",
    steps: [
      "Регистрируется, выбирает Start",
      "Настраивает автоворонку за 10 минут: ответы на «дорого», «подумаю»",
      "Подключает группу ВКонтакте",
      "Через неделю: 12 заявок, 3 записались на консультацию",
    ],
    outcome: "Платит 1 490 ₽ — и не думает.",
  },
  {
    tier: "🔵 Pro",
    title: "Мария хочет больше",
    steps: [
      "Получает уведомление: «Можете увеличить заявки на 40% — переходите на Pro»",
      "Переходит на Pro (первый месяц доплата 0 ₽)",
      "Аудит канала показывает: закреплённый пост — мусор",
      "Меняет закреп → +5 заявок в неделю",
      "Контент-план на месяц экономит 10 часов",
    ],
    outcome: "Через месяц 3 490 ₽ окупаются с первой консультации.",
  },
  {
    tier: "🟠 Expert",
    title: "Мария выходит на новый уровень",
    steps: [
      "Открывает модуль «Марафоны под ключ»",
      "За 30 минут собирает марафон «5 дней без вздутия»",
      "Бот ведёт участников и проверяет домашки",
      "В конце марафона — 8 продаж сопровождения по 30 000 ₽",
    ],
    outcome: "Платит 7 990 ₽ в месяц с улыбкой.",
  },
];

export function Scenarios() {
  return (
    <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
      {SCENARIOS.map((s) => (
        <article
          key={s.title}
          className="flex flex-col rounded-lg border border-gray-200 bg-white p-6 shadow-sm"
        >
          <span className="text-xs font-semibold uppercase tracking-wider text-gray-500">
            {s.tier}
          </span>
          <h3 className="mt-2 text-base font-semibold text-gray-900">
            {s.title}
          </h3>
          <ol className="mt-4 flex-1 space-y-2 text-sm text-gray-700">
            {s.steps.map((step, i) => (
              <li key={step} className="flex gap-2">
                <span className="flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-gray-900 text-xs font-semibold text-white">
                  {i + 1}
                </span>
                <span>{step}</span>
              </li>
            ))}
          </ol>
          <p className="mt-4 border-t border-gray-200 pt-3 text-sm font-medium text-gray-900">
            {s.outcome}
          </p>
        </article>
      ))}
    </div>
  );
}
