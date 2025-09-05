import { Router } from 'express';

const router = Router();

// TODO: Implement configuration routes
router.get('/', (req, res) => {
  res.json({ message: 'Configuration routes - Coming soon' });
});

export { router as configRoutes };
