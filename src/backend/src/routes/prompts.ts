import { Router } from 'express';

const router = Router();

// TODO: Implement prompt routes
router.get('/', (req, res) => {
  res.json({ message: 'Prompt routes - Coming soon' });
});

export { router as promptRoutes };
