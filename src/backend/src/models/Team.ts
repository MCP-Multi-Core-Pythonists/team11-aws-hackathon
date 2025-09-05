import { DataTypes, Model, Optional } from 'sequelize';
import { sequelize } from '../config/database';

interface TeamSettings {
  visibility: 'public' | 'private';
  allowMemberInvite: boolean;
  requireApproval: boolean;
  maxMembers?: number;
}

interface TeamAttributes {
  id: string;
  name: string;
  description?: string;
  ownerId: string;
  settings: TeamSettings;
  createdAt: Date;
  updatedAt: Date;
}

interface TeamCreationAttributes extends Optional<TeamAttributes, 'id' | 'createdAt' | 'updatedAt' | 'description' | 'settings'> {}

export class Team extends Model<TeamAttributes, TeamCreationAttributes> implements TeamAttributes {
  public id!: string;
  public name!: string;
  public description?: string;
  public ownerId!: string;
  public settings!: TeamSettings;
  public createdAt!: Date;
  public updatedAt!: Date;

  // 연관 관계 메서드들
  public getOwner!: () => Promise<any>;
  public getMembers!: () => Promise<any[]>;
  public getConfigurations!: () => Promise<any[]>;
  public getPrompts!: () => Promise<any[]>;
}

Team.init({
  id: {
    type: DataTypes.UUID,
    defaultValue: DataTypes.UUIDV4,
    primaryKey: true
  },
  name: {
    type: DataTypes.STRING(255),
    allowNull: false,
    validate: {
      len: [2, 100],
      notEmpty: true
    }
  },
  description: {
    type: DataTypes.TEXT,
    allowNull: true,
    validate: {
      len: [0, 1000]
    }
  },
  ownerId: {
    type: DataTypes.UUID,
    allowNull: false,
    references: {
      model: 'users',
      key: 'id'
    }
  },
  settings: {
    type: DataTypes.JSONB,
    allowNull: false,
    defaultValue: {
      visibility: 'private',
      allowMemberInvite: false,
      requireApproval: true
    },
    validate: {
      isValidSettings(value: TeamSettings) {
        if (!value || typeof value !== 'object') {
          throw new Error('Settings must be a valid object');
        }
        
        const validVisibility = ['public', 'private'];
        if (!validVisibility.includes(value.visibility)) {
          throw new Error('Invalid visibility setting');
        }
        
        if (typeof value.allowMemberInvite !== 'boolean') {
          throw new Error('allowMemberInvite must be a boolean');
        }
        
        if (typeof value.requireApproval !== 'boolean') {
          throw new Error('requireApproval must be a boolean');
        }
        
        if (value.maxMembers && (typeof value.maxMembers !== 'number' || value.maxMembers < 1)) {
          throw new Error('maxMembers must be a positive number');
        }
      }
    }
  }
}, {
  sequelize,
  modelName: 'Team',
  tableName: 'teams',
  timestamps: true,
  indexes: [
    {
      fields: ['ownerId']
    },
    {
      fields: ['name']
    },
    {
      fields: ['createdAt']
    }
  ],
  hooks: {
    beforeCreate: (team: Team) => {
      // 팀 이름 트림
      team.name = team.name.trim();
    },
    beforeUpdate: (team: Team) => {
      if (team.changed('name')) {
        team.name = team.name.trim();
      }
    }
  }
});

export default Team;
