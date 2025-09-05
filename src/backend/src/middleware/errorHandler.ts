import { Request, Response, NextFunction } from 'express';
import { Logger } from '../utils/logger';

interface CustomError extends Error {
  statusCode?: number;
  code?: string;
  details?: any;
}

export const errorHandler = (
  error: CustomError,
  req: Request,
  res: Response,
  next: NextFunction
) => {
  let statusCode = error.statusCode || 500;
  let message = error.message || 'Internal Server Error';
  let details = error.details;

  // Sequelize 에러 처리
  if (error.name === 'SequelizeValidationError') {
    statusCode = 400;
    message = 'Validation Error';
    details = error.details || 'Invalid input data';
  } else if (error.name === 'SequelizeUniqueConstraintError') {
    statusCode = 409;
    message = 'Duplicate Entry';
    details = 'Resource already exists';
  } else if (error.name === 'SequelizeForeignKeyConstraintError') {
    statusCode = 400;
    message = 'Invalid Reference';
    details = 'Referenced resource does not exist';
  }

  // JWT 에러 처리
  if (error.name === 'JsonWebTokenError') {
    statusCode = 401;
    message = 'Invalid Token';
    details = 'Authentication token is invalid';
  } else if (error.name === 'TokenExpiredError') {
    statusCode = 401;
    message = 'Token Expired';
    details = 'Authentication token has expired';
  }

  // 로깅
  const logData = {
    error: {
      name: error.name,
      message: error.message,
      stack: error.stack
    },
    request: {
      method: req.method,
      url: req.originalUrl,
      ip: req.ip,
      userAgent: req.get('User-Agent'),
      userId: req.user?.id
    },
    statusCode
  };

  if (statusCode >= 500) {
    Logger.error('Server Error:', logData);
  } else {
    Logger.warn('Client Error:', logData);
  }

  // 응답
  const response: any = {
    error: message,
    statusCode
  };

  if (details) {
    response.details = details;
  }

  // 개발 환경에서는 스택 트레이스 포함
  if (process.env.NODE_ENV === 'development') {
    response.stack = error.stack;
  }

  res.status(statusCode).json(response);
};
