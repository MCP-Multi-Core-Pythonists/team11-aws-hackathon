import * as vscode from 'vscode';
import { SyncService } from './syncService';
import { SettingsSyncService } from './settingsSyncService';
import { ExtensionsSyncService } from './extensionsSyncService';
import { PromptSyncService } from './promptSyncService';
import { TeamConfig } from '../types/config';

export interface SyncStatus {
  lastSync: Date | null;
  configVersion: string | null;
  syncedSettings: number;
  syncedExtensions: number;
  syncedPrompts: number;
}

export class TeamSyncService {
  private syncService: SyncService;
  private settingsSyncService: SettingsSyncService;
  private extensionsSyncService: ExtensionsSyncService;
  private promptSyncService: PromptSyncService;

  constructor() {
    this.syncService = new SyncService();
    this.settingsSyncService = new SettingsSyncService();
    this.extensionsSyncService = new ExtensionsSyncService();
    this.promptSyncService = new PromptSyncService();
  }

  async fullSync(repositoryUrl: string): Promise<TeamConfig> {
    return vscode.window.withProgress({
      location: vscode.ProgressLocation.Notification,
      title: "TeamSync Pro 동기화 중...",
      cancellable: false
    }, async (progress) => {
      try {
        progress.report({ increment: 0, message: "팀 설정 다운로드 중..." });
        const config = await this.syncService.syncTeamSettings(repositoryUrl);

        progress.report({ increment: 25, message: "VS Code 설정 동기화 중..." });
        await this.settingsSyncService.syncVSCodeSettings('.teamsync', config);

        progress.report({ increment: 50, message: "확장 동기화 중..." });
        await this.extensionsSyncService.syncExtensions('.teamsync', config);

        progress.report({ increment: 75, message: "프롬프트 동기화 중..." });
        await this.promptSyncService.syncPrompts('.teamsync', config);

        progress.report({ increment: 100, message: "동기화 완료!" });
        
        return config;
      } catch (error) {
        throw error;
      }
    });
  }

  async getStatus(): Promise<SyncStatus> {
    return {
      lastSync: new Date(),
      configVersion: "1.0",
      syncedSettings: 5,
      syncedExtensions: 3,
      syncedPrompts: 10
    };
  }

  getPromptSyncService(): PromptSyncService {
    return this.promptSyncService;
  }

  getExtensionsSyncService(): ExtensionsSyncService {
    return this.extensionsSyncService;
  }
}
