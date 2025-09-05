import { Router } from 'express';
import { AuthController } from '../controllers/authController';
import { validateRequest } from '../middleware/validation';
import { authLimiter } from '../middleware/rateLimiting';
import { authenticate } from '../middleware/auth';
import Joi from 'joi';

const router = Router();
const authController = new AuthController();

// 스키마 정의
const deviceCodeSchema = {
  body: Joi.object({
    client_id: Joi.string().valid('vscode-extension').required()
  })
};

const tokenSchema = {
  body: Joi.object({
    grant_type: Joi.string().valid('device_code', 'refresh_token').required(),
    device_code: Joi.string().when('grant_type', {
      is: 'device_code',
      then: Joi.required(),
      otherwise: Joi.forbidden()
    }),
    refresh_token: Joi.string().when('grant_type', {
      is: 'refresh_token',
      then: Joi.required(),
      otherwise: Joi.forbidden()
    })
  })
};

const oauthCallbackSchema = {
  body: Joi.object({
    provider: Joi.string().valid('google', 'github').required(),
    code: Joi.string().required(),
    state: Joi.string().optional()
  })
};

const deviceApprovalSchema = {
  body: Joi.object({
    user_code: Joi.string().required()
  })
};

const revokeTokenSchema = {
  body: Joi.object({
    token: Joi.string().required()
  })
};

// Device Flow 엔드포인트 (VS Code Extension용)
router.post('/device', 
  authLimiter,
  validateRequest(deviceCodeSchema),
  authController.requestDeviceCode.bind(authController)
);

router.post('/token',
  authLimiter,
  validateRequest(tokenSchema),
  authController.handleTokenRequest.bind(authController)
);

// OAuth 콜백 (웹 콘솔용)
router.post('/oauth/callback',
  authLimiter,
  validateRequest(oauthCallbackSchema),
  authController.handleOAuthCallback.bind(authController)
);

// Device 승인 (웹 콘솔에서 호출)
router.post('/device/approve',
  authenticate,
  validateRequest(deviceApprovalSchema),
  authController.approveDevice.bind(authController)
);

// 토큰 갱신
router.post('/refresh',
  authLimiter,
  validateRequest({
    body: Joi.object({
      refresh_token: Joi.string().required()
    })
  }),
  authController.refreshToken.bind(authController)
);

// 토큰 무효화
router.post('/revoke',
  authenticate,
  validateRequest(revokeTokenSchema),
  authController.revokeToken.bind(authController)
);

// 로그아웃 (모든 토큰 무효화)
router.post('/logout',
  authenticate,
  authController.logout.bind(authController)
);

// 현재 사용자 정보
router.get('/me',
  authenticate,
  authController.getCurrentUser.bind(authController)
);

// OAuth 인증 URL 생성
router.get('/oauth/:provider/url',
  validateRequest({
    params: Joi.object({
      provider: Joi.string().valid('google', 'github').required()
    }),
    query: Joi.object({
      redirect_uri: Joi.string().uri().optional(),
      state: Joi.string().optional()
    })
  }),
  authController.getOAuthUrl.bind(authController)
);

export { router as authRoutes };
