"use client";

import { useState } from "react";
import * as Dialog from "@radix-ui/react-dialog";
import { Check, X } from "lucide-react";
import Link from "next/link";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "";
const FALLBACK_EMAIL = "hello@fishflow.ru";

type SubmitState =
  | { kind: "idle" }
  | { kind: "submitting" }
  | { kind: "success" }
  | { kind: "error"; message: string };

export function EarlyAccessDialog({ trigger }: { trigger: React.ReactNode }) {
  const [open, setOpen] = useState(false);
  const [name, setName] = useState("");
  const [contact, setContact] = useState("");
  const [niche, setNiche] = useState("");
  const [consent, setConsent] = useState(false);
  const [state, setState] = useState<SubmitState>({ kind: "idle" });

  const reset = () => {
    setName("");
    setContact("");
    setNiche("");
    setConsent(false);
    setState({ kind: "idle" });
  };

  const fallbackToMailto = () => {
    const subject = encodeURIComponent("FishFlow — заявка на ранний доступ");
    const body = encodeURIComponent(
      `Имя: ${name}\nКонтакт: ${contact}\nНиша / запрос: ${niche}\n`,
    );
    if (typeof window !== "undefined") {
      window.location.href = `mailto:${FALLBACK_EMAIL}?subject=${subject}&body=${body}`;
    }
  };

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!consent) return;
    setState({ kind: "submitting" });

    if (!API_URL) {
      // Fallback to mailto when no API endpoint is configured.
      fallbackToMailto();
      setState({ kind: "success" });
      return;
    }

    try {
      const res = await fetch(`${API_URL}/api/v1/leads/early-access`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          name,
          contact,
          niche,
          source: "landing_modal",
        }),
      });
      if (!res.ok) {
        const text = await res.text().catch(() => "");
        throw new Error(text || `HTTP ${res.status}`);
      }
      setState({ kind: "success" });
    } catch (err) {
      // eslint-disable-next-line no-console
      console.warn("[early-access] api submit failed, falling back to mailto", err);
      fallbackToMailto();
      setState({ kind: "success" });
    }
  };

  return (
    <Dialog.Root
      open={open}
      onOpenChange={(o) => {
        setOpen(o);
        if (!o) reset();
      }}
    >
      <Dialog.Trigger asChild>{trigger}</Dialog.Trigger>
      <Dialog.Portal>
        <Dialog.Overlay className="fixed inset-0 z-40 bg-gray-900/40 backdrop-blur-sm data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:fade-out data-[state=open]:fade-in" />
        <Dialog.Content className="fixed left-1/2 top-1/2 z-50 w-full max-w-md -translate-x-1/2 -translate-y-1/2 rounded-lg border border-gray-200 bg-white p-6 shadow-xl">
          {state.kind === "success" ? (
            <div className="text-center">
              <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-emerald-100">
                <Check className="h-6 w-6 text-emerald-600" aria-hidden />
              </div>
              <Dialog.Title className="mt-3 text-lg font-semibold text-gray-900">
                Спасибо! Заявка получена.
              </Dialog.Title>
              <Dialog.Description className="mt-2 text-sm text-gray-600">
                Ответим в течение суток. Если письмо не пришло — напишите
                нам прямо на{" "}
                <a
                  href={`mailto:${FALLBACK_EMAIL}`}
                  className="text-primary hover:underline"
                >
                  {FALLBACK_EMAIL}
                </a>
                .
              </Dialog.Description>
              <Dialog.Close asChild>
                <button
                  type="button"
                  className="mt-6 w-full rounded-md bg-gray-900 px-4 py-2 text-sm font-medium text-white hover:bg-gray-800"
                >
                  Закрыть
                </button>
              </Dialog.Close>
            </div>
          ) : (
            <>
              <div className="flex items-start justify-between">
                <Dialog.Title className="text-lg font-semibold text-gray-900">
                  Заявка на ранний доступ
                </Dialog.Title>
                <Dialog.Close asChild>
                  <button
                    type="button"
                    className="rounded p-1 text-gray-500 hover:bg-gray-100"
                    aria-label="Закрыть"
                  >
                    <X className="h-4 w-4" />
                  </button>
                </Dialog.Close>
              </div>
              <Dialog.Description className="mt-1 text-sm text-gray-600">
                Расскажите о себе — ответим в течение суток.
              </Dialog.Description>

              <form className="mt-4 space-y-4" onSubmit={onSubmit}>
                <div>
                  <label
                    htmlFor="ea-name"
                    className="block text-sm font-medium text-gray-700"
                  >
                    Имя
                  </label>
                  <input
                    id="ea-name"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    required
                    autoComplete="name"
                    className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 text-sm shadow-sm focus:border-primary focus:outline-none focus:ring-primary"
                  />
                </div>
                <div>
                  <label
                    htmlFor="ea-contact"
                    className="block text-sm font-medium text-gray-700"
                  >
                    Email или Telegram
                  </label>
                  <input
                    id="ea-contact"
                    value={contact}
                    onChange={(e) => setContact(e.target.value)}
                    required
                    placeholder="name@mail.com или @username"
                    className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 text-sm shadow-sm focus:border-primary focus:outline-none focus:ring-primary"
                  />
                </div>
                <div>
                  <label
                    htmlFor="ea-niche"
                    className="block text-sm font-medium text-gray-700"
                  >
                    Ниша или с чем хотите помочь
                  </label>
                  <textarea
                    id="ea-niche"
                    value={niche}
                    onChange={(e) => setNiche(e.target.value)}
                    rows={3}
                    placeholder="Например: нутрициолог, нужны лиды через ВК и марафоны"
                    className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 text-sm shadow-sm focus:border-primary focus:outline-none focus:ring-primary"
                  />
                </div>

                <label className="flex items-start gap-2 text-xs text-gray-600">
                  <input
                    type="checkbox"
                    checked={consent}
                    onChange={(e) => setConsent(e.target.checked)}
                    required
                    className="mt-0.5 h-4 w-4 shrink-0 rounded border-gray-300 text-primary focus:ring-primary"
                  />
                  <span>
                    Я согласен с{" "}
                    <Link
                      href="/oferta"
                      className="text-primary hover:underline"
                      target="_blank"
                    >
                      офертой
                    </Link>{" "}
                    и{" "}
                    <Link
                      href="/privacy"
                      className="text-primary hover:underline"
                      target="_blank"
                    >
                      обработкой персональных данных
                    </Link>
                    .
                  </span>
                </label>

                {state.kind === "error" && (
                  <p className="rounded-md bg-rose-50 px-3 py-2 text-xs text-rose-700">
                    {state.message}
                  </p>
                )}

                <div className="flex justify-end gap-2 pt-2">
                  <Dialog.Close asChild>
                    <button
                      type="button"
                      className="rounded-md border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-100"
                    >
                      Отмена
                    </button>
                  </Dialog.Close>
                  <button
                    type="submit"
                    disabled={state.kind === "submitting" || !consent}
                    className="rounded-md bg-primary px-4 py-2 text-sm font-medium text-white hover:bg-primary/90 disabled:opacity-50"
                  >
                    {state.kind === "submitting"
                      ? "Отправляем..."
                      : "Отправить"}
                  </button>
                </div>
              </form>
            </>
          )}
        </Dialog.Content>
      </Dialog.Portal>
    </Dialog.Root>
  );
}
