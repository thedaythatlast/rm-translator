A Django REST API that translates English text to Vietnamese, with Redis-backed rate limiting.

Translation is powered by [ArgosTranslate](https://github.com/argosopentech/argos-translate) (local, no external API calls).
Rate limiting uses an algorithm implemented in Redis via Lua scripting.
> Note: The Redis integration was vibe-coded with AI assistance. 

## How it works

User sends the English that needs to be translated to the backend and receive the translation in Vietnamese. If the number of requests exceeds the allowed capacity (3 users), the request will be denied.

## Setup

### Prerequisites
- Python 3.12+
- A Redis instance ([Redis Cloud free tier](https://redis.io/try-free/))

### Steps

1. Clone the repo
   ```bash
   git clone <repo-url>
   cd rmt
   ```

2. Install dependencies
   ```bash
   pip install -r dependencies.txt
   ```

3. Install the translation language pack (run once)
   ```bash
   python install_language_pair.py
   ```

4. Create a `.env` file in the project root
   ```
   REDIS_URL=redis://default:<password>@<host>:<port>
   ```

5. Apply migrations
   ```bash
   python manage.py migrate
   ```

6. Run the server
   ```bash
   python manage.py runserver
   ```

## Usage

### Translate text

```bash
curl -X POST http://127.0.0.1:8000/api/translate/ -H "Content-Type: application/json" -d "{\"text\": \"Hello, how are you?\"}"
```

Response:
```json
{"translation":"Xin chào, anh khỏe không?"}
```

### Test rate limiting (PowerShell)

```powershell
1..5 | ForEach-Object {
    Start-Job { Invoke-RestMethod -Method POST -Uri http://127.0.0.1:8000/api/translate/ -ContentType "application/json" -Body '{"text": "hello"}' }
} | Receive-Job -Wait
```

Requests 1–3 return translations. Requests 4–5 return `429 Too Many Requests`.

## K6 Load testing

This project includes k6 load tests in the `/k6` directory. Make sure to install [k6](https://grafana.com/docs/k6/latest/set-up/install-k6/) if you want to run the test scripts

**Baseline** — tests single-user load:
```bash
k6 run k6/baseline.js
```

**Concurrent** — tests with 3 simultaneous users:
```bash
k6 run k6/concurrent.js
```

### Results

| Test | VUs | Success Rate | p95 Latency | Result |
|---|---|---|---|---|
| Baseline | 1 | 100% | 97ms | ✅ Pass |
| Concurrent | 3 | ~14% | 91ms | ❌ Fail |

## Credits

- Translation: [ArgosTranslate](https://github.com/argosopentech/argos-translate)
