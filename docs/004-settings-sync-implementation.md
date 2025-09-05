# 004 - settings.json 동기화 기능

## 📋 개발 목표
팀 설정 저장소의 settings.json을 로컬 VS Code 설정에 동기화하는 기능을 구현합니다.

## 🎯 구현 범위
- VS Code settings.json 읽기/쓰기
- 설정 병합 로직 (권장/강제 모드)
- 백업 및 복원 기능
- 사용자 승인 프로세스

## 🛠️ 기술 스택
- VS Code Configuration API
- JSON 파싱 및 병합
- 파일 시스템 조작

## 📝 구현 단계

### 1단계: 설정 관리자 클래스
```typescript
// src/services/settingsManager.ts
import * as vscode from 'vscode';
import * as fs from 'fs';
import * as path from 'path';

export class SettingsManager {
  private workspaceConfig: vscode.WorkspaceConfiguration;
  private settingsPath: string;

  constructor() {
    this.workspaceConfig = vscode.workspace.getConfiguration();
    this.settingsPath = this.getSettingsPath();
  }

  private getSettingsPath(): string {
    const workspaceFolder = vscode.workspace.workspaceFolders?.[0];
    if (workspaceFolder) {
      return path.join(workspaceFolder.uri.fsPath, '.vscode', 'settings.json');
    }
    throw new Error('워크스페이스를 찾을 수 없습니다');
  }

  async getCurrentSettings(): Promise<any> {
    try {
      if (fs.existsSync(this.settingsPath)) {
        const content = fs.readFileSync(this.settingsPath, 'utf8');
        return JSON.parse(content);
      }
      return {};
    } catch (error) {
      return {};
    }
  }
}
```

### 2단계: 설정 병합 로직
```typescript
// SettingsManager 클래스 내부 메서드
async mergeSettings(teamSettings: any, mode: 'recommended' | 'force'): Promise<void> {
  const currentSettings = await this.getCurrentSettings();
  
  if (mode === 'recommended') {
    await this.recommendedMerge(currentSettings, teamSettings);
  } else {
    await this.forceMerge(teamSettings);
  }
}

private async recommendedMerge(current: any, team: any): Promise<void> {
  const conflicts = this.findConflicts(current, team);
  
  if (conflicts.length > 0) {
    const shouldApply = await this.showConflictDialog(conflicts);
    if (shouldApply) {
      await this.applySettings({ ...current, ...team });
    }
  } else {
    await this.applySettings({ ...current, ...team });
  }
}

private async forceMerge(teamSettings: any): Promise<void> {
  await this.backupCurrentSettings();
  await this.applySettings(teamSettings);
  vscode.window.showInformationMessage('팀 설정이 강제 적용되었습니다');
}
```

### 3단계: 충돌 감지 및 사용자 승인
```typescript
// SettingsManager 클래스 내부 메서드
private findConflicts(current: any, team: any): string[] {
  const conflicts: string[] = [];
  
  for (const key in team) {
    if (current[key] && current[key] !== team[key]) {
      conflicts.push(key);
    }
  }
  
  return conflicts;
}

private async showConflictDialog(conflicts: string[]): Promise<boolean> {
  const message = `다음 설정이 변경됩니다:\n${conflicts.join('\n')}`;
  const result = await vscode.window.showWarningMessage(
    message,
    { modal: true },
    '적용',
    '취소'
  );
  
  return result === '적용';
}

private async applySettings(settings: any): Promise<void> {
  const vscodePath = path.dirname(this.settingsPath);
  
  // .vscode 폴더 생성
  if (!fs.existsSync(vscodePath)) {
    fs.mkdirSync(vscodePath, { recursive: true });
  }
  
  // settings.json 저장
  fs.writeFileSync(this.settingsPath, JSON.stringify(settings, null, 2));
  
  vscode.window.showInformationMessage('설정이 적용되었습니다');
}
```

### 4단계: 백업 및 복원 기능
```typescript
// SettingsManager 클래스 내부 메서드
private async backupCurrentSettings(): Promise<void> {
  const backupPath = this.settingsPath + '.backup';
  
  if (fs.existsSync(this.settingsPath)) {
    fs.copyFileSync(this.settingsPath, backupPath);
  }
}

async restoreBackup(): Promise<void> {
  const backupPath = this.settingsPath + '.backup';
  
  if (fs.existsSync(backupPath)) {
    fs.copyFileSync(backupPath, this.settingsPath);
    vscode.window.showInformationMessage('설정이 복원되었습니다');
  } else {
    vscode.window.showErrorMessage('백업 파일을 찾을 수 없습니다');
  }
}
```

### 5단계: 통합 설정 동기화 서비스
```typescript
// src/services/settingsSyncService.ts
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
```

### 6단계: 명령어 등록 및 통합
```typescript
// src/extension.ts 업데이트
import { SettingsSyncService } from './services/settingsSyncService';

export function activate(context: vscode.ExtensionContext) {
    const settingsSyncService = new SettingsSyncService();

    // 기존 syncSettings 명령어 업데이트
    const syncCommand = vscode.commands.registerCommand('teamsync.syncSettings', async () => {
        try {
            const repoUrl = await vscode.window.showInputBox({
                prompt: '팀 설정 저장소 URL을 입력하세요'
            });

            if (repoUrl) {
                const syncService = new SyncService();
                const config = await syncService.syncTeamSettings(repoUrl);
                
                // VS Code 설정 동기화
                await settingsSyncService.syncVSCodeSettings('.teamsync', config);
                
                vscode.window.showInformationMessage('팀 설정 동기화 완료!');
            }
        } catch (error) {
            vscode.window.showErrorMessage(`동기화 실패: ${error}`);
        }
    });

    // 설정 복원 명령어
    const restoreCommand = vscode.commands.registerCommand('teamsync.restoreSettings', async () => {
        try {
            const settingsManager = new SettingsManager();
            await settingsManager.restoreBackup();
        } catch (error) {
            vscode.window.showErrorMessage(`복원 실패: ${error}`);
        }
    });

    context.subscriptions.push(syncCommand, restoreCommand);
}
```

## ✅ 완료 기준
- [ ] VS Code settings.json 읽기/쓰기 기능 구현
- [ ] 권장/강제 모드 설정 병합 로직 구현
- [ ] 충돌 감지 및 사용자 승인 프로세스 구현
- [ ] 백업 및 복원 기능 구현

## 🔗 다음 단계
005-extensions-sync-implementation.md - extensions.json 적용 기능

## 📚 참고 자료
- [VS Code Configuration API](https://code.visualstudio.com/api/references/vscode-api#workspace.getConfiguration)
- [Workspace Settings](https://code.visualstudio.com/docs/getstarted/settings#_workspace-settings)
