import type { NextAuthOptions } from "next-auth";
import CredentialsProvider from "next-auth/providers/credentials";

const API_URL =
  process.env.NEXT_PUBLIC_API_URL ||
  process.env.API_URL ||
  "http://localhost:8000";

const ENVIRONMENT = (process.env.NODE_ENV || "development").toLowerCase();
const IS_PROD = ENVIRONMENT === "production";

if (IS_PROD) {
  if (!process.env.NEXTAUTH_SECRET) {
    // eslint-disable-next-line no-console
    console.error(
      "[auth] NEXTAUTH_SECRET is not set. Sessions will fail. " +
        "Set it in the deployment environment (e.g. Render env vars).",
    );
  }
  if (!process.env.NEXTAUTH_URL) {
    // eslint-disable-next-line no-console
    console.error(
      "[auth] NEXTAUTH_URL is not set. Callbacks may go to the wrong host. " +
        "Set it to the public URL of the deployment (e.g. https://app.example.com).",
    );
  }
}

export const authOptions: NextAuthOptions = {
  debug: !IS_PROD,
  secret: process.env.NEXTAUTH_SECRET,
  session: {
    strategy: "jwt",
    maxAge: 60 * 60 * 24 * 7,
  },
  pages: {
    signIn: "/auth/login",
  },
  logger: {
    error(code, metadata) {
      // eslint-disable-next-line no-console
      console.error(`[auth] error code=${code}`, metadata);
    },
    warn(code) {
      // eslint-disable-next-line no-console
      console.warn(`[auth] warn code=${code}`);
    },
    debug(code, metadata) {
      if (!IS_PROD) {
        // eslint-disable-next-line no-console
        console.debug(`[auth] debug code=${code}`, metadata);
      }
    },
  },
  events: {
    async signIn({ user }) {
      // eslint-disable-next-line no-console
      console.info(`[auth] signIn email=${user?.email}`);
    },
    async signOut({ token }) {
      // eslint-disable-next-line no-console
      console.info(`[auth] signOut sub=${token?.sub}`);
    },
    async session({ session }) {
      if (!IS_PROD) {
        // eslint-disable-next-line no-console
        console.debug(`[auth] session email=${session?.user?.email}`);
      }
    },
  },
  providers: [
    CredentialsProvider({
      name: "Credentials",
      credentials: {
        email: { label: "Email", type: "email" },
        password: { label: "Password", type: "password" },
      },
      async authorize(credentials) {
        if (!credentials?.email || !credentials?.password) {
          // eslint-disable-next-line no-console
          console.warn("[auth] authorize called without credentials");
          return null;
        }

        const url = `${API_URL}/api/v1/auth/login`;
        // eslint-disable-next-line no-console
        console.info(`[auth] authorize email=${credentials.email} url=${url}`);

        let res: Response;
        try {
          res = await fetch(url, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              email: credentials.email,
              password: credentials.password,
            }),
          });
        } catch (e) {
          // eslint-disable-next-line no-console
          console.error("[auth] authorize fetch failed", e);
          return null;
        }

        if (!res.ok) {
          const body = await res.text().catch(() => "<unreadable>");
          // eslint-disable-next-line no-console
          console.error(
            `[auth] authorize backend status=${res.status} body=${body.slice(0, 500)}`,
          );
          return null;
        }

        const data = await res.json().catch((e) => {
          // eslint-disable-next-line no-console
          console.error("[auth] authorize response not JSON", e);
          return null;
        });

        if (!data) return null;

        return {
          id: data.user?.id ?? data.user_id ?? credentials.email,
          email: data.user?.email ?? credentials.email,
          name: data.user?.full_name ?? null,
          accessToken: data.access_token,
          refreshToken: data.refresh_token,
        } as unknown as import("next-auth").User & {
          accessToken?: string;
          refreshToken?: string;
        };
      },
    }),
  ],
  callbacks: {
    async jwt({ token, user }) {
      if (user) {
        const u = user as typeof user & {
          accessToken?: string;
          refreshToken?: string;
        };
        token.accessToken = u.accessToken;
        token.refreshToken = u.refreshToken;
      }
      return token;
    },
    async session({ session, token }) {
      session.accessToken = token.accessToken as string | undefined;
      session.refreshToken = token.refreshToken as string | undefined;
      return session;
    },
  },
};
