import dotenv from 'dotenv';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Load environment variables
dotenv.config({ path: path.join(__dirname, '../../.env') });

export default {
  // Environment
  env: process.env.NODE_ENV || 'development',
  port: parseInt(process.env.PORT, 10) || 3000,
  
  // Twitter API
  twitter: {
    apiKey: process.env.TWITTER_API_KEY,
    apiSecret: process.env.TWITTER_API_SECRET,
    accessToken: process.env.TWITTER_ACCESS_TOKEN,
    accessSecret: process.env.TWITTER_ACCESS_SECRET,
    bearerToken: process.env.TWITTER_BEARER_TOKEN,
  },
  
  // Telegram Bot
  telegram: {
    botToken: process.env.TELEGRAM_BOT_TOKEN,
    channelId: process.env.TELEGRAM_CHANNEL_ID,
  },
  
  // Database
  database: {
    url: process.env.DATABASE_URL,
    host: process.env.DB_HOST || 'localhost',
    port: parseInt(process.env.DB_PORT, 10) || 5432,
    name: process.env.DB_NAME || 'twitter_telegram',
    user: process.env.DB_USER || 'postgres',
    password: process.env.DB_PASSWORD,
  },
  
  // Bot Configuration
  bot: {
    pollInterval: parseInt(process.env.POLL_INTERVAL, 10) || 60000,
    maxTweetAge: parseInt(process.env.MAX_TWEET_AGE, 10) || 3600000,
    enableMedia: process.env.ENABLE_MEDIA === 'true',
    enableThreads: process.env.ENABLE_THREADS === 'true',
    enableMetrics: process.env.ENABLE_METRICS === 'true',
  },
  
  // Logging
  logging: {
    level: process.env.LOG_LEVEL || 'info',
    dir: path.join(__dirname, '../../logs'),
  },
  
  // Optional Services
  redis: {
    url: process.env.REDIS_URL,
  },
  
  sentry: {
    dsn: process.env.SENTRY_DSN,
  },
};