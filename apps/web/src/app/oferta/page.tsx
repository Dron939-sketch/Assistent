import Link from "next/link";
import type { Metadata } from "next";

import { SELLER, TIERS } from "@/lib/pricing";

export const metadata: Metadata = {
  title: "Публичная оферта",
  description:
    "Публичная оферта FishFlow о заключении договора на оказание информационно-консультационных услуг.",
  robots: { index: false, follow: true },
};

const formatPrice = (rub: number) => `${rub.toLocaleString("ru-RU")} ₽`;

export default function OfertaPage() {
  return (
    <main className="min-h-screen bg-gray-50 text-gray-900">
      <header className="border-b border-gray-200 bg-white">
        <div className="mx-auto flex max-w-3xl items-center justify-between px-6 py-4">
          <Link href="/" className="text-lg font-semibold">
            FishFlow
          </Link>
          <Link href="/" className="text-sm text-gray-600 hover:text-gray-900">
            ← На главную
          </Link>
        </div>
      </header>

      <article className="prose mx-auto max-w-3xl px-6 py-12 text-sm leading-relaxed text-gray-800">
        <p className="text-xs uppercase tracking-wider text-gray-500">
          Действует с {SELLER.effectiveDate}
        </p>
        <h1 className="mt-2 text-3xl font-bold tracking-tight">
          Публичная оферта о заключении договора на оказание услуг
        </h1>
        <p className="mt-4">
          Настоящий документ является публичной офертой {SELLER.legalName}{" "}
          (далее — Исполнитель, ИНН {SELLER.inn}, ОГРНИП {SELLER.ogrnip},
          адрес: {SELLER.address}), адресованной любому физическому или
          юридическому лицу (далее — Заказчик), и определяет условия
          оказания информационно-консультационных и сервисных услуг через
          платформу FishFlow.
        </p>

        <h2 className="mt-8 text-xl font-semibold">1. Предмет договора</h2>
        <p className="mt-2">
          1.1. Исполнитель предоставляет Заказчику доступ к программному
          сервису FishFlow и связанным AI-ассистентам, обеспечивающим
          автоматизацию работы эксперта в социальных сетях: ответы в
          сообщениях, генерация контента, управление марафонами,
          аналитика и сопутствующие функции.
        </p>
        <p className="mt-2">
          1.2. Перечень функций, доступных Заказчику, определяется
          выбранным тарифом и подключёнными аддонами.
        </p>

        <h2 className="mt-8 text-xl font-semibold">2. Тарифы и оплата</h2>
        <ul className="ml-5 mt-2 list-disc space-y-1">
          {TIERS.map((t) => (
            <li key={t.id}>
              <strong>{t.name}</strong> — {formatPrice(t.price)} в месяц.
            </li>
          ))}
        </ul>
        <p className="mt-3">
          2.1. Оплата производится посредством платёжных систем,
          интегрированных в платформу. Возможны рублёвые подписки с
          ежемесячным или ежегодным списанием.
        </p>
        <p className="mt-2">
          2.2. Первые 14 (четырнадцать) календарных дней пользования
          сервисом предоставляются бесплатно. Списание начинается по
          истечении этого срока, если Заказчик не отменил подписку.
        </p>
        <p className="mt-2">
          2.3. При апгрейде тарифа разница в цене за первые 30 дней не
          списывается.
        </p>

        <h2 className="mt-8 text-xl font-semibold">
          3. Права и обязанности сторон
        </h2>
        <p className="mt-2">
          3.1. Исполнитель обязуется поддерживать работоспособность
          сервиса, своевременно устранять сбои и обеспечивать
          конфиденциальность персональных данных Заказчика в
          соответствии с{" "}
          <Link href="/privacy" className="text-primary hover:underline">
            Политикой обработки персональных данных
          </Link>
          .
        </p>
        <p className="mt-2">
          3.2. Заказчик обязуется не использовать сервис для рассылки
          спама, мошенничества, нарушения прав третьих лиц или
          распространения запрещённого законодательством контента.
        </p>

        <h2 className="mt-8 text-xl font-semibold">
          4. Ответственность и гарантии
        </h2>
        <p className="mt-2">
          4.1. Сервис предоставляется «как есть». Исполнитель не
          гарантирует конкретного количества заявок, продаж, охватов или
          иных коммерческих результатов.
        </p>
        <p className="mt-2">
          4.2. Исполнитель не несёт ответственности за содержание
          текстов, опубликованных Заказчиком на основании рекомендаций
          AI-ассистента, в том числе в регулируемых нишах (медицина,
          юриспруденция, финансы). Финальная проверка и публикация
          контента — ответственность Заказчика.
        </p>
        <p className="mt-2">
          4.3. В случае технического сбоя сервиса Исполнитель компенсирует
          неоказанную услугу пропорциональным продлением периода
          подписки.
        </p>

        <h2 className="mt-8 text-xl font-semibold">5. Возврат средств</h2>
        <p className="mt-2">
          5.1. Заказчик вправе отказаться от подписки в любое время через
          личный кабинет; списание средств прекращается со следующего
          расчётного периода.
        </p>
        <p className="mt-2">
          5.2. Возврат средств за уже оказанные услуги не производится,
          если иное не установлено законодательством Российской Федерации.
        </p>

        <h2 className="mt-8 text-xl font-semibold">6. Реквизиты</h2>
        <p className="mt-2">
          {SELLER.legalName}, ИНН {SELLER.inn}, ОГРНИП {SELLER.ogrnip},{" "}
          {SELLER.address}. Email для связи:{" "}
          <a
            href={`mailto:${SELLER.email}`}
            className="text-primary hover:underline"
          >
            {SELLER.email}
          </a>
          .
        </p>
      </article>

      <footer className="border-t border-gray-200 bg-white">
        <div className="mx-auto flex max-w-3xl flex-col items-center gap-2 px-6 py-8 text-xs text-gray-500 sm:flex-row sm:justify-between">
          <span>© FishFlow. Все права защищены.</span>
          <span className="flex gap-4">
            <Link href="/privacy" className="hover:text-gray-900">
              Политика
            </Link>
            <Link href="/" className="hover:text-gray-900">
              Главная
            </Link>
          </span>
        </div>
      </footer>
    </main>
  );
}
