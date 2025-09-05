import { ExtensionsManager, ExtensionConfig } from './extensionsManager';
import { ConfigLoader } from './configLoader';
import { TeamConfig } from '../types/config';
import * as vscode from 'vscode';

export class ExtensionsSyncService {
  private extensionsManager: ExtensionsManager;

  constructor() {
    this.extensionsManager = new ExtensionsManager();
  }

  async syncExtensions(configDir: string, teamConfig: TeamConfig): Promise<void> {
    try {
      if (teamConfig.settings.vscode.extensions) {
        const extensionConfig = await ConfigLoader.loadSettingsFile(
          configDir,
          teamConfig.settings.vscode.extensions
        ) as ExtensionConfig;

        await this.extensionsManager.updateExtensionsJson(extensionConfig);
        await this.extensionsManager.processExtensionRecommendations(extensionConfig);

        vscode.window.showInformationMessage('확장 동기화 완료');
      }
    } catch (error) {
      throw new Error(`확장 동기화 실패: ${error}`);
    }
  }

  async generateExtensionReport(): Promise<string> {
    const installed = await this.extensionsManager.getInstalledExtensions();
    
    const report = [
      '## 설치된 확장 목록',
      '',
      ...installed.map(ext => `- ${ext}`)
    ].join('\n');

    return report;
  }
}
