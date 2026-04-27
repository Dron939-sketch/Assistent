"use client";

import { Menu } from "lucide-react";

interface HeaderProps {
  onMenuClick: () => void;
}

export function Header({ onMenuClick }: HeaderProps) {
  return (
    <header className="sticky top-0 z-30 flex h-16 items-center justify-between border-b bg-white px-4 sm:px-6 lg:px-8">
      <button
        type="button"
        onClick={onMenuClick}
        className="rounded p-2 text-gray-700 hover:bg-gray-100 lg:hidden"
        aria-label="Открыть меню"
      >
        <Menu className="h-5 w-5" />
      </button>
      <h1 className="text-base font-semibold text-gray-900">FishFlow</h1>
      <div />
    </header>
  );
}
