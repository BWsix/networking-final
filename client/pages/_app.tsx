import "@mantine/core/styles.css";
import Head from "next/head";
import { MantineProvider } from "@mantine/core";
import { theme } from "../theme";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { MyAppShell } from "../components/MyAppShell";
import packageJson from "../package.json";

const queryClient = new QueryClient()

export default function App({ Component, pageProps }: any) {
  return (
    <MantineProvider theme={theme}>
      <QueryClientProvider client={queryClient}>
        <Head>
          <title>{packageJson.name}</title>
          <meta
            name="viewport"
            content="minimum-scale=1, initial-scale=1, width=device-width, user-scalable=no"
          />
          <link rel="shortcut icon" href="/favicon.svg" />
        </Head>
        <MyAppShell>
          <Component {...pageProps} />
        </MyAppShell>
      </QueryClientProvider>
    </MantineProvider>
  );
}
