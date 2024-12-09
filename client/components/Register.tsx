import { AxiosError } from "axios"
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
import { hasLength, isEmail, useForm } from '@mantine/form';
import { handleRetry, login, register } from '../src/api';
import { useMutation } from '@tanstack/react-query';
import { useRouter } from "next/router";
import { useState } from "react";

export function MyRegister() {
  const router = useRouter();
  const [submitted, setSubmitted] = useState(false);

  const form = useForm({
    mode: 'uncontrolled',
    initialValues: {
      username: '',
      email: '',
      password: '',
    },
    validate: {
        email: isEmail('Invalid email'),
      password: hasLength({ min: 4 }, 'Password must be at least 4 characters long'),
    },
  });


  const registerMutation = useMutation({
    mutationFn: register,
    onSuccess: (data) => {
      console.log("Register successful");
      router.push("/login");
    },
    retry(failureCount, error) {
      return handleRetry(failureCount, error, (failureCount, error) => {
        // bad input
        if (error.status === 400) {
          form.setErrors({ username: 'Bad input, unexpected error' });
          return false;
        }

        // username or email already exists
        if (error.status === 409) {
          const body: any = error.response?.data;
          form.setErrors({ [body?.field || 'username']: body?.error || 'Unknown error' });
          return false;
        }
      });
    },
  });

  return (
    <Container size={420} my={40}>
      <Title ta="center" className={classes.title}>
        Welcome!
      </Title>
      <Text c="dimmed" size="sm" ta="center" mt={5}>
        Already have an account?{' '}
        <Anchor size="sm" component="a" href="/login">
          Login
        </Anchor>
      </Text>

      <Paper withBorder shadow="md" p={30} mt={30} radius="md">
        <form onSubmit={form.onSubmit((props) => {
          registerMutation.mutate(props);
          setSubmitted(true);
        })}>
          <TextInput
            required
            label="Username"
            placeholder="Your Username"
            key={form.key('username')}
            {...form.getInputProps('username')}
          />

          <TextInput
            required
            label="Email"
            placeholder="Your email"
            mt="md"
            key={form.key('email')}
            {...form.getInputProps('email')}
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
            Register
          </Button>
        </form>
      </Paper>
    </Container>
  );
}
