import { Request, Response, NextFunction } from 'express';
import { Logger } from '../utils/logger';

export const requestLogger = (req: Request, res: Response, next: NextFunction) => {
  const startTime = Date.now();
  
  // 응답 완료 시 로깅
  res.on('finish', () => {
    const duration = Date.now() - startTime;
    
    const logData = {
      method: req.method,
      url: req.originalUrl,
      statusCode: res.statusCode,
      duration: `${duration}ms`,
      ip: req.ip,
      userAgent: req.get('User-Agent'),
      userId: req.user?.id,
      contentLength: res.get('Content-Length')
    };

    // 상태 코드에 따른 로그 레벨 결정
    if (res.statusCode >= 500) {
      Logger.error('Request completed with server error:', logData);
    } else if (res.statusCode >= 400) {
      Logger.warn('Request completed with client error:', logData);
    } else {
      Logger.info('Request completed:', logData);
    }
  });

  next();
};
