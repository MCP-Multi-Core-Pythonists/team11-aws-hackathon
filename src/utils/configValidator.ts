import { TeamConfig } from '../types/config';

export class ConfigValidator {
  static validate(config: TeamConfig): string[] {
    const errors: string[] = [];

    if (!config.version) {
      errors.push('version 필드가 필요합니다');
    }

    if (!config.organization?.name) {
      errors.push('organization.name 필드가 필요합니다');
    }

    if (!config.organization?.repository) {
      errors.push('organization.repository 필드가 필요합니다');
    }

    return errors;
  }
}
