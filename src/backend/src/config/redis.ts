import { createClient } from 'redis';

// TODO: Implement proper Redis configuration
export const redis = createClient({
  url: process.env.REDIS_URL || 'redis://localhost:6379'
});

export async function connectRedis() {
  try {
    await redis.connect();
    console.log('Redis connection established successfully.');
  } catch (error) {
    console.error('Unable to connect to Redis:', error);
    throw error;
  }
}
