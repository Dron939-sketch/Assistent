"use client";

import { useState } from "react";
import { signIn } from "next-auth/react";
import { useRouter } from "next/navigation";
import { useForm } from "react-hook-form";
import toast from "react-hot-toast";
import Link from "next/link";

import { api } from "@/lib/api-client";

interface RegisterForm {
  full_name: string;
  email: string;
  password: string;
  password_confirm: string;
}

export default function RegisterPage() {
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(false);
  const {
    register,
    handleSubmit,
    watch,
    formState: { errors },
  } = useForm<RegisterForm>();

  const password = watch("password");

  const onSubmit = async (data: RegisterForm) => {
    setIsLoading(true);
    // eslint-disable-next-line no-console
    console.info("[register] submit", { email: data.email });
    try {
      await api.auth.register({
        email: data.email,
        password: data.password,
        full_name: data.full_name,
      });

      const result = await signIn("credentials", {
        email: data.email,
        password: data.password,
        redirect: false,
      });

      if (result?.error) {
        // eslint-disable-next-line no-console
        console.error("[register] signIn after register failed", result);
        toast.error(
          "Регистрация прошла, но войти не удалось. Попробуйте на странице входа.",
        );
        router.push("/auth/login");
        return;
      }

      toast.success("Аккаунт создан");
      router.push("/");
    } catch (e: unknown) {
      // eslint-disable-next-line no-console
      console.error("[register] failed", e);
      const message =
        (e as { response?: { data?: { detail?: string } } })?.response?.data?.detail ||
        "Не удалось создать аккаунт";
      toast.error(message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="w-full max-w-md space-y-8">
        <div>
          <h2 className="mt-6 text-center text-3xl font-bold tracking-tight text-gray-900">
            Регистрация временно закрыта
          </h2>
          <p className="mt-2 text-center text-sm text-gray-600">
            Мы подключаем доступ вручную для пилотных пользователей.{" "}
            <Link href="/" className="font-medium text-primary hover:text-primary/80">
              Вернуться на главную
            </Link>
            .
          </p>
        </div>

        <form className="mt-8 space-y-6" onSubmit={handleSubmit(onSubmit)}>
          <div className="space-y-4 rounded-md">
            <div>
              <label htmlFor="full_name" className="block text-sm font-medium text-gray-700">
                Имя
              </label>
              <input
                id="full_name"
                {...register("full_name", { required: "Укажите имя" })}
                type="text"
                autoComplete="name"
                className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-primary focus:outline-none focus:ring-primary sm:text-sm"
              />
              {errors.full_name && (
                <p className="mt-1 text-sm text-red-600">{errors.full_name.message}</p>
              )}
            </div>

            <div>
              <label htmlFor="email" className="block text-sm font-medium text-gray-700">
                Email
              </label>
              <input
                id="email"
                {...register("email", {
                  required: "Email обязателен",
                  pattern: { value: /^[^\s@]+@[^\s@]+\.[^\s@]+$/, message: "Некорректный email" },
                })}
                type="email"
                autoComplete="email"
                className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-primary focus:outline-none focus:ring-primary sm:text-sm"
              />
              {errors.email && (
                <p className="mt-1 text-sm text-red-600">{errors.email.message}</p>
              )}
            </div>

            <div>
              <label htmlFor="password" className="block text-sm font-medium text-gray-700">
                Пароль
              </label>
              <input
                id="password"
                {...register("password", {
                  required: "Пароль обязателен",
                  minLength: { value: 8, message: "Минимум 8 символов" },
                })}
                type="password"
                autoComplete="new-password"
                className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-primary focus:outline-none focus:ring-primary sm:text-sm"
              />
              {errors.password && (
                <p className="mt-1 text-sm text-red-600">{errors.password.message}</p>
              )}
            </div>

            <div>
              <label htmlFor="password_confirm" className="block text-sm font-medium text-gray-700">
                Повторите пароль
              </label>
              <input
                id="password_confirm"
                {...register("password_confirm", {
                  required: "Повторите пароль",
                  validate: (value) => value === password || "Пароли не совпадают",
                })}
                type="password"
                autoComplete="new-password"
                className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-primary focus:outline-none focus:ring-primary sm:text-sm"
              />
              {errors.password_confirm && (
                <p className="mt-1 text-sm text-red-600">{errors.password_confirm.message}</p>
              )}
            </div>
          </div>

          <button
            type="submit"
            disabled={isLoading}
            className="group relative flex w-full justify-center rounded-md bg-primary px-4 py-2 text-sm font-medium text-white hover:bg-primary/90 focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2 disabled:opacity-50"
          >
            {isLoading ? "Создаём аккаунт..." : "Зарегистрироваться"}
          </button>
        </form>
      </div>
    </div>
  );
}
