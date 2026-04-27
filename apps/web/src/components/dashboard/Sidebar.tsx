"use client";

import { X } from "lucide-react";

interface SidebarProps {
  open: boolean;
  onClose: () => void;
}

const NAV_ITEMS = [
  { label: "Дашборд", href: "/" },
  { label: "Контент", href: "/content" },
  { label: "Марафоны", href: "/marathon" },
  { label: "Воронки", href: "/funnel" },
  { label: "Аналитика", href: "/analytics" },
];

export function Sidebar({ open, onClose }: SidebarProps) {
  return (
    <>
      {open && (
        <div
          className="fixed inset-0 z-40 bg-gray-900/40 lg:hidden"
          onClick={onClose}
          aria-hidden
        />
      )}
      <aside
        className={`fixed inset-y-0 left-0 z-50 w-64 transform border-r bg-white transition-transform lg:translate-x-0 ${
          open ? "translate-x-0" : "-translate-x-full"
        }`}
      >
        <div className="flex h-16 items-center justify-between border-b px-4">
          <span className="text-base font-semibold">FishFlow</span>
          <button
            type="button"
            onClick={onClose}
            className="rounded p-2 text-gray-700 hover:bg-gray-100 lg:hidden"
            aria-label="Закрыть меню"
          >
            <X className="h-5 w-5" />
          </button>
        </div>
        <nav className="space-y-1 p-4">
          {NAV_ITEMS.map((item) => (
            <a
              key={item.href}
              href={item.href}
              className="block rounded px-3 py-2 text-sm text-gray-700 hover:bg-gray-100"
            >
              {item.label}
            </a>
          ))}
        </nav>
      </aside>
    </>
  );
}
