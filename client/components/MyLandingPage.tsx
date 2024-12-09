import { Button, Container, Overlay, Text, Title } from '@mantine/core';
import classes from './MyLandingPage.module.css';

import packageJson from "../package.json";

export function MyLandingPage() {
  return (
    <div className={classes.hero}>
      <Overlay
        gradient="linear-gradient(180deg, rgba(0, 0, 0, 0.25) 0%, rgba(0, 0, 0, .65) 40%)"
        opacity={1}
        zIndex={0}
      />
      <Container className={classes.container} size="md">
        <Title className={classes.title} fw="bolder">{packageJson.name}</Title>
        <Text className={classes.description} size="xl" mt="xl">
            {packageJson.description}
        </Text>

        <Button variant="gradient" size="xl" radius="xl" className={classes.control} component='a' href="/dashboard/new-message">
          Get started
        </Button>
      </Container>
    </div>
  );
}