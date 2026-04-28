"use client";

import * as Accordion from "@radix-ui/react-accordion";
import { ChevronDown } from "lucide-react";

const QA: { q: string; a: string }[] = [
  {
    q: "Сколько времени занимает запуск?",
    a: "10–30 минут на тариф Start. Подключаете VK или Telegram, выбираете нишевый Pack, отвечаете на 5 вопросов — бот начинает отвечать клиентам.",
  },
  {
    q: "Можно ли начать без подписки?",
    a: "Да. 14 дней бесплатно на любом тарифе. Платёж списывается только если вы решите остаться, и в первый месяц мы не списываем разницу при апгрейде.",
  },
  {
    q: "Я не в нутрициологии. Подойдёт ли мне?",
    a: "Подойдёт. Сейчас 7 нишевых пресетов покрывают 65+ профессий: от психолога и фитнес-тренера до таролога, юриста и репетитора. Если вашей ниши нет — соберём за 5 рабочих дней.",
  },
  {
    q: "Как AI пишет в моём стиле?",
    a: "Берёт 10–20 ваших постов или 2 минуты голосовой записи и подстраивает голос. Стиль можно править вручную в любой момент.",
  },
  {
    q: "Не подставите ли меня в регулируемой нише?",
    a: "Для медицины, психотерапии с лицензией, юриспруденции и финансов мы предлагаем Compliance Pack: усиленные дисклеймеры, гард-рейлы, человек-в-петле для риск-операций. Все сгенерированные тексты можно редактировать перед публикацией.",
  },
  {
    q: "Что если уйдёте? Заберу ли я свои данные?",
    a: "Все ваши контакты, тексты и шаблоны можно выгрузить в CSV/JSON в один клик. Никакого vendor lock-in.",
  },
  {
    q: "А годовая подписка дешевле?",
    a: "Да, при предоплате на 12 месяцев — скидка 20%.",
  },
];

export function FAQ() {
  return (
    <Accordion.Root type="single" collapsible className="space-y-3">
      {QA.map((item, i) => (
        <Accordion.Item
          key={i}
          value={`faq-${i}`}
          className="rounded-lg border border-gray-200 bg-white shadow-sm"
        >
          <Accordion.Header>
            <Accordion.Trigger className="group flex w-full items-center justify-between gap-4 p-5 text-left">
              <span className="text-sm font-medium text-gray-900">
                {item.q}
              </span>
              <ChevronDown
                className="h-4 w-4 shrink-0 text-gray-400 transition-transform duration-200 group-data-[state=open]:rotate-180"
                aria-hidden
              />
            </Accordion.Trigger>
          </Accordion.Header>
          <Accordion.Content className="overflow-hidden text-sm text-gray-700 data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:fade-out data-[state=open]:fade-in">
            <p className="px-5 pb-5">{item.a}</p>
          </Accordion.Content>
        </Accordion.Item>
      ))}
    </Accordion.Root>
  );
}
