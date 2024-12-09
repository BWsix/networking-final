import {AxiosError} from "axios"
import {
  Anchor,
  Button,
  Container,
  Group,
  Paper,
  PasswordInput,
  Text,
  TextInput,
  Title,
} from '@mantine/core';
import classes from './Login.module.css';
import { hasLength, useForm } from '@mantine/form';
import { handleRetry, login } from '../src/api';
import { useMutation } from '@tanstack/react-query';
import { useRouter } from "next/router";
import { useState } from "react";

export function MyLogin() {
  const router = useRouter();
  const [submitted, setSubmitted] = useState(false);

  const form = useForm({
    mode: 'uncontrolled',
    initialValues: {
      username: '',
      password: '',
    },
    validate: {
      password: hasLength({ min: 4 }, 'Password must be at least 4 characters long'),
    }
  });

  const loginMutation = useMutation({
    mutationFn: login,
    onSuccess: (data) => {
      localStorage.setItem('token', data.data.jwt);
      router.push("/dashboard");
    },
    retry(failureCount, error) {
      return handleRetry(failureCount, error, (failureCount, error) => {
        // bad input
        if (error.status === 400) {
          form.setErrors({ username: 'Bad input, unexpected error' });
          return false;
        }
        // password incorrect
        if (error.status === 401) {
          form.setErrors({ password: 'Incorrect password' });
          return false;
        }
        // user not found
        if (error.status === 404) {
          form.setErrors({ username: 'User not found' });
          return false;
        }
      });
    },
  });

  return (
    <Container size={420} my={40}>
      <Title ta="center" className={classes.title}>
        Welcome back!
      </Title>
      <Text c="dimmed" size="sm" ta="center" mt={5}>
        Do not have an account yet?{' '}
        <Anchor size="sm" component="a" href="/register">
          Create account
        </Anchor>
      </Text>

      <Paper withBorder shadow="md" p={30} mt={30} radius="md">
        <form onSubmit={form.onSubmit((props) => {
            loginMutation.mutate(props);
            setSubmitted(true);
        })}>
          <TextInput
            required
            label="Username"
            placeholder="Your Username"
            key={form.key('username')}
            {...form.getInputProps('username')}
          />

          <PasswordInput
            required
            label="Password"
            placeholder="Your password"
            mt="md"
            key={form.key('password')}
            {...form.getInputProps('password')}
          />

          <Button fullWidth mt="xl" type="submit" disabled={submitted}>
            Sign in
          </Button>
        </form>
      </Paper>
    </Container>
  );
}
