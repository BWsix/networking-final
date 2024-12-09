import {
  Button,
  Paper,
  Textarea,
  TextInput,
  Title
} from '@mantine/core';
import { isEmail, useForm } from '@mantine/form';
import { useMutation } from '@tanstack/react-query';
import { useRouter } from "next/router";
import { handleRetry, sendMail } from "../../src/api";
import { useMeQuery } from "../../src/queries";
import classes from '../../components/Login.module.css';
import { useState } from 'react';

export default function NewMessage() {
  const meQuery = useMeQuery();
  const router = useRouter();
  const [submitting, setSubmitting] = useState(false);

  const form = useForm({
    mode: 'uncontrolled',
    initialValues: {
      to: '',
      subject: '',
      body: '',
    },
    validate: {
      to: isEmail('Invalid email'),
    },
  });

  const registerMutation = useMutation({
    mutationFn: sendMail,
    onSuccess: (data) => {
      console.log("Mail Sent");
      router.push("/dashboard/sent");
    },
    retry(failureCount, error) {
      return handleRetry(failureCount, error, (failureCount, error) => {
        // bad input
        if (error.status === 400) {
          form.setErrors({ username: 'Bad input, unexpected error' });
          return false;
        }

        // username or email already exists
        if (error.status === 500) {
          form.setErrors({ to: 'Unknown error' });
          return false;
        }
      });
    },
  });

  return (
    <>
      <Title ta="center" className={classes.title} py="md">
        New Message
      </Title>

      {meQuery.isLoading && <p>Loading...</p>}
      {meQuery.isError && <p>{meQuery.error || "Unknown error"}</p>}
      {meQuery.user && (
        <Paper withBorder shadow="md" p={30} radius="md">
          <form onSubmit={form.onSubmit((props) => {
            setSubmitting(true);
            registerMutation.mutate(props);
          })}>
            <TextInput
              required
              label="From"
              value={meQuery.user?.email || "Loading..."}
              disabled
            />

            <TextInput
              required
              label="To"
              placeholder="recipient@example.com"
              mt="md"
              key={form.key('to')}
              {...form.getInputProps('to')}
            />

            <TextInput
              required
              label="Subject"
              placeholder="Subject"
              mt="md"
              key={form.key('subject')}
              {...form.getInputProps('subject')}
            />

            <Textarea
              label="Body"
              placeholder="Body"
              mt="md"
              autosize
              key={form.key('body')}
              {...form.getInputProps('body')}
            />

            <Button fullWidth mt="xl" type="submit" disabled={submitting}>
              Send
            </Button>
          </form>
        </Paper>
      )}
    </>
  );
}
