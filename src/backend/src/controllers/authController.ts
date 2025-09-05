import { Request, Response, NextFunction } from 'express';
import crypto from 'crypto';
import { User } from '../models/User';
import { TokenService } from '../services/tokenService';
import { OAuthService } from '../services/oauthService';
import { redis } from '../config/redis';
import { Logger } from '../utils/logger';

export class AuthController {
  private tokenService = new TokenService();
  private oauthService = new OAuthService();

  async requestDeviceCode(req: Request, res: Response, next: NextFunction) {
    try {
      const { client_id } = req.body;

      const deviceCode = crypto.randomBytes(32).toString('hex');
      const userCode = this.generateUserCode();
      const expiresIn = 600; // 10분

      // Redis에 device code 저장
      await redis.setex(`device_code:${deviceCode}`, expiresIn, JSON.stringify({
        userCode,
        clientId: client_id,
        createdAt: Date.now()
      }));

      Logger.info(`Device code generated: ${userCode}`);

      res.json({
        device_code: deviceCode,
        user_code: userCode,
        verification_uri: `${process.env.FRONTEND_URL}/auth/device`,
        verification_uri_complete: `${process.env.FRONTEND_URL}/auth/device?user_code=${userCode}`,
        expires_in: expiresIn,
        interval: 5
      });
    } catch (error) {
      Logger.error('Device code generation failed:', error);
      next(error);
    }
  }

  async handleTokenRequest(req: Request, res: Response, next: NextFunction) {
    try {
      const { grant_type } = req.body;

      if (grant_type === 'device_code') {
        return this.pollForToken(req, res, next);
      } else if (grant_type === 'refresh_token') {
        return this.refreshToken(req, res, next);
      }

      res.status(400).json({ error: 'unsupported_grant_type' });
    } catch (error) {
      next(error);
    }
  }

  async pollForToken(req: Request, res: Response, next: NextFunction) {
    try {
      const { device_code } = req.body;

      const deviceData = await redis.get(`device_code:${device_code}`);
      if (!deviceData) {
        return res.status(400).json({ 
          error: 'expired_token',
          error_description: 'The device code has expired'
        });
      }

      const { userCode } = JSON.parse(deviceData);
      
      // 사용자 승인 확인
      const approvalData = await redis.get(`device_approval:${userCode}`);
      if (!approvalData) {
        return res.status(400).json({ 
          error: 'authorization_pending',
          error_description: 'User has not yet approved the device'
        });
      }

      const { userId } = JSON.parse(approvalData);
      const user = await User.findByPk(userId);

      if (!user) {
        return res.status(400).json({ 
          error: 'access_denied',
          error_description: 'User not found'
        });
      }

      // 토큰 생성
      const tokens = await this.tokenService.generateTokens(
        user.id,
        user.email,
        user.name
      );

      // 임시 데이터 삭제
      await redis.del(`device_code:${device_code}`);
      await redis.del(`device_approval:${userCode}`);

      // 마지막 로그인 시간 업데이트
      await user.update({ lastLoginAt: new Date() });

      Logger.info(`Device token issued for user: ${user.email}`);

      res.json({
        access_token: tokens.accessToken,
        refresh_token: tokens.refreshToken,
        token_type: 'Bearer',
        expires_in: tokens.expiresIn
      });
    } catch (error) {
      Logger.error('Token polling failed:', error);
      next(error);
    }
  }

  async handleOAuthCallback(req: Request, res: Response, next: NextFunction) {
    try {
      const { provider, code, state } = req.body;

      // OAuth 코드로 사용자 정보 가져오기
      const userInfo = await this.oauthService.exchangeCodeForUser(provider, code);
      
      // 사용자 찾기 또는 생성
      let user = await User.findOne({
        where: {
          provider,
          providerId: userInfo.id
        }
      });

      if (!user) {
        // 이메일로 기존 사용자 확인
        const existingUser = await User.findOne({
          where: { email: userInfo.email }
        });

        if (existingUser) {
          // 기존 사용자에 OAuth 연결
          user = await existingUser.update({
            provider,
            providerId: userInfo.id,
            avatar: userInfo.avatar || existingUser.avatar,
            emailVerified: true
          });
        } else {
          // 새 사용자 생성
          user = await User.create({
            email: userInfo.email,
            name: userInfo.name,
            avatar: userInfo.avatar,
            provider,
            providerId: userInfo.id,
            emailVerified: true
          });
        }
      } else {
        // 기존 OAuth 사용자 정보 업데이트
        await user.update({
          name: userInfo.name,
          avatar: userInfo.avatar || user.avatar,
          lastLoginAt: new Date()
        });
      }

      // 토큰 생성
      const tokens = await this.tokenService.generateTokens(
        user.id,
        user.email,
        user.name
      );

      Logger.info(`OAuth login successful for user: ${user.email}`);

      res.json({
        user: {
          id: user.id,
          email: user.email,
          name: user.name,
          avatar: user.avatar
        },
        tokens: {
          access_token: tokens.accessToken,
          refresh_token: tokens.refreshToken,
          token_type: 'Bearer',
          expires_in: tokens.expiresIn
        }
      });
    } catch (error) {
      Logger.error('OAuth callback failed:', error);
      next(error);
    }
  }

  async approveDevice(req: Request, res: Response, next: NextFunction) {
    try {
      const { user_code } = req.body;
      const userId = req.user!.id;

      // User code 유효성 확인
      const deviceCodeKey = await this.findDeviceCodeByUserCode(user_code);
      if (!deviceCodeKey) {
        return res.status(400).json({ 
          error: 'invalid_user_code',
          error_description: 'The user code is invalid or expired'
        });
      }

      // 승인 정보 저장
      await redis.setex(`device_approval:${user_code}`, 600, JSON.stringify({
        userId,
        approvedAt: Date.now()
      }));

      Logger.info(`Device approved by user: ${req.user!.email}, code: ${user_code}`);

      res.json({ 
        success: true,
        message: 'Device has been approved successfully'
      });
    } catch (error) {
      Logger.error('Device approval failed:', error);
      next(error);
    }
  }

  async refreshToken(req: Request, res: Response, next: NextFunction) {
    try {
      const { refresh_token } = req.body;

      const tokens = await this.tokenService.refreshTokens(refresh_token);

      Logger.info('Token refreshed successfully');

      res.json({
        access_token: tokens.accessToken,
        refresh_token: tokens.refreshToken,
        token_type: 'Bearer',
        expires_in: tokens.expiresIn
      });
    } catch (error) {
      Logger.error('Token refresh failed:', error);
      res.status(401).json({ 
        error: 'invalid_grant',
        error_description: 'Invalid or expired refresh token'
      });
    }
  }

  async revokeToken(req: Request, res: Response, next: NextFunction) {
    try {
      const { token } = req.body;

      await this.tokenService.revokeRefreshToken(token);

      Logger.info(`Token revoked for user: ${req.user!.email}`);

      res.status(204).send();
    } catch (error) {
      Logger.error('Token revocation failed:', error);
      next(error);
    }
  }

  async logout(req: Request, res: Response, next: NextFunction) {
    try {
      const userId = req.user!.id;

      await this.tokenService.revokeAllUserTokens(userId);

      Logger.info(`User logged out: ${req.user!.email}`);

      res.status(204).send();
    } catch (error) {
      Logger.error('Logout failed:', error);
      next(error);
    }
  }

  async getCurrentUser(req: Request, res: Response, next: NextFunction) {
    try {
      const user = req.user!;

      res.json({
        id: user.id,
        email: user.email,
        name: user.name,
        avatar: user.avatar,
        provider: user.provider,
        emailVerified: user.emailVerified,
        createdAt: user.createdAt,
        lastLoginAt: user.lastLoginAt
      });
    } catch (error) {
      next(error);
    }
  }

  async getOAuthUrl(req: Request, res: Response, next: NextFunction) {
    try {
      const { provider } = req.params;
      const { redirect_uri, state } = req.query;

      const authUrl = this.oauthService.getAuthorizationUrl(
        provider as 'google' | 'github',
        redirect_uri as string,
        state as string
      );

      res.json({ auth_url: authUrl });
    } catch (error) {
      Logger.error('OAuth URL generation failed:', error);
      next(error);
    }
  }

  private generateUserCode(): string {
    const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789';
    let result = '';
    for (let i = 0; i < 8; i++) {
      result += chars.charAt(Math.floor(Math.random() * chars.length));
    }
    return result.match(/.{1,4}/g)?.join('-') || result;
  }

  private async findDeviceCodeByUserCode(userCode: string): Promise<string | null> {
    const keys = await redis.keys('device_code:*');
    
    for (const key of keys) {
      const data = await redis.get(key);
      if (data) {
        const { userCode: storedUserCode } = JSON.parse(data);
        if (storedUserCode === userCode) {
          return key;
        }
      }
    }
    
    return null;
  }
}
