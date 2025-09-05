import { GitService } from './gitService';
import { ConfigLoader } from './configLoader';
import { ConfigValidator } from '../utils/configValidator';
import { TeamConfig } from '../types/config';

export class SyncService {
  private gitService: GitService;

  constructor() {
    this.gitService = new GitService();
  }

  async syncTeamSettings(repositoryUrl: string): Promise<TeamConfig> {
    try {
      // 1. Git 저장소에서 설정 가져오기
      const configDir = await this.gitService.cloneOrUpdateConfig(repositoryUrl);
      
      // 2. 설정 파일 로드
      const teamConfig = await ConfigLoader.loadTeamConfig(configDir);
      
      // 3. 설정 검증
      const errors = ConfigValidator.validate(teamConfig);
      if (errors.length > 0) {
        throw new Error(`설정 검증 실패: ${errors.join(', ')}`);
      }

      return teamConfig;
    } catch (error) {
      throw new Error(`동기화 실패: ${error}`);
    }
  }
}
