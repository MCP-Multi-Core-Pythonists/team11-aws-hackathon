import { Request, Response, NextFunction } from 'express';

// TODO: Implement proper validation middleware
export const validateRequest = (schema: any) => {
  return (req: Request, res: Response, next: NextFunction) => {
    // Placeholder implementation - just pass through
    next();
  };
};
