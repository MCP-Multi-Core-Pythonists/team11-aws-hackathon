import { createClient } from 'redis';
import { Logger } from '../utils/logger';

export const redis = createClient({
  url: process.env.REDIS_URL || 'redis://localhost:6379'
});

redis.on('error', (err) => {
  Logger.error('Redis Client Error:', err);
});

redis.on('connect', () => {
  Logger.info('Redis client connected');
});

redis.on('ready', () => {
  Logger.info('Redis client ready');
});

export async function connectRedis() {
  try {
    await redis.connect();
    Logger.info('Redis connection established successfully');
  } catch (error) {
    Logger.error('Unable to connect to Redis:', error);
    throw error;
  }
}
