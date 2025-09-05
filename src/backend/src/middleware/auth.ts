import { Request, Response, NextFunction } from 'express';
import { TokenService } from '../services/tokenService';
import { User } from '../models/User';
import { Logger } from '../utils/logger';

const tokenService = new TokenService();

export const authenticate = async (req: Request, res: Response, next: NextFunction) => {
  try {
    const authHeader = req.headers.authorization;
    
    if (!authHeader || !authHeader.startsWith('Bearer ')) {
      return res.status(401).json({ 
        error: 'Authentication required',
        message: 'Please provide a valid access token'
      });
    }

    const token = authHeader.substring(7); // Remove 'Bearer ' prefix
    
    const payload = tokenService.verifyAccessToken(token);
    const user = await User.findByPk(payload.userId);

    if (!user) {
      return res.status(401).json({ 
        error: 'Invalid token',
        message: 'User not found'
      });
    }

    req.user = user;
    next();
  } catch (error) {
    Logger.warn('Authentication failed:', { error: error.message, ip: req.ip });
    res.status(401).json({ 
      error: 'Invalid token',
      message: 'Authentication failed'
    });
  }
};
