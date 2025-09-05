import { User } from './User';
import { Team } from './Team';
import { TeamMember } from './TeamMember';
import { Configuration } from './Configuration';

// User associations
User.hasMany(Team, { foreignKey: 'ownerId', as: 'ownedTeams' });
User.hasMany(TeamMember, { foreignKey: 'userId' });
User.hasMany(Configuration, { foreignKey: 'createdBy' });

// Team associations
Team.belongsTo(User, { foreignKey: 'ownerId', as: 'owner' });
Team.hasMany(TeamMember, { foreignKey: 'teamId' });
Team.hasMany(Configuration, { foreignKey: 'teamId' });

// TeamMember associations
TeamMember.belongsTo(User, { foreignKey: 'userId' });
TeamMember.belongsTo(Team, { foreignKey: 'teamId' });
TeamMember.belongsTo(User, { foreignKey: 'invitedBy', as: 'inviter' });

// Configuration associations
Configuration.belongsTo(Team, { foreignKey: 'teamId' });
Configuration.belongsTo(User, { foreignKey: 'createdBy', as: 'creator' });

export {
  User,
  Team,
  TeamMember,
  Configuration
};
