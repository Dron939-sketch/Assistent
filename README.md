# FishFlow — AI-ассистент эксперта

Трёхуровневый AI-сервис для нутрициологов, психологов, тарологов и других экспертов.

- **Start** — бот приводит заявки
- **Pro** — бот + контент + аналитика
- **Expert** — полная система: клиенты, бренд, марафоны

## Быстрый старт

```bash
# 1. Clone repository
git clone https://github.com/your/fishflow.git
cd fishflow

# 2. Copy environment
cp .env.example .env
# Edit .env with your keys

# 3. Start services
make up

# 4. Run migrations
make migrate

# 5. Open browser
# Web: http://localhost:3000
# API: http://localhost:8000/docs
# Admin: http://localhost:3001
