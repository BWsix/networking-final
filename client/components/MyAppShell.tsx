// https://mantine.dev/core/app-shell/

import { AppShell, Container } from '@mantine/core';
import { MyHeader } from './MyHeader';
import { useRouter } from 'next/router';

interface MyAppShellProps {
  children: React.ReactNode;
}

export function MyAppShell(props: MyAppShellProps) {
  const router = useRouter();

  const dashboard = router.pathname.startsWith("/dashboard");

  return (
    <AppShell
      header={{ height: 0, collapsed: false }}
      padding="sm"
    >
      {dashboard && (
        <AppShell.Header zIndex={150}>
          <MyHeader />
        </AppShell.Header>
      )}

      {dashboard ? (
        <AppShell.Main m={0} p={0}>
          <Container size="sm" pt={50}>
            {props.children}
          </Container>
        </AppShell.Main>
      ) : (
        <AppShell.Main m={0} p={0}>
          {props.children}
        </AppShell.Main>
      )}
    </AppShell>
  );
}