import axios, { AxiosError } from 'axios';
import { RedirectStatusCode } from 'next/dist/client/components/redirect-status-code';

const api = axios.create({
    baseURL: 'http://localhost:6969',
});

api.interceptors.request.use((config) => {
    const getToken = () => localStorage.getItem('token');
    config.headers.Authorization = getToken();
    return config;
});

type RetryFn = (failureCount: number, error: AxiosError) => boolean | undefined;
export function handleRetry(failureCount: number, error: any, retryFn: RetryFn) {
    if (!(error instanceof AxiosError)) return failureCount < 3; // unknown error, retry

    if (error.status === 500) return failureCount < 3; // server error
    if (error.status === 504) return true; // gateway timeout
    if (error.code === 'ERR_NETWORK') return true; // preflight request timeout, retry

    const res = retryFn(failureCount, error);
    if (res !== undefined) return res;

    console.log("Encountered unknown error while logging in", error);
    return failureCount < 3; // unknown error, retry
}

export async function getUsers() {
    console.log(`API - getUsers()...`);
    const res = await api.get('/users');
    console.log(`API - getUsers() = ${res}`);
    return res;
}

export async function getMe() {
    console.log(`API - getMe()...`);
    const res = await api.get('/me');
    console.log(`API - getMe() = ${res}`);
    return res;
}

interface RegisterProps {
    username: string;
    email: string;
    password: string;
}
export async function register(props: RegisterProps) {
    console.log(`API - register(${props})...`);
    const res = await api.post('/user', props);
    console.log(`API - register(${props}) = ${res}`);
    return res;
}

interface LoginProps {
    username: string;
    password: string;
}
export async function login(props: LoginProps) {
    console.log(`API - login(${props})...`);
    const res = await api.post('/login', props);
    console.log(`API - login(${props}) = ${res}`);
    return res;
}

export function logout() {
    localStorage.removeItem('token');
    window.location.reload();
}
