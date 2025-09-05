import { Router } from 'express';
import { ConfigurationController } from '../controllers/configurationController';
import { authenticate } from '../middleware/auth';
import { validateRequest } from '../middleware/validation';
import { userLimiter } from '../middleware/rateLimiting';
import Joi from 'joi';

const router = Router();
const configController = new ConfigurationController();

router.use(authenticate);
router.use(userLimiter);

const syncConfigSchema = {
  body: Joi.object({
    teamId: Joi.string().uuid().required(),
    configuration: Joi.object({
      settings: Joi.object().optional(),
      keybindings: Joi.array().optional(),
      extensions: Joi.array().optional(),
      snippets: Joi.object().optional()
    }).required()
  })
};

const createConfigSchema = {
  body: Joi.object({
    teamId: Joi.string().uuid().required(),
    name: Joi.string().min(1).max(100).required(),
    description: Joi.string().max(500).optional(),
    editorType: Joi.string().valid('vscode', 'cursor').default('vscode'),
    settings: Joi.object().required()
  })
};

// 설정 동기화 (VS Code Extension용)
router.post('/sync',
  validateRequest(syncConfigSchema),
  configController.syncConfiguration.bind(configController)
);

// 팀의 최신 설정 가져오기
router.get('/teams/:teamId/latest',
  validateRequest({
    params: Joi.object({
      teamId: Joi.string().uuid().required()
    })
  }),
  configController.getLatestConfiguration.bind(configController)
);

// 팀의 설정 목록
router.get('/teams/:teamId',
  validateRequest({
    params: Joi.object({
      teamId: Joi.string().uuid().required()
    })
  }),
  configController.getTeamConfigurations.bind(configController)
);

// 설정 생성
router.post('/',
  validateRequest(createConfigSchema),
  configController.createConfiguration.bind(configController)
);

// 설정 상세 조회
router.get('/:id',
  validateRequest({
    params: Joi.object({
      id: Joi.string().uuid().required()
    })
  }),
  configController.getConfiguration.bind(configController)
);

export { router as configRoutes };
