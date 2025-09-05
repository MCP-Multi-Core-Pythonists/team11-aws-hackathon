# 005 - extensions.json 적용 기능

## 📋 개발 목표
팀 설정 저장소의 extensions.json을 기반으로 권장 확장과 차단 확장을 관리하는 기능을 구현합니다.

## 🎯 구현 범위
- extensions.json 파일 처리
- 권장 확장 설치 안내
- 차단 확장 비활성화
- 확장 상태 모니터링

## 🛠️ 기술 스택
- VS Code Extensions API
- 확장 설치/비활성화 명령어
- 상태 관리

## 📝 구현 단계

### 1단계: 확장 관리자 클래스
```typescript
// src/services/extensionsManager.ts
import * as vscode from 'vscode';

export interface ExtensionConfig {
  recommendations: string[];
  unwantedRecommendations?: string[];
}

export class ExtensionsManager {
  async getInstalledExtensions(): Promise<string[]> {
    return vscode.extensions.all
      .filter(ext => !ext.packageJSON.isBuiltin)
      .map(ext => ext.id);
  }

  async getExtensionStatus(extensionId: string): Promise<'installed' | 'not-installed' | 'disabled'> {
    const extension = vscode.extensions.getExtension(extensionId);
    
    if (!extension) {
      return 'not-installed';
    }
    
    return extension.isActive ? 'installed' : 'disabled';
  }

  async recommendExtension(extensionId: string): Promise<void> {
    const status = await this.getExtensionStatus(extensionId);
    
    if (status === 'not-installed') {
      const install = await vscode.window.showInformationMessage(
        `팀에서 권장하는 확장 '${extensionId}'를 설치하시겠습니까?`,
        '설치',
        '나중에'
      );
      
      if (install === '설치') {
        await this.installExtension(extensionId);
      }
    }
  }
}
```

### 2단계: 확장 설치 및 관리 로직
```typescript
// ExtensionsManager 클래스 내부 메서드
private async installExtension(extensionId: string): Promise<void> {
  try {
    await vscode.commands.executeCommand('workbench.extensions.installExtension', extensionId);
    vscode.window.showInformationMessage(`확장 '${extensionId}' 설치 완료`);
  } catch (error) {
    vscode.window.showErrorMessage(`확장 설치 실패: ${error}`);
  }
}

async disableUnwantedExtension(extensionId: string): Promise<void> {
  const extension = vscode.extensions.getExtension(extensionId);
  
  if (extension && extension.isActive) {
    const disable = await vscode.window.showWarningMessage(
      `팀 정책에 따라 확장 '${extensionId}'를 비활성화해야 합니다.`,
      '비활성화',
      '무시'
    );
    
    if (disable === '비활성화') {
      try {
        await vscode.commands.executeCommand('workbench.extensions.action.disableWorkspace', extensionId);
        vscode.window.showInformationMessage(`확장 '${extensionId}' 비활성화 완료`);
      } catch (error) {
        vscode.window.showErrorMessage(`확장 비활성화 실패: ${error}`);
      }
    }
  }
}
```

### 3단계: extensions.json 파일 관리
```typescript
// ExtensionsManager 클래스 내부 메서드
async updateExtensionsJson(config: ExtensionConfig): Promise<void> {
  const workspaceFolder = vscode.workspace.workspaceFolders?.[0];
  if (!workspaceFolder) {
    throw new Error('워크스페이스를 찾을 수 없습니다');
  }

  const extensionsPath = path.join(workspaceFolder.uri.fsPath, '.vscode', 'extensions.json');
  const vscodePath = path.dirname(extensionsPath);

  // .vscode 폴더 생성
  if (!fs.existsSync(vscodePath)) {
    fs.mkdirSync(vscodePath, { recursive: true });
  }

  // extensions.json 생성/업데이트
  fs.writeFileSync(extensionsPath, JSON.stringify(config, null, 2));
  
  vscode.window.showInformationMessage('확장 권장 목록이 업데이트되었습니다');
}

async processExtensionRecommendations(config: ExtensionConfig): Promise<void> {
  // 권장 확장 처리
  for (const extensionId of config.recommendations) {
    await this.recommendExtension(extensionId);
  }

  // 차단 확장 처리
  if (config.unwantedRecommendations) {
    for (const extensionId of config.unwantedRecommendations) {
      await this.disableUnwantedExtension(extensionId);
    }
  }
}
```

### 4단계: 확장 동기화 서비스
```typescript
// src/services/extensionsSyncService.ts
import { ExtensionsManager, ExtensionConfig } from './extensionsManager';
import { ConfigLoader } from './configLoader';
import { TeamConfig } from '../types/config';

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

        // extensions.json 파일 업데이트
        await this.extensionsManager.updateExtensionsJson(extensionConfig);

        // 확장 권장사항 처리
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
```

### 5단계: 확장 상태 모니터링
```typescript
// src/services/extensionMonitor.ts
import * as vscode from 'vscode';

export class ExtensionMonitor {
  private disposables: vscode.Disposable[] = [];

  startMonitoring(): void {
    // 확장 설치/제거 이벤트 모니터링
    const onDidChange = vscode.extensions.onDidChange(() => {
      this.checkExtensionCompliance();
    });

    this.disposables.push(onDidChange);
  }

  private async checkExtensionCompliance(): Promise<void> {
    // 팀 정책과 현재 확장 상태 비교
    // 필요시 사용자에게 알림
  }

  dispose(): void {
    this.disposables.forEach(d => d.dispose());
  }
}
```

### 6단계: 통합 및 명령어 등록
```typescript
// src/extension.ts 업데이트
import { ExtensionsSyncService } from './services/extensionsSyncService';
import { ExtensionMonitor } from './services/extensionMonitor';

export function activate(context: vscode.ExtensionContext) {
    const extensionsSyncService = new ExtensionsSyncService();
    const extensionMonitor = new ExtensionMonitor();

    // 확장 모니터링 시작
    extensionMonitor.startMonitoring();

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
                const settingsSyncService = new SettingsSyncService();
                await settingsSyncService.syncVSCodeSettings('.teamsync', config);
                
                // 확장 동기화
                await extensionsSyncService.syncExtensions('.teamsync', config);
                
                vscode.window.showInformationMessage('팀 설정 동기화 완료!');
            }
        } catch (error) {
            vscode.window.showErrorMessage(`동기화 실패: ${error}`);
        }
    });

    // 확장 리포트 생성 명령어
    const reportCommand = vscode.commands.registerCommand('teamsync.extensionReport', async () => {
        try {
            const report = await extensionsSyncService.generateExtensionReport();
            
            const doc = await vscode.workspace.openTextDocument({
                content: report,
                language: 'markdown'
            });
            
            await vscode.window.showTextDocument(doc);
        } catch (error) {
            vscode.window.showErrorMessage(`리포트 생성 실패: ${error}`);
        }
    });

    context.subscriptions.push(syncCommand, reportCommand, extensionMonitor);
}
```

## ✅ 완료 기준
- [ ] extensions.json 파일 생성/업데이트 기능 구현
- [ ] 권장 확장 설치 안내 기능 구현
- [ ] 차단 확장 비활성화 기능 구현
- [ ] 확장 상태 리포트 생성 기능 구현

## 🔗 다음 단계
006-prompt-palette-ui.md - 기본 프롬프트 팔레트 UI

## 📚 참고 자료
- [VS Code Extensions API](https://code.visualstudio.com/api/references/vscode-api#extensions)
- [Extension Recommendations](https://code.visualstudio.com/docs/editor/extension-marketplace#_workspace-recommended-extensions)
