import { useQuery } from "@tanstack/react-query";
import { useRouter } from "next/router";
import { handleRetry, listMails } from "../../src/api";
import { useMeQuery, User } from "../../src/queries";
import { Card, Title, Text, Table, Divider, Code, Box } from "@mantine/core";
import classes from '../../components/Login.module.css';

interface Mail {
  id: number;
  to: string;
  subject: string;
  body: string;
}

interface MailCardProps {
  user: User;
  mail: Mail;
}
function MailCard({ user, mail }: MailCardProps) {
  return (
    <Card mb="md" shadow="sm" withBorder>
      <Table withRowBorders={false}>
        <Table.Tbody>
          <Table.Tr>
            <Table.Td>From</Table.Td>
            <Table.Td>{user.email}</Table.Td>
          </Table.Tr>
          <Table.Tr>
            <Table.Td>To</Table.Td>
            <Table.Td>{user.email}</Table.Td>
          </Table.Tr>
          <Table.Tr>
            <Table.Td>Subject</Table.Td>
            <Table.Td>{mail.subject}</Table.Td>
          </Table.Tr>
        </Table.Tbody>
      </Table>

      <Divider />

      <Box m="sm">
        {mail.body.split("\n").map((line, i) => (
          line.length ? <Text key={i}>{line}</Text> : <br key={i} />
        ))}
      </Box>
    </Card>
  );
}

export default function MailsPage() {
  const meQuery = useMeQuery();
  const router = useRouter();

  const query = useQuery({
    queryKey: ['listMails'],
    queryFn: listMails,
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

  return (
    <>
      <Title ta="center" className={classes.title} py="md">
        Sent
      </Title>

      {query.isLoading && <p>Loading...</p>}
      {query.isError && <p>{query.error?.message || "Unknown error"}</p>}
      {query.isSuccess && query.data?.data.length === 0 && "No messages found."}
      {query.isSuccess && (
        ((query.data?.data || []) as Mail[]).map((mail) => <MailCard key={mail.id} mail={mail} user={meQuery.user} />)
      )}
    </>
  );
}
