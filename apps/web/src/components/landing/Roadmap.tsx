type Stage = {
  number: string;
  title: string;
  duration: string;
  result: string;
};

const STAGES: Stage[] = [
  {
    number: "1",
    title: "Ядро (Start)",
    duration: "4–6 недель",
    result:
      "Автоворонка + автоответы + сбор заявок + платежи. Эксперт собирает первые лиды.",
  },
  {
    number: "2",
    title: "Рост (Pro)",
    duration: "+4 недели",
    result:
      "Аудит, контент-план, генератор постов, автопостинг. Стабильный поток клиентов.",
  },
  {
    number: "3",
    title: "Масштаб (Expert)",
    duration: "+6 недель",
    result:
      "Марафоны, личный бренд, лендинги, аналитика. Эксперт — бренд, не зависит от команды.",
  },
  {
    number: "4",
    title: "White-label",
    duration: "параллельно",
    result:
      "Клонирование под другие ниши: психолог, таролог, фитнес-тренер, коуч.",
  },
];

export function Roadmap() {
  return (
    <ol className="relative space-y-6 border-l border-gray-200 pl-6">
      {STAGES.map((s) => (
        <li key={s.number} className="relative">
          <span className="absolute -left-[33px] flex h-8 w-8 items-center justify-center rounded-full border border-gray-200 bg-white text-sm font-semibold text-gray-900 shadow-sm">
            {s.number}
          </span>
          <div className="rounded-lg border border-gray-200 bg-white p-5 shadow-sm">
            <div className="flex flex-wrap items-baseline justify-between gap-2">
              <h3 className="text-base font-semibold text-gray-900">
                {s.title}
              </h3>
              <span className="text-xs uppercase tracking-wider text-gray-500">
                {s.duration}
              </span>
            </div>
            <p className="mt-2 text-sm text-gray-600">{s.result}</p>
          </div>
        </li>
      ))}
    </ol>
  );
}
