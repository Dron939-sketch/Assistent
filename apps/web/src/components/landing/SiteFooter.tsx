import Link from "next/link";

import { SELLER } from "@/lib/pricing";

export function SiteFooter() {
  return (
    <footer className="border-t border-gray-200 bg-white">
      <div className="mx-auto flex max-w-6xl flex-col gap-6 px-6 py-10 text-xs text-gray-500 sm:flex-row sm:justify-between">
        <div className="space-y-2">
          <span className="block font-semibold text-gray-700">
            © FishFlow. Все права защищены.
          </span>
          <span className="block">
            {SELLER.legalName} · ИНН {SELLER.inn}
          </span>
          <span className="block">{SELLER.address}</span>
          <a
            href={`mailto:${SELLER.email}`}
            className="block text-primary hover:underline"
          >
            {SELLER.email}
          </a>
        </div>
        <nav className="flex flex-wrap gap-x-4 gap-y-2">
          <Link href="/" className="hover:text-gray-900">
            Главная
          </Link>
          <Link href="/studio" className="hover:text-gray-900">
            White-label
          </Link>
          <Link href="/oferta" className="hover:text-gray-900">
            Оферта
          </Link>
          <Link href="/privacy" className="hover:text-gray-900">
            Политика ПДн
          </Link>
        </nav>
      </div>
    </footer>
  );
}
