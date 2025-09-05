import { Request, Response, NextFunction } from 'express';
import { Configuration } from '../models/Configuration';
import { TeamMember } from '../models/TeamMember';
import { Logger } from '../utils/logger';

export class ConfigurationController {
  async syncConfiguration(req: Request, res: Response, next: NextFunction) {
    try {
      const { teamId, configuration } = req.body;
      const userId = req.user!.id;

      // 팀 멤버 권한 확인
      const teamMember = await TeamMember.findOne({
        where: { teamId, userId }
      });

      if (!teamMember) {
        return res.status(403).json({ 
          error: 'Not a team member' 
        });
      }

      // 현재 활성 설정 조회
      const currentConfig = await Configuration.findOne({
        where: { teamId, isActive: true },
        order: [['version', 'DESC']]
      });

      let newVersion = 1;
      if (currentConfig) {
        newVersion = currentConfig.version + 1;
        // 기존 설정 비활성화
        await currentConfig.update({ isActive: false });
      }

      // 새 설정 생성
      const newConfig = await Configuration.create({
        teamId,
        name: `Auto Sync v${newVersion}`,
        description: `Automatically synced configuration`,
        editorType: 'vscode',
        settings: configuration,
        version: newVersion,
        isActive: true,
        createdBy: userId
      });

      Logger.info(`Configuration synced for team ${teamId} by ${req.user!.email}`);

      res.json({
        success: true,
        configuration: newConfig,
        message: 'Configuration synchronized successfully'
      });
    } catch (error) {
      Logger.error('Configuration sync failed:', error);
      next(error);
    }
  }

  async getLatestConfiguration(req: Request, res: Response, next: NextFunction) {
    try {
      const { teamId } = req.params;
      const userId = req.user!.id;

      // 팀 멤버 권한 확인
      const teamMember = await TeamMember.findOne({
        where: { teamId, userId }
      });

      if (!teamMember) {
        return res.status(403).json({ 
          error: 'Not a team member' 
        });
      }

      const configuration = await Configuration.findOne({
        where: { teamId, isActive: true },
        order: [['version', 'DESC']]
      });

      if (!configuration) {
        return res.status(404).json({ 
          error: 'No configuration found for this team' 
        });
      }

      res.json({ configuration });
    } catch (error) {
      Logger.error('Failed to get latest configuration:', error);
      next(error);
    }
  }

  async getTeamConfigurations(req: Request, res: Response, next: NextFunction) {
    try {
      const { teamId } = req.params;
      const userId = req.user!.id;

      // 팀 멤버 권한 확인
      const teamMember = await TeamMember.findOne({
        where: { teamId, userId }
      });

      if (!teamMember) {
        return res.status(403).json({ 
          error: 'Not a team member' 
        });
      }

      const configurations = await Configuration.findAll({
        where: { teamId },
        order: [['version', 'DESC']],
        limit: 10 // 최근 10개만
      });

      res.json({ configurations });
    } catch (error) {
      Logger.error('Failed to get team configurations:', error);
      next(error);
    }
  }

  async createConfiguration(req: Request, res: Response, next: NextFunction) {
    try {
      const { teamId, name, description, editorType, settings } = req.body;
      const userId = req.user!.id;

      // 팀 멤버 권한 확인
      const teamMember = await TeamMember.findOne({
        where: { teamId, userId }
      });

      if (!teamMember) {
        return res.status(403).json({ 
          error: 'Not a team member' 
        });
      }

      // 버전 계산
      const latestConfig = await Configuration.findOne({
        where: { teamId },
        order: [['version', 'DESC']]
      });

      const version = latestConfig ? latestConfig.version + 1 : 1;

      const configuration = await Configuration.create({
        teamId,
        name,
        description,
        editorType: editorType || 'vscode',
        settings,
        version,
        isActive: true,
        createdBy: userId
      });

      // 기존 활성 설정 비활성화
      if (latestConfig && latestConfig.isActive) {
        await latestConfig.update({ isActive: false });
      }

      Logger.info(`Configuration created: ${name} for team ${teamId}`);

      res.status(201).json({ configuration });
    } catch (error) {
      Logger.error('Failed to create configuration:', error);
      next(error);
    }
  }

  async getConfiguration(req: Request, res: Response, next: NextFunction) {
    try {
      const { id } = req.params;
      const userId = req.user!.id;

      const configuration = await Configuration.findByPk(id);
      if (!configuration) {
        return res.status(404).json({ 
          error: 'Configuration not found' 
        });
      }

      // 팀 멤버 권한 확인
      const teamMember = await TeamMember.findOne({
        where: { teamId: configuration.teamId, userId }
      });

      if (!teamMember) {
        return res.status(403).json({ 
          error: 'Access denied' 
        });
      }

      res.json({ configuration });
    } catch (error) {
      Logger.error('Failed to get configuration:', error);
      next(error);
    }
  }
}
