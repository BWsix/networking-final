import { IconApi, IconCookie, IconGauge, IconLock, IconMail, IconUser } from '@tabler/icons-react';
import {
  Badge,
  Card,
  Container,
  Group,
  SimpleGrid,
  Text,
  Title,
  useMantineTheme,
} from '@mantine/core';
import classes from './MyFeatures.module.css';

const mockdata = [
  {
    title: 'Socket Mail Sender',
    description: 'Powered by NTUST’s SMTP server and only the Python’s built-in socket library, this app delivers mails with minimal dependencies.',
    icon: IconMail,
  },
  {
    title: 'Custom API Framework',
    description: 'Backed by a custom API framework built from the ground up with only Python’s built-in socket library',
    icon: IconApi,
  },
  {
    title: 'User Authentication',
    description: 'Secured by a custom user authentication system, never worry about your data being compromised',
    icon: IconLock,
  },
];

export function MyFeatures() {
  const theme = useMantineTheme();
  const features = mockdata.map((feature) => (
    <Card key={feature.title} shadow="md" radius="md" className={classes.card} padding="xl">
      <feature.icon size={50} stroke={2} color={theme.colors.blue[6]} />
      <Text fz="lg" fw={500} className={classes.cardTitle} mt="md">
        {feature.title}
      </Text>
      <Text fz="sm" c="dimmed" mt="sm">
        {feature.description}
      </Text>
    </Card>
  ));

  return (
    <Container size="lg" py="xl">
      <Group justify="center">
        <Badge variant="filled" size="xl">
            Socket Only
        </Badge>
      </Group>

      <Title order={2} className={classes.title} ta="center" mt="sm">
        Powered by Python’s built-in socket module
      </Title>

      <SimpleGrid cols={{ base: 1, md: 3 }} spacing="xl" mt={50}>
        {features}
      </SimpleGrid>
    </Container>
  );
}