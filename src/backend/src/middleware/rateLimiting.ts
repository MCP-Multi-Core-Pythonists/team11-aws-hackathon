import { Request, Response, NextFunction } from 'express';

// TODO: Implement proper rate limiting
export const authLimiter = (req: Request, res: Response, next: NextFunction) => {
  // Placeholder implementation - just pass through
  next();
};
