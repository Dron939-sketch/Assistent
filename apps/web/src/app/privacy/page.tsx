import Link from "next/link";
import type { Metadata } from "next";

import { SELLER } from "@/lib/pricing";

export const metadata: Metadata = {
  title: "Политика обработки персональных данных",
  description:
    "Политика обработки персональных данных FishFlow в соответствии с 152-ФЗ.",
  robots: { index: false, follow: true },
};

export default function PrivacyPage() {
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

      <article className="mx-auto max-w-3xl px-6 py-12 text-sm leading-relaxed text-gray-800">
        <p className="text-xs uppercase tracking-wider text-gray-500">
          Действует с {SELLER.effectiveDate}
        </p>
        <h1 className="mt-2 text-3xl font-bold tracking-tight">
          Политика обработки персональных данных
        </h1>

        <p className="mt-4">
          Настоящая Политика разработана {SELLER.legalName} (ИНН{" "}
          {SELLER.inn}, ОГРНИП {SELLER.ogrnip}) — далее «Оператор» — в
          соответствии с Федеральным законом от 27.07.2006 № 152-ФЗ
          «О персональных данных» и определяет порядок обработки
          персональных данных пользователей сайта и сервиса FishFlow.
        </p>

        <h2 className="mt-8 text-xl font-semibold">1. Общие положения</h2>
        <p className="mt-2">
          1.1. Используя сайт и сервис, пользователь подтверждает, что
          ознакомлен с настоящей Политикой и даёт согласие на обработку
          своих персональных данных Оператором.
        </p>
        <p className="mt-2">
          1.2. Если пользователь не согласен с условиями обработки, он
          обязан прекратить использование сайта и сервиса.
        </p>

        <h2 className="mt-8 text-xl font-semibold">
          2. Какие данные собираются
        </h2>
        <ul className="ml-5 mt-2 list-disc space-y-1">
          <li>имя и фамилия;</li>
          <li>адрес электронной почты;</li>
          <li>номер телефона и/или ник в Telegram;</li>
          <li>идентификатор страницы ВКонтакте, токен сообщества;</li>
          <li>ниша / специализация эксперта;</li>
          <li>тексты, сгенерированные через AI-ассистент;</li>
          <li>
            технические данные (IP, тип устройства, браузер, страницы
            посещения);
          </li>
          <li>платёжная информация — обрабатывается напрямую платёжным
            оператором, Оператор её не хранит.</li>
        </ul>

        <h2 className="mt-8 text-xl font-semibold">3. Цели обработки</h2>
        <ul className="ml-5 mt-2 list-disc space-y-1">
          <li>предоставление функций сервиса в рамках выбранного тарифа;</li>
          <li>идентификация пользователя в личном кабинете;</li>
          <li>отправка уведомлений (новые лиды, статус подписки);</li>
          <li>обработка платежей через платёжного партнёра;</li>
          <li>аналитика использования сервиса в обезличенной форме;</li>
          <li>исполнение обязательств перед пользователем по оферте.</li>
        </ul>

        <h2 className="mt-8 text-xl font-semibold">
          4. Передача данных третьим лицам
        </h2>
        <p className="mt-2">
          4.1. Оператор не передаёт персональные данные третьим лицам без
          согласия пользователя, за исключением случаев, прямо
          предусмотренных законодательством Российской Федерации.
        </p>
        <p className="mt-2">
          4.2. Технологические партнёры, обеспечивающие работу сервиса
          (хостинг, платёжный шлюз, сервисы AI-моделей), получают только
          тот минимум данных, который необходим для оказания их услуг,
          и обязаны обеспечивать их конфиденциальность.
        </p>

        <h2 className="mt-8 text-xl font-semibold">
          5. Срок и условия хранения
        </h2>
        <p className="mt-2">
          5.1. Персональные данные хранятся на серверах в Российской
          Федерации (или в иной юрисдикции с эквивалентным уровнем защиты)
          в течение всего срока действия подписки пользователя и 12
          месяцев после её прекращения, после чего удаляются.
        </p>
        <p className="mt-2">
          5.2. Пользователь вправе в любой момент потребовать удаления или
          выгрузки своих данных по запросу на{" "}
          <a
            href={`mailto:${SELLER.email}`}
            className="text-primary hover:underline"
          >
            {SELLER.email}
          </a>
          .
        </p>

        <h2 className="mt-8 text-xl font-semibold">
          6. Защита персональных данных
        </h2>
        <p className="mt-2">
          Оператор принимает технические и организационные меры для защиты
          данных от несанкционированного доступа, изменения, раскрытия или
          уничтожения: шифрование на уровне канала (TLS), хеширование
          паролей, ограничение доступа сотрудников к данным.
        </p>

        <h2 className="mt-8 text-xl font-semibold">
          7. Изменения в Политике
        </h2>
        <p className="mt-2">
          Оператор вправе изменять настоящую Политику. Актуальная версия
          всегда доступна по адресу <code>/privacy</code>. Существенные
          изменения публикуются за 14 дней до вступления в силу.
        </p>

        <h2 className="mt-8 text-xl font-semibold">8. Контакты</h2>
        <p className="mt-2">
          {SELLER.legalName}. Email для запросов:{" "}
          <a
            href={`mailto:${SELLER.email}`}
            className="text-primary hover:underline"
          >
            {SELLER.email}
          </a>
          . Адрес: {SELLER.address}.
        </p>
      </article>

      <footer className="border-t border-gray-200 bg-white">
        <div className="mx-auto flex max-w-3xl flex-col items-center gap-2 px-6 py-8 text-xs text-gray-500 sm:flex-row sm:justify-between">
          <span>© FishFlow. Все права защищены.</span>
          <span className="flex gap-4">
            <Link href="/oferta" className="hover:text-gray-900">
              Оферта
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
