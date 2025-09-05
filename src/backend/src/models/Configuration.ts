import { DataTypes, Model, Optional } from 'sequelize';
import { sequelize } from '../config/database';

interface ConfigurationAttributes {
  id: string;
  teamId: string;
  name: string;
  description?: string;
  editorType: 'vscode' | 'cursor';
  settings: any;
  version: number;
  isActive: boolean;
  createdBy: string;
  createdAt: Date;
  updatedAt: Date;
}

interface ConfigurationCreationAttributes extends Optional<ConfigurationAttributes, 'id' | 'createdAt' | 'updatedAt' | 'description' | 'version' | 'isActive'> {}

export class Configuration extends Model<ConfigurationAttributes, ConfigurationCreationAttributes> implements ConfigurationAttributes {
  public id!: string;
  public teamId!: string;
  public name!: string;
  public description?: string;
  public editorType!: 'vscode' | 'cursor';
  public settings!: any;
  public version!: number;
  public isActive!: boolean;
  public createdBy!: string;
  public createdAt!: Date;
  public updatedAt!: Date;
}

Configuration.init({
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
  name: {
    type: DataTypes.STRING(255),
    allowNull: false,
    validate: {
      len: [1, 100]
    }
  },
  description: {
    type: DataTypes.TEXT,
    allowNull: true
  },
  editorType: {
    type: DataTypes.ENUM('vscode', 'cursor'),
    allowNull: false,
    defaultValue: 'vscode'
  },
  settings: {
    type: DataTypes.JSONB,
    allowNull: false,
    defaultValue: {}
  },
  version: {
    type: DataTypes.INTEGER,
    allowNull: false,
    defaultValue: 1
  },
  isActive: {
    type: DataTypes.BOOLEAN,
    defaultValue: true
  },
  createdBy: {
    type: DataTypes.UUID,
    allowNull: false,
    references: {
      model: 'users',
      key: 'id'
    }
  }
}, {
  sequelize,
  modelName: 'Configuration',
  tableName: 'configurations',
  timestamps: true,
  indexes: [
    {
      fields: ['teamId']
    },
    {
      fields: ['teamId', 'version']
    },
    {
      fields: ['teamId', 'isActive']
    }
  ]
});

export default Configuration;
