import dotenv from 'dotenv';
import { app } from './app';
import { Logger } from './utils/logger';
import { connectDatabase } from './config/database';
import { connectRedis } from './config/redis';

// 모델 연관관계 설정을 위한 import
import './models';

// 환경 변수 로드
dotenv.config();

const PORT = process.env.PORT || 3001;

async function startServer() {
    try {
        // 데이터베이스 연결
        await connectDatabase();
        Logger.info('Database connected successfully');

        // Redis 연결
        await connectRedis();
        Logger.info('Redis connected successfully');

        // 서버 시작
        const server = app.listen(PORT, () => {
            Logger.info(`Server is running on port ${PORT}`);
            Logger.info(`Environment: ${process.env.NODE_ENV || 'development'}`);
        });

        // Graceful shutdown
        const gracefulShutdown = (signal: string) => {
            Logger.info(`${signal} received, shutting down gracefully`);
            server.close(() => {
                Logger.info('HTTP server closed');
                process.exit(0);
            });
        };

        process.on('SIGTERM', () => gracefulShutdown('SIGTERM'));
        process.on('SIGINT', () => gracefulShutdown('SIGINT'));

    } catch (error) {
        Logger.error('Failed to start server:', error);
        process.exit(1);
    }
}

startServer();
