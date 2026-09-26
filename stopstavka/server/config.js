// Настройки сервера из переменных окружения. Полный список — в README и .env.example.

function num(value, fallback) {
  const n = Number(value);
  return Number.isFinite(n) && value !== '' && value !== undefined ? n : fallback;
}

export function loadConfig(env = process.env) {
  const production = env.NODE_ENV === 'production';
  const appSecret = env.APP_SECRET || (production ? '' : 'dev-secret-change-me');
  if (!appSecret || appSecret.length < 16) {
    throw new Error('APP_SECRET обязателен (минимум 16 символов): им подписываются коды и токены подписки');
  }
  const aiMock = env.AI_MOCK === '1';
  const apiKey = env.ANTHROPIC_API_KEY || '';
  return {
    production,
    port: num(env.PORT, 8080),
    host: env.HOST || '0.0.0.0',
    dataDir: env.DATA_DIR || './data',
    appSecret,
    adminToken: env.ADMIN_TOKEN || '',
    trustProxy: env.TRUST_PROXY === '1',
    ai: {
      enabled: aiMock || Boolean(apiKey),
      mock: aiMock,
      apiKey,
      model: env.AI_MODEL || 'claude-opus-5',
      effort: env.AI_EFFORT ?? 'low',
      fallbacks: env.AI_FALLBACKS !== '0',
      maxTokens: num(env.AI_MAX_TOKENS, 4000),
      freePerDay: num(env.FREE_AI_PER_DAY, 5),
      premiumPerDay: num(env.PREMIUM_AI_PER_DAY, 200),
    },
    prices: {
      kg: { 1: num(env.PRICE_KG_1, 390), 3: num(env.PRICE_KG_3, 990), 12: num(env.PRICE_KG_12, 2990) },
      kz: { 1: num(env.PRICE_KZ_1, 1990), 3: num(env.PRICE_KZ_3, 4990), 12: num(env.PRICE_KZ_12, 14990) },
    },
    payment: {
      kg: { phone: env.PAY_KG_PHONE || '', contact: env.PAY_KG_CONTACT || '' },
      kz: { phone: env.PAY_KZ_PHONE || '', contact: env.PAY_KZ_CONTACT || '' },
    },
  };
}

// Что можно показать браузеру: без секретов.
export function publicConfig(config) {
  const payment = {};
  for (const [country, p] of Object.entries(config.payment)) {
    payment[country] = p.phone && p.contact ? { phone: p.phone, contact: p.contact } : null;
  }
  return {
    ai: { enabled: config.ai.enabled, freePerDay: config.ai.freePerDay },
    prices: config.prices,
    payment,
  };
}
