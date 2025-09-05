import * as yaml from 'js-yaml';
import * as fs from 'fs';
import { TeamConfig } from '../types/config';

export class ConfigParser {
  static async parseConfig(configPath: string): Promise<TeamConfig> {
    try {
      const fileContent = fs.readFileSync(configPath, 'utf8');
      const config = yaml.load(fileContent) as TeamConfig;
      
      return this.applyDefaults(config);
    } catch (error) {
      throw new Error(`설정 파일 파싱 실패: ${error}`);
    }
  }

  private static applyDefaults(config: Partial<TeamConfig>): TeamConfig {
    return {
      version: config.version || "1.0",
      organization: config.organization || { name: "", repository: "" },
      settings: {
        vscode: config.settings?.vscode || {},
        code_quality: config.settings?.code_quality || {}
      },
      prompts: config.prompts || [],
      policies: {
        sync_mode: config.policies?.sync_mode || 'recommended',
        auto_update: config.policies?.auto_update ?? true,
        backup_local: config.policies?.backup_local ?? true
      }
    };
  }
}
