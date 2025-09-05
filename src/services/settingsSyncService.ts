import { SettingsManager } from './settingsManager';
import { ConfigLoader } from './configLoader';
import { TeamConfig } from '../types/config';

export class SettingsSyncService {
  private settingsManager: SettingsManager;

  constructor() {
    this.settingsManager = new SettingsManager();
  }

  async syncVSCodeSettings(configDir: string, teamConfig: TeamConfig): Promise<void> {
    try {
      if (teamConfig.settings.vscode.settings) {
        const teamSettings = await ConfigLoader.loadSettingsFile(
          configDir, 
          teamConfig.settings.vscode.settings
        );
        
        await this.settingsManager.mergeSettings(
          teamSettings, 
          teamConfig.policies.sync_mode
        );
      }
    } catch (error) {
      throw new Error(`VS Code 설정 동기화 실패: ${error}`);
    }
  }
}
