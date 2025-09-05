import { Request, Response, NextFunction } from 'express';
import { Team } from '../models/Team';
import { TeamMember } from '../models/TeamMember';
import { User } from '../models/User';
import { Logger } from '../utils/logger';

export class TeamController {
  async getTeams(req: Request, res: Response, next: NextFunction) {
    try {
      const userId = req.user!.id;

      const teams = await Team.findAll({
        include: [
          {
            model: TeamMember,
            where: { userId },
            include: [
              {
                model: User,
                attributes: ['id', 'name', 'email', 'avatar']
              }
            ]
          }
        ]
      });

      res.json(teams);
    } catch (error) {
      Logger.error('Failed to get teams:', error);
      next(error);
    }
  }

  async createTeam(req: Request, res: Response, next: NextFunction) {
    try {
      const { name, description } = req.body;
      const userId = req.user!.id;

      const team = await Team.create({
        name,
        description,
        ownerId: userId,
        settings: {
          visibility: 'private',
          allowMemberInvite: false,
          requireApproval: true
        }
      });

      // 생성자를 오너로 추가
      await TeamMember.create({
        teamId: team.id,
        userId,
        role: 'owner'
      });

      Logger.info(`Team created: ${team.name} by ${req.user!.email}`);

      res.status(201).json(team);
    } catch (error) {
      Logger.error('Failed to create team:', error);
      next(error);
    }
  }

  async getTeam(req: Request, res: Response, next: NextFunction) {
    try {
      const { id } = req.params;
      const userId = req.user!.id;

      const team = await Team.findOne({
        where: { id },
        include: [
          {
            model: TeamMember,
            where: { userId }
          }
        ]
      });

      if (!team) {
        return res.status(404).json({ 
          error: 'Team not found or access denied' 
        });
      }

      res.json(team);
    } catch (error) {
      Logger.error('Failed to get team:', error);
      next(error);
    }
  }

  async updateTeam(req: Request, res: Response, next: NextFunction) {
    try {
      const { id } = req.params;
      const { name, description } = req.body;
      const userId = req.user!.id;

      // 권한 확인 (오너 또는 관리자)
      const teamMember = await TeamMember.findOne({
        where: { teamId: id, userId }
      });

      if (!teamMember || !['owner', 'admin'].includes(teamMember.role)) {
        return res.status(403).json({ 
          error: 'Insufficient permissions' 
        });
      }

      const team = await Team.findByPk(id);
      if (!team) {
        return res.status(404).json({ error: 'Team not found' });
      }

      await team.update({ name, description });

      Logger.info(`Team updated: ${team.name} by ${req.user!.email}`);

      res.json(team);
    } catch (error) {
      Logger.error('Failed to update team:', error);
      next(error);
    }
  }

  async deleteTeam(req: Request, res: Response, next: NextFunction) {
    try {
      const { id } = req.params;
      const userId = req.user!.id;

      const team = await Team.findOne({
        where: { id, ownerId: userId }
      });

      if (!team) {
        return res.status(404).json({ 
          error: 'Team not found or you are not the owner' 
        });
      }

      await team.destroy();

      Logger.info(`Team deleted: ${team.name} by ${req.user!.email}`);

      res.status(204).send();
    } catch (error) {
      Logger.error('Failed to delete team:', error);
      next(error);
    }
  }

  async inviteMember(req: Request, res: Response, next: NextFunction) {
    try {
      const { id } = req.params;
      const { email, role } = req.body;
      const userId = req.user!.id;

      // 권한 확인
      const teamMember = await TeamMember.findOne({
        where: { teamId: id, userId }
      });

      if (!teamMember || !['owner', 'admin'].includes(teamMember.role)) {
        return res.status(403).json({ 
          error: 'Insufficient permissions to invite members' 
        });
      }

      // 초대할 사용자 찾기
      const invitedUser = await User.findOne({ where: { email } });
      if (!invitedUser) {
        return res.status(404).json({ 
          error: 'User not found' 
        });
      }

      // 이미 멤버인지 확인
      const existingMember = await TeamMember.findOne({
        where: { teamId: id, userId: invitedUser.id }
      });

      if (existingMember) {
        return res.status(409).json({ 
          error: 'User is already a team member' 
        });
      }

      // 멤버 추가
      const newMember = await TeamMember.create({
        teamId: id,
        userId: invitedUser.id,
        role: role || 'member',
        invitedBy: userId
      });

      Logger.info(`User invited to team: ${email} by ${req.user!.email}`);

      res.status(201).json({
        message: 'Member invited successfully',
        member: newMember
      });
    } catch (error) {
      Logger.error('Failed to invite member:', error);
      next(error);
    }
  }

  async getTeamMembers(req: Request, res: Response, next: NextFunction) {
    try {
      const { id } = req.params;
      const userId = req.user!.id;

      // 팀 멤버인지 확인
      const teamMember = await TeamMember.findOne({
        where: { teamId: id, userId }
      });

      if (!teamMember) {
        return res.status(403).json({ 
          error: 'Access denied' 
        });
      }

      const members = await TeamMember.findAll({
        where: { teamId: id },
        include: [
          {
            model: User,
            attributes: ['id', 'name', 'email', 'avatar']
          }
        ]
      });

      res.json(members);
    } catch (error) {
      Logger.error('Failed to get team members:', error);
      next(error);
    }
  }
}
