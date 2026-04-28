"use client";

import * as Tabs from "@radix-ui/react-tabs";
import * as Accordion from "@radix-ui/react-accordion";
import { ChevronDown } from "lucide-react";

import { MODULES_BY_TIER, Tier } from "@/lib/pricing";

const TAB_LABELS: { value: Tier; label: string }[] = [
  { value: "start", label: "🟢 Start" },
  { value: "pro", label: "🔵 Pro" },
  { value: "expert", label: "🟠 Expert" },
];

export function ModulesByTier() {
  return (
    <Tabs.Root defaultValue="start" className="w-full">
      <Tabs.List
        aria-label="Уровни"
        className="mx-auto mb-6 flex w-fit gap-1 rounded-md border border-gray-200 bg-white p-1 shadow-sm"
      >
        {TAB_LABELS.map((t) => (
          <Tabs.Trigger
            key={t.value}
            value={t.value}
            className="rounded px-4 py-2 text-sm font-medium text-gray-600 data-[state=active]:bg-gray-900 data-[state=active]:text-white"
          >
            {t.label}
          </Tabs.Trigger>
        ))}
      </Tabs.List>

      {TAB_LABELS.map((t) => (
        <Tabs.Content key={t.value} value={t.value}>
          <Accordion.Root
            type="single"
            collapsible
            className="grid grid-cols-1 gap-3 lg:grid-cols-2"
          >
            {MODULES_BY_TIER[t.value].map((m) => (
              <Accordion.Item
                key={m.id}
                value={m.id}
                className="rounded-lg border border-gray-200 bg-white shadow-sm"
              >
                <Accordion.Header>
                  <Accordion.Trigger className="group flex w-full items-center justify-between gap-4 p-5 text-left">
                    <span className="text-sm font-semibold text-gray-900">
                      {m.title}
                    </span>
                    <ChevronDown
                      className="h-4 w-4 shrink-0 text-gray-400 transition-transform duration-200 group-data-[state=open]:rotate-180"
                      aria-hidden
                    />
                  </Accordion.Trigger>
                </Accordion.Header>
                <Accordion.Content className="overflow-hidden text-sm text-gray-700 data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:fade-out data-[state=open]:fade-in">
                  <p className="px-5 pb-5">{m.body}</p>
                </Accordion.Content>
              </Accordion.Item>
            ))}
          </Accordion.Root>
        </Tabs.Content>
      ))}
    </Tabs.Root>
  );
}
