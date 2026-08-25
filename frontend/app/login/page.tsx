"use client";

import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";
import { getApiBaseUrl } from "@/lib/api";

export default function LoginPage() {
  const [username, setUsername] = useState("supervisor");
  const [password, setPassword] = useState("password");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const router = useRouter();

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      const res = await fetch(`${getApiBaseUrl()}/auth/token`, {
        method: "POST",
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
        },
        body: new URLSearchParams({
          username,
          password,
          grant_type: "password",
        }),
      });
      if (!res.ok) {
        throw new Error("Login failed");
      }
      const data = await res.json();
      if (typeof window !== "undefined") {
        window.localStorage.setItem("courtops_token", data.access_token);
      }
      router.push("/");
    } catch (err) {
      setError("Invalid credentials or server unavailable.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="mx-auto max-w-md space-y-4 rounded-md border bg-white p-6">
      <h2 className="text-lg font-semibold text-slate-900">Login</h2>
      <p className="text-sm text-slate-600">
        Use the seeded demo accounts, for example <code>supervisor</code> /
        <code>password</code>.
      </p>
      <form className="space-y-3" onSubmit={handleSubmit}>
        <div className="space-y-1">
          <label className="text-xs font-medium text-slate-700">
            Username
          </label>
          <input
            className="w-full rounded-md border px-2 py-1 text-sm"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            autoComplete="username"
          />
        </div>
        <div className="space-y-1">
          <label className="text-xs font-medium text-slate-700">
            Password
          </label>
          <input
            className="w-full rounded-md border px-2 py-1 text-sm"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            autoComplete="current-password"
          />
        </div>
        {error && (
          <div className="rounded-md bg-red-50 px-3 py-2 text-xs text-red-700">
            {error}
          </div>
        )}
        <button
          type="submit"
          disabled={loading}
          className="w-full rounded-md bg-primary px-3 py-1.5 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-60"
        >
          {loading ? "Signing in..." : "Sign in"}
        </button>
      </form>
    </div>
  );
}

