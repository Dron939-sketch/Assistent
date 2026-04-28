interface Quote {
  name: string;
  role: string;
  quote: string;
  metric: string;
}

const QUOTES: Quote[] = [
  {
    name: "Мария Л.",
    role: "Нутрициолог, тариф Start",
    quote:
      "За первую неделю автоворонка собрала 12 заявок. Раньше я не успевала отвечать в директе — теперь это просто перестало быть моей задачей.",
    metric: "+12 заявок / 7 дней",
  },
  {
    name: "Анна К.",
    role: "Психолог, тариф Pro",
    quote:
      "Аудит показал, что мой закреп работает вхолостую. Поменяла его и подключила контент-план — выросла вовлечённость и стало приходить больше тёплых лидов.",
    metric: "+40% к заявкам / месяц",
  },
  {
    name: "Дмитрий С.",
    role: "Бизнес-коуч, тариф Expert",
    quote:
      "Запустил марафон за выходные и продал 8 сопровождений. Раньше такая же кампания занимала у меня 3 недели и команду из двух человек.",
    metric: "8 продаж / 5 дней",
  },
];

export function Testimonials() {
  return (
    <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
      {QUOTES.map((q) => (
        <figure
          key={q.name}
          className="flex flex-col rounded-lg border border-gray-200 bg-white p-6 shadow-sm"
        >
          <span className="text-xs font-semibold uppercase tracking-wider text-emerald-700">
            {q.metric}
          </span>
          <blockquote className="mt-3 flex-1 text-sm text-gray-700">
            «{q.quote}»
          </blockquote>
          <figcaption className="mt-4 border-t border-gray-200 pt-3 text-sm">
            <span className="font-semibold text-gray-900">{q.name}</span>
            <span className="block text-xs text-gray-500">{q.role}</span>
          </figcaption>
        </figure>
      ))}
    </div>
  );
}
