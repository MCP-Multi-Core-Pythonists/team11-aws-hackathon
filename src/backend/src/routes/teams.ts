import { Router } from 'express';

const router = Router();

// TODO: Implement team routes
router.get('/', (req, res) => {
  res.json({ message: 'Teams routes - Coming soon' });
});

export { router as teamRoutes };
