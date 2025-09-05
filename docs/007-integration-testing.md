# 007 - 기능 통합 및 테스트

## 📋 개발 목표
개발된 모든 기능을 통합하고 데모를 위한 테스트 및 버그 수정을 진행합니다.

## 🎯 구현 범위
- 전체 기능 통합
- 에러 처리 개선
- 사용자 경험 최적화
- 데모 시나리오 준비

## 🛠️ 기술 스택
- VS Code Extension Testing
- 통합 테스트
- 에러 로깅

## 📝 구현 단계

### 1단계: 통합 서비스 클래스
```typescript
// src/services/teamSyncService.ts
import { SyncService } from './syncService';
import { SettingsSyncService } from './settingsSyncService';
import { ExtensionsSyncService } from './extensionsSyncService';
import { PromptSyncService } from './promptSyncService';
import { TeamConfig } from '../types/config';

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

  async fullSync(repositoryUrl: string): Promise<void> {
    const progress = vscode.window.withProgress({
      location: vscode.ProgressLocation.Notification,
      title: "TeamSync Pro 동기화 중...",
      cancellable: false
    }, async (progress) => {
      try {
        // 1. Git 저장소 동기화
        progress.report({ increment: 0, message: "팀 설정 다운로드 중..." });
        const config = await this.syncService.syncTeamSettings(repositoryUrl);

        // 2. VS Code 설정 동기화
        progress.report({ increment: 25, message: "VS Code 설정 동기화 중..." });
        await this.settingsSyncService.syncVSCodeSettings('.teamsync', config);

        // 3. 확장 동기화
        progress.report({ increment: 50, message: "확장 동기화 중..." });
        await this.extensionsSyncService.syncExtensions('.teamsync', config);

        // 4. 프롬프트 동기화
        progress.report({ increment: 75, message: "프롬프트 동기화 중..." });
        await this.promptSyncService.syncPrompts('.teamsync', config);

        progress.report({ increment: 100, message: "동기화 완료!" });
        
        return config;
      } catch (error) {
        throw error;
      }
    });

    await progress;
  }

  async getStatus(): Promise<SyncStatus> {
    return {
      lastSync: this.getLastSyncTime(),
      configVersion: await this.getConfigVersion(),
      syncedSettings: await this.getSyncedSettingsCount(),
      syncedExtensions: await this.getSyncedExtensionsCount(),
      syncedPrompts: await this.getSyncedPromptsCount()
    };
  }

  private getLastSyncTime(): Date | null {
    // 마지막 동기화 시간 반환
    return null;
  }

  private async getConfigVersion(): Promise<string | null> {
    // 현재 설정 버전 반환
    return null;
  }

  private async getSyncedSettingsCount(): Promise<number> {
    // 동기화된 설정 수 반환
    return 0;
  }

  private async getSyncedExtensionsCount(): Promise<number> {
    // 동기화된 확장 수 반환
    return 0;
  }

  private async getSyncedPromptsCount(): Promise<number> {
    // 동기화된 프롬프트 수 반환
    return 0;
  }
}

interface SyncStatus {
  lastSync: Date | null;
  configVersion: string | null;
  syncedSettings: number;
  syncedExtensions: number;
  syncedPrompts: number;
}
```

### 2단계: 에러 처리 및 로깅 시스템
```typescript
// src/utils/logger.ts
import * as vscode from 'vscode';

export enum LogLevel {
  DEBUG = 0,
  INFO = 1,
  WARN = 2,
  ERROR = 3
}

export class Logger {
  private static outputChannel: vscode.OutputChannel;

  static initialize(): void {
    this.outputChannel = vscode.window.createOutputChannel('TeamSync Pro');
  }

  static log(level: LogLevel, message: string, error?: any): void {
    const timestamp = new Date().toISOString();
    const levelStr = LogLevel[level];
    const logMessage = `[${timestamp}] ${levelStr}: ${message}`;

    this.outputChannel.appendLine(logMessage);

    if (error) {
      this.outputChannel.appendLine(`Error details: ${JSON.stringify(error, null, 2)}`);
    }

    // 에러 레벨인 경우 사용자에게 알림
    if (level === LogLevel.ERROR) {
      vscode.window.showErrorMessage(`TeamSync Pro: ${message}`);
    }
  }

  static debug(message: string): void {
    this.log(LogLevel.DEBUG, message);
  }

  static info(message: string): void {
    this.log(LogLevel.INFO, message);
  }

  static warn(message: string): void {
    this.log(LogLevel.WARN, message);
  }

  static error(message: string, error?: any): void {
    this.log(LogLevel.ERROR, message, error);
  }

  static show(): void {
    this.outputChannel.show();
  }
}
```

### 3단계: 상태 표시 및 사용자 피드백
```typescript
// src/ui/statusBar.ts
import * as vscode from 'vscode';

export class StatusBarManager {
  private statusBarItem: vscode.StatusBarItem;

  constructor() {
    this.statusBarItem = vscode.window.createStatusBarItem(
      vscode.StatusBarAlignment.Right,
      100
    );
    this.statusBarItem.command = 'teamsync.showStatus';
  }

  updateStatus(status: 'synced' | 'syncing' | 'error' | 'not-synced'): void {
    switch (status) {
      case 'synced':
        this.statusBarItem.text = '$(check) TeamSync';
        this.statusBarItem.tooltip = '팀 설정 동기화 완료';
        this.statusBarItem.backgroundColor = undefined;
        break;
      
      case 'syncing':
        this.statusBarItem.text = '$(sync~spin) TeamSync';
        this.statusBarItem.tooltip = '팀 설정 동기화 중...';
        this.statusBarItem.backgroundColor = undefined;
        break;
      
      case 'error':
        this.statusBarItem.text = '$(error) TeamSync';
        this.statusBarItem.tooltip = '동기화 오류 발생';
        this.statusBarItem.backgroundColor = new vscode.ThemeColor('statusBarItem.errorBackground');
        break;
      
      case 'not-synced':
        this.statusBarItem.text = '$(cloud-download) TeamSync';
        this.statusBarItem.tooltip = '팀 설정 동기화 필요';
        this.statusBarItem.backgroundColor = undefined;
        break;
    }
    
    this.statusBarItem.show();
  }

  dispose(): void {
    this.statusBarItem.dispose();
  }
}
```

### 4단계: 데모 시나리오 및 샘플 데이터
```typescript
// src/demo/demoData.ts
export const DEMO_CONFIG = {
  version: "1.0",
  organization: {
    name: "TeamSync Pro Demo",
    repository: "https://github.com/demo/teamsync-config"
  },
  settings: {
    vscode: {
      settings: "./settings/settings.json",
      extensions: "./settings/extensions.json"
    }
  },
  prompts: [
    {
      name: "code-review",
      file: "./prompts/review-prompt.md",
      category: "development"
    },
    {
      name: "refactoring",
      file: "./prompts/refactor-prompt.md",
      category: "development"
    }
  ],
  policies: {
    sync_mode: "recommended",
    auto_update: true,
    backup_local: true
  }
};

export const DEMO_SETTINGS = {
  "editor.fontSize": 14,
  "editor.tabSize": 2,
  "editor.insertSpaces": true,
  "files.autoSave": "afterDelay",
  "workbench.colorTheme": "Default Dark+",
  "editor.formatOnSave": true
};

export const DEMO_EXTENSIONS = {
  recommendations: [
    "ms-python.python",
    "esbenp.prettier-vscode",
    "ms-vscode.vscode-typescript-next"
  ],
  unwantedRecommendations: [
    "ms-vscode.vscode-json"
  ]
};
```

### 5단계: 통합 테스트 및 검증
```typescript
// src/test/integration.test.ts
import * as assert from 'assert';
import * as vscode from 'vscode';
import { TeamSyncService } from '../services/teamSyncService';

suite('TeamSync Integration Tests', () => {
  let teamSyncService: TeamSyncService;

  setup(() => {
    teamSyncService = new TeamSyncService();
  });

  test('Full sync workflow', async () => {
    // 데모 저장소로 전체 동기화 테스트
    try {
      await teamSyncService.fullSync('demo-repo-url');
      
      // 동기화 상태 확인
      const status = await teamSyncService.getStatus();
      assert.ok(status.lastSync, 'Last sync time should be set');
      assert.ok(status.syncedSettings > 0, 'Settings should be synced');
      
    } catch (error) {
      assert.fail(`Sync should not fail: ${error}`);
    }
  });

  test('Error handling', async () => {
    // 잘못된 저장소 URL로 테스트
    try {
      await teamSyncService.fullSync('invalid-url');
      assert.fail('Should throw error for invalid URL');
    } catch (error) {
      assert.ok(error, 'Should handle invalid URL gracefully');
    }
  });
});
```

### 6단계: 최종 확장 진입점 통합
```typescript
// src/extension.ts - 최종 통합 버전
import * as vscode from 'vscode';
import { TeamSyncService } from './services/teamSyncService';
import { PromptSyncService } from './services/promptSyncService';
import { StatusBarManager } from './ui/statusBar';
import { Logger } from './utils/logger';

export function activate(context: vscode.ExtensionContext) {
    // 초기화
    Logger.initialize();
    Logger.info('TeamSync Pro 확장이 활성화되었습니다');

    const teamSyncService = new TeamSyncService();
    const promptSyncService = new PromptSyncService();
    const statusBarManager = new StatusBarManager();

    // 초기 상태 설정
    statusBarManager.updateStatus('not-synced');

    // 명령어 등록
    const commands = [
        // 전체 동기화
        vscode.commands.registerCommand('teamsync.syncSettings', async () => {
            try {
                statusBarManager.updateStatus('syncing');
                
                const repoUrl = await vscode.window.showInputBox({
                    prompt: '팀 설정 저장소 URL을 입력하세요',
                    placeholder: 'https://github.com/your-org/teamsync-config'
                });

                if (repoUrl) {
                    await teamSyncService.fullSync(repoUrl);
                    statusBarManager.updateStatus('synced');
                    Logger.info('팀 설정 동기화 완료');
                }
            } catch (error) {
                statusBarManager.updateStatus('error');
                Logger.error('동기화 실패', error);
            }
        }),

        // 프롬프트 팔레트
        vscode.commands.registerCommand('teamsync.showPrompts', async () => {
            await promptSyncService.showPromptPalette();
        }),

        // 상태 표시
        vscode.commands.registerCommand('teamsync.showStatus', async () => {
            const status = await teamSyncService.getStatus();
            const message = `
마지막 동기화: ${status.lastSync?.toLocaleString() || '없음'}
설정: ${status.syncedSettings}개
확장: ${status.syncedExtensions}개  
프롬프트: ${status.syncedPrompts}개
            `.trim();
            
            vscode.window.showInformationMessage(message);
        }),

        // 로그 표시
        vscode.commands.registerCommand('teamsync.showLogs', () => {
            Logger.show();
        })
    ];

    context.subscriptions.push(...commands, statusBarManager);
    
    Logger.info('모든 명령어가 등록되었습니다');
}

export function deactivate() {
    Logger.info('TeamSync Pro 확장이 비활성화되었습니다');
}
```

## ✅ 완료 기준
- [ ] 모든 기능이 통합된 TeamSyncService 구현
- [ ] 에러 처리 및 로깅 시스템 구현
- [ ] 상태 표시 및 사용자 피드백 구현
- [ ] 데모 시나리오 및 샘플 데이터 준비
- [ ] 기본 통합 테스트 구현

## 🔗 다음 단계
데모 준비 및 발표 자료 제작

## 📚 참고 자료
- [VS Code Extension Testing](https://code.visualstudio.com/api/working-with-extensions/testing-extension)
- [Progress API](https://code.visualstudio.com/api/references/vscode-api#Progress)
