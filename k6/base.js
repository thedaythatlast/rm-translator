import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  vus: 1,
  duration: '30s',
};

const TEXTS = [
  'Hello, how are you?',
  'What is your name?',
  'I am fine, thank you.',
];

export default function () {
  const payload = JSON.stringify({
    text: TEXTS[Math.floor(Math.random() * TEXTS.length)],
  });

  const res = http.post('http://localhost:8000/api/translate/', payload, {
    headers: { 'Content-Type': 'application/json' },
  });

  check(res, {
    'status is 200':              (r) => r.status === 200,
    'response has translation':   (r) => JSON.parse(r.body).translation !== undefined,
    'translation is not empty':   (r) => JSON.parse(r.body).translation.length > 0,
  });

  sleep(1);
}