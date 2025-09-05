# 003 - Git 저장소 연동 기본 로직

## 📋 개발 목표
팀 설정 저장소에서 설정 파일을 가져오고 로컬에 동기화하는 Git 연동 기능을 구현합니다.

## 🎯 구현 범위
- Git 저장소 클론 및 업데이트
- 설정 파일 다운로드
- 로컬 캐시 관리
- 에러 처리 및 재시도 로직

## 🛠️ 기술 스택
- simple-git (Git 명령어 래퍼)
- Node.js fs 모듈
- VS Code 워크스페이스 API

## 📝 구현 단계

### 1단계: Git 클라이언트 설정
```typescript
// src/services/gitService.ts
import simpleGit, { SimpleGit } from 'simple-git';
import * as path from 'path';
import * as fs from 'fs';
import * as vscode from 'vscode';

export class GitService {
  private git: SimpleGit;
  private localConfigPath: string;

  constructor() {
    this.localConfigPath = path.join(
      vscode.workspace.workspaceFolders?.[0]?.uri.fsPath || '',
      '.teamsync'
    );
    this.git = simpleGit();
  }

  async cloneOrUpdateConfig(repositoryUrl: string): Promise<string> {
    try {
      if (fs.existsSync(this.localConfigPath)) {
        return await this.updateConfig();
      } else {
        return await this.cloneConfig(repositoryUrl);
      }
    } catch (error) {
      throw new Error(`Git 연동 실패: ${error}`);
    }
  }
}
```

### 2단계: 저장소 클론 로직
```typescript
// GitService 클래스 내부 메서드
private async cloneConfig(repositoryUrl: string): Promise<string> {
  vscode.window.showInformationMessage('팀 설정을 다운로드 중...');
  
  await this.git.clone(repositoryUrl, this.localConfigPath);
  
  vscode.window.showInformationMessage('팀 설정 다운로드 완료!');
  return this.localConfigPath;
}

private async updateConfig(): Promise<string> {
  vscode.window.showInformationMessage('팀 설정을 업데이트 중...');
  
  const git = simpleGit(this.localConfigPath);
  await git.pull();
  
  vscode.window.showInformationMessage('팀 설정 업데이트 완료!');
  return this.localConfigPath;
}
```

### 3단계: 설정 파일 로더
```typescript
// src/services/configLoader.ts
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
```

### 4단계: 통합 동기화 서비스
```typescript
// src/services/syncService.ts
import { GitService } from './gitService';
import { ConfigLoader } from './configLoader';
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
      const errors = this.validateConfig(teamConfig);
      if (errors.length > 0) {
        throw new Error(`설정 검증 실패: ${errors.join(', ')}`);
      }

      return teamConfig;
    } catch (error) {
      throw new Error(`동기화 실패: ${error}`);
    }
  }

  private validateConfig(config: TeamConfig): string[] {
    // 기본 검증 로직
    const errors: string[] = [];
    
    if (!config.version) {
      errors.push('version 필드가 필요합니다');
    }
    
    return errors;
  }
}
```

### 5단계: VS Code 명령어 등록
```typescript
// src/extension.ts 업데이트
import * as vscode from 'vscode';
import { SyncService } from './services/syncService';

export function activate(context: vscode.ExtensionContext) {
    const syncService = new SyncService();

    const syncCommand = vscode.commands.registerCommand('teamsync.syncSettings', async () => {
        try {
            const repoUrl = await vscode.window.showInputBox({
                prompt: '팀 설정 저장소 URL을 입력하세요',
                placeholder: 'https://github.com/your-org/teamsync-config'
            });

            if (repoUrl) {
                const config = await syncService.syncTeamSettings(repoUrl);
                vscode.window.showInformationMessage(`${config.organization.name} 설정 동기화 완료!`);
            }
        } catch (error) {
            vscode.window.showErrorMessage(`동기화 실패: ${error}`);
        }
    });

    context.subscriptions.push(syncCommand);
}
```

## ✅ 완료 기준
- [ ] Git 저장소 클론/업데이트 기능 구현
- [ ] 설정 파일 로드 및 파싱 기능 구현
- [ ] 에러 처리 및 사용자 피드백 구현
- [ ] VS Code 명령어로 동기화 실행 가능

## 🔗 다음 단계
004-settings-sync-implementation.md - settings.json 동기화 기능

## 📚 참고 자료
- [simple-git Documentation](https://github.com/steveukx/git-js)
- [VS Code Workspace API](https://code.visualstudio.com/api/references/vscode-api#workspace)
