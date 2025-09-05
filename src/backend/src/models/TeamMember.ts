import { DataTypes, Model, Optional } from 'sequelize';
import { sequelize } from '../config/database';

interface TeamMemberAttributes {
  id: string;
  teamId: string;
  userId: string;
  role: 'owner' | 'admin' | 'member';
  joinedAt: Date;
  invitedBy?: string;
}

interface TeamMemberCreationAttributes extends Optional<TeamMemberAttributes, 'id' | 'joinedAt' | 'invitedBy'> {}

export class TeamMember extends Model<TeamMemberAttributes, TeamMemberCreationAttributes> implements TeamMemberAttributes {
  public id!: string;
  public teamId!: string;
  public userId!: string;
  public role!: 'owner' | 'admin' | 'member';
  public joinedAt!: Date;
  public invitedBy?: string;

  // 연관 관계 메서드들
  public getUser!: () => Promise<any>;
  public getTeam!: () => Promise<any>;
}

TeamMember.init({
  id: {
    type: DataTypes.UUID,
    defaultValue: DataTypes.UUIDV4,
    primaryKey: true
  },
  teamId: {
    type: DataTypes.UUID,
    allowNull: false,
    references: {
      model: 'teams',
      key: 'id'
    }
  },
  userId: {
    type: DataTypes.UUID,
    allowNull: false,
    references: {
      model: 'users',
      key: 'id'
    }
  },
  role: {
    type: DataTypes.ENUM('owner', 'admin', 'member'),
    allowNull: false,
    defaultValue: 'member'
  },
  joinedAt: {
    type: DataTypes.DATE,
    defaultValue: DataTypes.NOW
  },
  invitedBy: {
    type: DataTypes.UUID,
    allowNull: true,
    references: {
      model: 'users',
      key: 'id'
    }
  }
}, {
  sequelize,
  modelName: 'TeamMember',
  tableName: 'team_members',
  timestamps: false,
  indexes: [
    {
      unique: true,
      fields: ['teamId', 'userId']
    },
    {
      fields: ['teamId']
    },
    {
      fields: ['userId']
    }
  ]
});

export default TeamMember;
