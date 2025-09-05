import jwt from 'jsonwebtoken';
import crypto from 'crypto';
import { User } from '../models/User';

interface TokenPayload {
  userId: string;
  email: string;
  name: string;
  iat: number;
  exp: number;
}

export class TokenService {
  private readonly ACCESS_TOKEN_SECRET = process.env.JWT_ACCESS_SECRET || 'default-access-secret';
  private readonly REFRESH_TOKEN_SECRET = process.env.JWT_REFRESH_SECRET || 'default-refresh-secret';
  private readonly ACCESS_TOKEN_EXPIRY = '15m';
  private readonly REFRESH_TOKEN_EXPIRY = '7d';

  async generateTokens(userId: string, email: string, name: string) {
    const accessToken = jwt.sign(
      { userId, email, name },
      this.ACCESS_TOKEN_SECRET,
      { expiresIn: this.ACCESS_TOKEN_EXPIRY }
    );

    const refreshToken = jwt.sign(
      { userId, type: 'refresh' },
      this.REFRESH_TOKEN_SECRET,
      { expiresIn: this.REFRESH_TOKEN_EXPIRY }
    );

    return {
      accessToken,
      refreshToken,
      expiresIn: 15 * 60
    };
  }

  async refreshTokens(refreshToken: string) {
    try {
      const payload = jwt.verify(refreshToken, this.REFRESH_TOKEN_SECRET) as any;
      
      if (payload.type !== 'refresh') {
        throw new Error('Invalid token type');
      }

      const user = await User.findByPk(payload.userId);
      if (!user) {
        throw new Error('User not found');
      }

      return this.generateTokens(user.id, user.email, user.name);
    } catch (error) {
      throw new Error('Invalid refresh token');
    }
  }

  verifyAccessToken(token: string): TokenPayload {
    try {
      return jwt.verify(token, this.ACCESS_TOKEN_SECRET) as TokenPayload;
    } catch (error) {
      throw new Error('Invalid access token');
    }
  }

  async revokeRefreshToken(refreshToken: string) {
    // 간단한 구현: 실제로는 블랙리스트에 추가
    return Promise.resolve();
  }

  async revokeAllUserTokens(userId: string) {
    // 간단한 구현: 실제로는 사용자의 모든 토큰 무효화
    return Promise.resolve();
  }
}
