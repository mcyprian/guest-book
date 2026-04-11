"use client";

import { useRouter } from "next/navigation";
import { useCallback, useEffect, useState } from "react";

import { isAuthenticated, login as apiLogin, logout as apiLogout } from "@/lib/api";

export function useAuth() {
  const router = useRouter();
  const [authenticated, setAuthenticated] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setAuthenticated(isAuthenticated());
    setLoading(false);
  }, []);

  const login = useCallback(
    async (email: string, password: string) => {
      await apiLogin(email, password);
      setAuthenticated(true);
      router.push("/guests");
    },
    [router],
  );

  const logout = useCallback(() => {
    apiLogout();
    setAuthenticated(false);
  }, []);

  return { authenticated, loading, login, logout };
}
