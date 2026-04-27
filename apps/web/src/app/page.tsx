"use client";

import { useSession, signIn } from "next-auth/react";
import { useRouter } from "next/navigation";
import { useEffect } from "react";
import { Dashboard } from "@/components/dashboard/Dashboard";
import { useAuthStore } from "@/store/useAuthStore";

export default function HomePage() {
  const { data: session, status } = useSession();
  const router = useRouter();
  const { setUser, setToken } = useAuthStore();

  useEffect(() => {
    if (status === "authenticated" && session) {
      setUser(session.user as any);
      setToken(session.accessToken as string);
    } else if (status === "unauthenticated") {
      router.push("/auth/login");
    }
  }, [status, session, router, setUser, setToken]);

  if (status === "loading") {
    return (
      <div className="flex h-screen items-center justify-center">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
      </div>
    );
  }

  if (status === "authenticated") {
    return <Dashboard />;
  }

  return null;
}
