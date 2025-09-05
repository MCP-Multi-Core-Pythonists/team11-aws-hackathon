import { DataTypes, Model, Optional } from 'sequelize';
import { sequelize } from '../config/database';

interface UserAttributes {
  id: string;
  email: string;
  name: string;
  avatar?: string;
  provider: 'google' | 'github' | 'email';
  providerId?: string;
  emailVerified: boolean;
  createdAt: Date;
  updatedAt: Date;
  lastLoginAt?: Date;
}

interface UserCreationAttributes extends Optional<UserAttributes, 'id' | 'createdAt' | 'updatedAt' | 'avatar' | 'providerId' | 'emailVerified' | 'lastLoginAt'> {}

export class User extends Model<UserAttributes, UserCreationAttributes> implements UserAttributes {
  public id!: string;
  public email!: string;
  public name!: string;
  public avatar?: string;
  public provider!: 'google' | 'github' | 'email';
  public providerId?: string;
  public emailVerified!: boolean;
  public createdAt!: Date;
  public updatedAt!: Date;
  public lastLoginAt?: Date;

  // 연관 관계 메서드들
  public getTeams!: () => Promise<any[]>;
  public getRefreshTokens!: () => Promise<any[]>;
}

User.init({
  id: {
    type: DataTypes.UUID,
    defaultValue: DataTypes.UUIDV4,
    primaryKey: true
  },
  email: {
    type: DataTypes.STRING(255),
    allowNull: false,
    unique: true,
    validate: {
      isEmail: true
    }
  },
  name: {
    type: DataTypes.STRING(255),
    allowNull: false,
    validate: {
      len: [1, 255]
    }
  },
  avatar: {
    type: DataTypes.TEXT,
    allowNull: true,
    validate: {
      isUrl: true
    }
  },
  provider: {
    type: DataTypes.ENUM('google', 'github', 'email'),
    allowNull: false
  },
  providerId: {
    type: DataTypes.STRING(255),
    allowNull: true
  },
  emailVerified: {
    type: DataTypes.BOOLEAN,
    defaultValue: false
  },
  lastLoginAt: {
    type: DataTypes.DATE,
    allowNull: true
  }
}, {
  sequelize,
  modelName: 'User',
  tableName: 'users',
  timestamps: true,
  indexes: [
    {
      unique: true,
      fields: ['email']
    },
    {
      unique: true,
      fields: ['provider', 'providerId'],
      where: {
        providerId: {
          [DataTypes.Op.ne]: null
        }
      }
    }
  ],
  hooks: {
    beforeCreate: (user: User) => {
      // 이메일 소문자 변환
      user.email = user.email.toLowerCase();
    },
    beforeUpdate: (user: User) => {
      if (user.changed('email')) {
        user.email = user.email.toLowerCase();
      }
    }
  }
});

export default User;
