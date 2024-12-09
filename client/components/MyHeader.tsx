// https://ui.mantine.dev/category/headers/#header-tabs

import classes from './MyHeader.module.css';

import packageJson from "../package.json";

import { Container, Flex, Group, Tabs, Text } from '@mantine/core';
import { useRouter } from 'next/router';

type TabProps = {
  label: string;
  link: string;
};

const tabs = [
  { label: 'New Message', link: '/dashboard/new-message' },
  { label: 'Sent', link: '/dashboard/sent' },
  { label: 'Account', link: '/dashboard/account' },
] satisfies TabProps[];

export function MyHeader() {
  const router = useRouter();

  const items = tabs.map((tab) => (
    <Tabs.Tab value={tab.link} key={tab.link} onClick={() => router.push(tab.link)}>
      {tab.label}
    </Tabs.Tab>
  ));

  return (
    <div className={classes.header}>
      <Container className={classes.mainSection} size="sm">
        <Group>
          <Flex gap="sm">
            <Text fw="bolder" component='a' href="/" variant="gradient" gradient={{from: 'blue', to: 'cyan'}}>{packageJson.name}</Text>
          </Flex>
          <Tabs
            value={router.pathname}
            variant="outline"
            classNames={{
              list: classes.tabsList,
              tab: classes.tab,
            }}
          >
            <Tabs.List>{items}</Tabs.List>
          </Tabs>
        </Group>
      </Container>
    </div>
  );
}