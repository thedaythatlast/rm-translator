import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  stages: [
    { duration: '10s', target: 1  },  // ramp to capacity
    { duration: '10s',  target: 3  },  // hold at capacity
    { duration: '5s', target: 0  },  // ramp down
  ],
  thresholds: {
    http_req_duration: ['p(95)<2000'],
    http_req_failed:   ['rate<0.05'],
  },
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