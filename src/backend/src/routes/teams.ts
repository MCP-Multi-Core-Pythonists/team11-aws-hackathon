import { Router } from 'express';
import { TeamController } from '../controllers/teamController';
import { authenticate } from '../middleware/auth';
import { validateRequest } from '../middleware/validation';
import { userLimiter } from '../middleware/rateLimiting';
import Joi from 'joi';

const router = Router();
const teamController = new TeamController();

// 모든 팀 라우트에 인증 필요
router.use(authenticate);
router.use(userLimiter);

// 스키마 정의
const createTeamSchema = {
  body: Joi.object({
    name: Joi.string().min(2).max(100).required(),
    description: Joi.string().max(500).optional()
  })
};

const updateTeamSchema = {
  params: Joi.object({
    id: Joi.string().uuid().required()
  }),
  body: Joi.object({
    name: Joi.string().min(2).max(100).optional(),
    description: Joi.string().max(500).optional()
  })
};

const inviteMemberSchema = {
  params: Joi.object({
    id: Joi.string().uuid().required()
  }),
  body: Joi.object({
    email: Joi.string().email().required(),
    role: Joi.string().valid('admin', 'member').default('member')
  })
};

// 팀 목록 조회
router.get('/', teamController.getTeams.bind(teamController));

// 팀 생성
router.post('/', 
  validateRequest(createTeamSchema),
  teamController.createTeam.bind(teamController)
);

// 팀 상세 조회
router.get('/:id',
  validateRequest({
    params: Joi.object({
      id: Joi.string().uuid().required()
    })
  }),
  teamController.getTeam.bind(teamController)
);

// 팀 수정
router.put('/:id',
  validateRequest(updateTeamSchema),
  teamController.updateTeam.bind(teamController)
);

// 팀 삭제
router.delete('/:id',
  validateRequest({
    params: Joi.object({
      id: Joi.string().uuid().required()
    })
  }),
  teamController.deleteTeam.bind(teamController)
);

// 멤버 초대
router.post('/:id/invite',
  validateRequest(inviteMemberSchema),
  teamController.inviteMember.bind(teamController)
);

// 팀 멤버 목록
router.get('/:id/members',
  validateRequest({
    params: Joi.object({
      id: Joi.string().uuid().required()
    })
  }),
  teamController.getTeamMembers.bind(teamController)
);

export { router as teamRoutes };
