import rateLimit from 'express-rate-limit';

// 일반 API 제한
export const apiLimiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15분
  max: 100, // IP당 최대 100 요청
  message: {
    error: 'Too many requests from this IP, please try again later.'
  },
  standardHeaders: true,
  legacyHeaders: false,
});

// 인증 API 제한 (더 엄격)
export const authLimiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15분
  max: 10, // IP당 최대 10 요청
  message: {
    error: 'Too many authentication attempts, please try again later.'
  },
  standardHeaders: true,
  legacyHeaders: false,
});

// 사용자별 제한
export const userLimiter = rateLimit({
  windowMs: 60 * 1000, // 1분
  max: 30, // 사용자당 최대 30 요청
  keyGenerator: (req) => req.user?.id || req.ip,
  message: {
    error: 'Too many requests from this user, please try again later.'
  }
});
