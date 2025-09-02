# CloudBuster

simple, straight forward CloudFlare turnstile defeat mechanism using [Botasaurus](https://github.com/omkarcloud/botasaurus)

# Usage

1. Run the API server:

```
  python server.py
```

2. Then ask it to solve a turnsile captcha:

```
  curl -X POST http://localhost:8000/token \
    -H "Content-Type: application/json"    \
    -d '{"link":"https://wplace.live"}'
```

3. ???
4. Profit!

# Dependencies

- chromedriver package
- pip install -r requirements.txt
