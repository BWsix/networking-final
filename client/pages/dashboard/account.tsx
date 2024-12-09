import { Box, Text, Title } from "@mantine/core";
import classes from '../../components/Login.module.css';
import { logout } from "../../src/api";
import { useMeQuery } from "../../src/queries";

export default function IndexPage() {
  const meQuery = useMeQuery();

  return (
    <>
      <Title ta="center" className={classes.title} py="md">
        Account
      </Title>

      {meQuery.isLoading && <p>Loading...</p>}
      {meQuery.isError && <p>{meQuery.error || "Unknown error"}</p>}
      {meQuery.user && (
        <Box>
          <Title order={4}>Welcome, {meQuery.user?.username}</Title>
          <br />
          <Text href="#" onClick={logout} component="a" ta="end">Logout</Text>
        </Box>
      )}
    </>
  );
}
