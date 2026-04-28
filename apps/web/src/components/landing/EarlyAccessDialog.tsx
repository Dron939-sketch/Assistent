"use client";

import { useState } from "react";
import * as Dialog from "@radix-ui/react-dialog";
import { X } from "lucide-react";

const MAIL_TO = "hello@fishflow.ru";

export function EarlyAccessDialog({ trigger }: { trigger: React.ReactNode }) {
  const [open, setOpen] = useState(false);
  const [name, setName] = useState("");
  const [contact, setContact] = useState("");
  const [niche, setNiche] = useState("");

  const onSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const subject = encodeURIComponent("FishFlow — заявка на ранний доступ");
    const body = encodeURIComponent(
      `Имя: ${name}\nКонтакт: ${contact}\nНиша / запрос: ${niche}\n`,
    );
    window.location.href = `mailto:${MAIL_TO}?subject=${subject}&body=${body}`;
    setOpen(false);
  };

  return (
    <Dialog.Root open={open} onOpenChange={setOpen}>
      <Dialog.Trigger asChild>{trigger}</Dialog.Trigger>
      <Dialog.Portal>
        <Dialog.Overlay className="fixed inset-0 z-40 bg-gray-900/40 backdrop-blur-sm data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:fade-out data-[state=open]:fade-in" />
        <Dialog.Content className="fixed left-1/2 top-1/2 z-50 w-full max-w-md -translate-x-1/2 -translate-y-1/2 rounded-lg border border-gray-200 bg-white p-6 shadow-xl">
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
            Расскажите о себе — ответим в течение суток. Заявка откроется в
            вашем почтовом клиенте, отправите оттуда.
          </Dialog.Description>

          <form className="mt-4 space-y-4" onSubmit={onSubmit}>
            <div>
              <label htmlFor="ea-name" className="block text-sm font-medium text-gray-700">
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
              <label htmlFor="ea-contact" className="block text-sm font-medium text-gray-700">
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
              <label htmlFor="ea-niche" className="block text-sm font-medium text-gray-700">
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
                className="rounded-md bg-primary px-4 py-2 text-sm font-medium text-white hover:bg-primary/90"
              >
                Отправить
              </button>
            </div>
          </form>
        </Dialog.Content>
      </Dialog.Portal>
    </Dialog.Root>
  );
}
