import * as path from 'path';
import * as fs from 'fs';
import { ConfigParser } from '../utils/configParser';
import { TeamConfig } from '../types/config';

export class ConfigLoader {
  static async loadTeamConfig(configDir: string): Promise<TeamConfig> {
    const configPath = path.join(configDir, 'config.yaml');
    
    if (!fs.existsSync(configPath)) {
      throw new Error('config.yaml 파일을 찾을 수 없습니다');
    }

    return await ConfigParser.parseConfig(configPath);
  }

  static async loadSettingsFile(configDir: string, relativePath: string): Promise<any> {
    const fullPath = path.join(configDir, relativePath);
    
    if (!fs.existsSync(fullPath)) {
      throw new Error(`설정 파일을 찾을 수 없습니다: ${relativePath}`);
    }

    const content = fs.readFileSync(fullPath, 'utf8');
    return JSON.parse(content);
  }
}
