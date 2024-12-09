import { useQuery } from "@tanstack/react-query";
import { useState, useEffect } from "react";
import { getMe, handleRetry } from "../src/api";
import { useRouter } from "next/router";

export interface User {
  username: string;
  email: string;
}

export function useMeQuery() {
  const router = useRouter();

  const query = useQuery({
    queryKey: ['getMe'],
    queryFn: getMe,
    retry: (failureCount, error) => {
      return handleRetry(failureCount, error, (failureCount, error) => {
        // unauthorized
        if (error.status === 401) {
          router.push("/login");
          return false;
        }
      });
    }
  });

  return {
    isLoading: query.isLoading,
    isError: query.isError,
    error: query.error?.message || "Unknown error",
    user: query.data?.data || null,
  };
}