import { Sequelize } from 'sequelize';
import { Logger } from '../utils/logger';

export const sequelize = new Sequelize({
  dialect: 'postgres',
  host: process.env.DB_HOST || 'localhost',
  port: parseInt(process.env.DB_PORT || '5432'),
  database: process.env.DB_NAME || 'teamsync',
  username: process.env.DB_USER || 'postgres',
  password: process.env.DB_PASSWORD || 'password',
  logging: process.env.NODE_ENV === 'development' ? (msg) => Logger.debug(msg) : false,
  pool: {
    max: 10,
    min: 0,
    acquire: 30000,
    idle: 10000
  },
  define: {
    timestamps: true,
    underscored: false,
    freezeTableName: true
  }
});

export async function connectDatabase() {
  try {
    await sequelize.authenticate();
    Logger.info('Database connection established successfully');
    
    // 개발 환경에서만 동기화
    if (process.env.NODE_ENV === 'development') {
      await sequelize.sync({ alter: true });
      Logger.info('Database synchronized');
    }
  } catch (error) {
    Logger.error('Unable to connect to database:', error);
    throw error;
  }
}
