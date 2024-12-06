import { Button, Group } from "@mantine/core";
import { getMe, getUsers, handleRetry, logout } from "../src/api";
import { useQuery } from '@tanstack/react-query'
import Link from "next/link";

export default function IndexPage() {
  const query = useQuery({
    queryKey: ['getMe'],
    queryFn: getMe,
    retry: (failureCount, error) => {
      return handleRetry(failureCount, error, (failureCount, error) => {
        // unauthorized
        if (error.status === 401) {
          return false;
        }
      });
    }
  })

  return (
    <>
      <Group mt={50} justify="center">
        {query.isLoading ? (
          "Loading..."
        ) : query.isError ? (
          query.error.message || "An error occurred"
        ) : (
          <div>
            <p>Welcome, {query.data?.data.username}</p>
            <p>Your email is {query.data?.data.email}</p>
          </div>
        )}
      </Group>
      <Group mt={50} justify="center">
        <Link href="/register">
          register
        </Link>
        <Link href="/login">
          login
        </Link>
        <Link href="#" onClick={logout}>
          logout
        </Link>
      </Group>
    </>
  );
}
