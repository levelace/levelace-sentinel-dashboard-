import axios from 'axios';

const client = axios.create({
  baseURL: 'https://security.ilevelace.com/api',
  timeout: 5000
});

export default client;
