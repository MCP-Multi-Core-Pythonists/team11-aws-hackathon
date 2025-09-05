# Extension Service 구현 명세서

## 1. 서비스 개요

### 1.1 목적
TeamSync Pro의 VS Code Extension으로, 개발자의 IDE 내에서 팀 설정 동기화 및 협업 기능을 제공합니다.

### 1.2 기술 스택
- **Runtime**: Node.js (VS Code Extension Host)
- **Language**: TypeScript
- **API**: VS Code Extension API
- **Build Tool**: TypeScript Compiler
- **Package Manager**: npm

## 2. 아키텍처 설계

### 2.1 디렉토리 구조
```
src/extension/
├── src/
│   ├── auth/           # 인증 관련
│   ├── sync/           # 동기화 엔진
│   ├── ui/             # 사용자 인터페이스
│   ├── utils/          # 유틸리티
│   └── extension.ts    # 메인 엔트리 포인트
├── package.json        # Extension 매니페스트
├── tsconfig.json
└── .vscode/
    ├── launch.json     # 디버깅 설정
    └── tasks.json      # 빌드 태스크
```

### 2.2 핵심 컴포넌트

#### 2.2.1 인증 시스템 (AuthProvider)
- **Device Flow**: OAuth 2.0 Device Flow 구현
- **토큰 관리**: JWT 토큰 저장 및 갱신
- **상태 관리**: 로그인/로그아웃 상태 추적

#### 2.2.2 동기화 엔진 (SyncEngine)
- **설정 수집**: VS Code 설정, 확장, 키바인딩 수집
- **업로드/다운로드**: 서버와 설정 동기화
- **자동 동기화**: 주기적 동기화 및 변경 감지

#### 2.2.3 사용자 인터페이스 (UI Components)
- **Command Palette**: 명령어 등록 및 처리
- **Status Bar**: 동기화 상태 표시
- **Notification**: 사용자 알림 및 피드백

## 3. Extension 매니페스트

### 3.1 package.json 설정
```json
{
  "name": "teamsync-pro",
  "displayName": "TeamSync Pro",
  "description": "팀 개발 환경 설정 동기화 및 협업 도구",
  "version": "0.1.0",
  "publisher": "teamsync",
  "engines": {
    "vscode": "^1.80.0"
  },
  "categories": ["Other"],
  "activationEvents": ["onStartupFinished"],
  "main": "./out/extension.js",
  "contributes": {
    "commands": [
      {
        "command": "teamsync.login",
        "title": "로그인",
        "category": "TeamSync"
      },
      {
        "command": "teamsync.logout",
        "title": "로그아웃",
        "category": "TeamSync"
      },
      {
        "command": "teamsync.syncToRemote",
        "title": "설정을 원격으로 동기화",
        "category": "TeamSync"
      },
      {
        "command": "teamsync.syncFromRemote",
        "title": "원격에서 설정 가져오기",
        "category": "TeamSync"
      },
      {
        "command": "teamsync.selectTeam",
        "title": "팀 선택",
        "category": "TeamSync"
      }
    ],
    "configuration": {
      "title": "TeamSync Pro",
      "properties": {
        "teamsync.autoSync": {
          "type": "boolean",
          "default": true,
          "description": "자동 동기화 활성화"
        },
        "teamsync.syncInterval": {
          "type": "number",
          "default": 300,
          "description": "동기화 간격 (초)"
        }
      }
    }
  }
}
```

## 4. 핵심 기능 구현

### 4.1 인증 시스템

#### 4.1.1 AuthProvider 클래스
```typescript
export class AuthProvider {
  private context: vscode.ExtensionContext;
  private readonly API_BASE_URL = 'http://localhost:3001/api/v1';
  private tokens: AuthTokens | null = null;

  constructor(context: vscode.ExtensionContext) {
    this.context = context;
  }

  // Device Flow 로그인
  async login(): Promise<boolean> {
    try {
      // 1. Device Code 요청
      const deviceCode = await this.requestDeviceCode();
      
      // 2. 사용자에게 인증 URL 표시
      const authUrl = `${deviceCode.verification_uri}?user_code=${deviceCode.user_code}`;
      const result = await vscode.window.showInformationMessage(
        `브라우저에서 인증을 완료해주세요.\n코드: ${deviceCode.user_code}`,
        '브라우저 열기',
        '취소'
      );

      if (result === '브라우저 열기') {
        await vscode.env.openExternal(vscode.Uri.parse(authUrl));
      } else {
        return false;
      }

      // 3. 토큰 폴링
      const tokens = await this.pollForTokens(deviceCode.device_code, deviceCode.interval);
      
      if (tokens) {
        await this.saveTokens(tokens);
        vscode.window.showInformationMessage('TeamSync 로그인 성공!');
        return true;
      }

      return false;
    } catch (error) {
      Logger.error('로그인 실패:', error);
      vscode.window.showErrorMessage(`로그인 실패: ${error.message}`);
      return false;
    }
  }

  // 토큰 폴링
  private async pollForTokens(deviceCode: string, interval: number): Promise<AuthTokens | null> {
    const maxAttempts = 60; // 5분
    let attempts = 0;

    return new Promise((resolve) => {
      const poll = async () => {
        attempts++;
        
        if (attempts > maxAttempts) {
          resolve(null);
          return;
        }

        try {
          const response = await fetch(`${this.API_BASE_URL}/auth/token`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              grant_type: 'device_code',
              device_code: deviceCode
            })
          });

          if (response.ok) {
            const tokens = await response.json();
            resolve({
              accessToken: tokens.access_token,
              refreshToken: tokens.refresh_token,
              expiresAt: Date.now() + (tokens.expires_in * 1000)
            });
            return;
          }

          // 아직 인증되지 않음, 계속 폴링
          setTimeout(poll, interval * 1000);
        } catch (error) {
          Logger.error('토큰 폴링 오류:', error);
          setTimeout(poll, interval * 1000);
        }
      };

      poll();
    });
  }
}
```

#### 4.1.2 토큰 관리
```typescript
interface AuthTokens {
  accessToken: string;
  refreshToken: string;
  expiresAt: number;
}

// 토큰 저장
private async saveTokens(tokens: AuthTokens): Promise<void> {
  await this.context.secrets.store('teamsync.tokens', JSON.stringify(tokens));
  this.tokens = tokens;
}

// 토큰 조회
private async getTokens(): Promise<AuthTokens | null> {
  if (this.tokens && this.tokens.expiresAt > Date.now()) {
    return this.tokens;
  }

  const stored = await this.context.secrets.get('teamsync.tokens');
  if (stored) {
    this.tokens = JSON.parse(stored);
    return this.tokens;
  }

  return null;
}

// 토큰 갱신
private async refreshTokens(): Promise<void> {
  const tokens = await this.getTokens();
  if (!tokens?.refreshToken) {
    throw new Error('Refresh token not found');
  }

  const response = await fetch(`${this.API_BASE_URL}/auth/refresh`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ refresh_token: tokens.refreshToken })
  });

  if (response.ok) {
    const newTokens = await response.json();
    await this.saveTokens({
      accessToken: newTokens.access_token,
      refreshToken: newTokens.refresh_token,
      expiresAt: Date.now() + (newTokens.expires_in * 1000)
    });
  } else {
    throw new Error('Token refresh failed');
  }
}
```

### 4.2 동기화 엔진

#### 4.2.1 SyncEngine 클래스
```typescript
export class SyncEngine {
  private context: vscode.ExtensionContext;
  private authProvider: AuthProvider;
  private autoSyncTimer?: NodeJS.Timeout;

  constructor(context: vscode.ExtensionContext, authProvider: AuthProvider) {
    this.context = context;
    this.authProvider = authProvider;
  }

  // 원격으로 동기화 (업로드)
  async syncToRemote(): Promise<SyncResult> {
    try {
      const accessToken = await this.authProvider.getAccessToken();
      if (!accessToken) {
        return { success: false, message: '로그인이 필요합니다.' };
      }

      // 현재 설정 수집
      const configuration = await this.collectCurrentConfiguration();
      
      // 팀 ID 가져오기
      const teamId = this.context.globalState.get<string>('teamsync.selectedTeam');
      if (!teamId) {
        return { success: false, message: '팀을 선택해주세요.' };
      }

      // 서버로 업로드
      const response = await fetch(`${this.API_BASE_URL}/api/v1/configurations/sync`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${accessToken}`
        },
        body: JSON.stringify({
          teamId,
          configuration
        })
      });

      if (!response.ok) {
        const error = await response.json();
        return { success: false, message: error.message || '동기화 실패' };
      }

      Logger.info('원격 동기화 완료');
      return { success: true, message: '설정이 성공적으로 동기화되었습니다.' };

    } catch (error) {
      Logger.error('동기화 실패:', error);
      return { success: false, message: '동기화 중 오류가 발생했습니다.' };
    }
  }

  // 원격에서 동기화 (다운로드)
  async syncFromRemote(): Promise<SyncResult> {
    try {
      const accessToken = await this.authProvider.getAccessToken();
      if (!accessToken) {
        return { success: false, message: '로그인이 필요합니다.' };
      }

      const teamId = this.context.globalState.get<string>('teamsync.selectedTeam');
      if (!teamId) {
        return { success: false, message: '팀을 선택해주세요.' };
      }

      // 원격 설정 가져오기
      const response = await fetch(`${this.API_BASE_URL}/api/v1/configurations/teams/${teamId}/latest`, {
        headers: {
          'Authorization': `Bearer ${accessToken}`
        }
      });

      if (!response.ok) {
        const error = await response.json();
        return { success: false, message: error.message || '설정 가져오기 실패' };
      }

      const remoteConfig = await response.json();
      
      // 로컬에 적용
      await this.applyConfiguration(remoteConfig.configuration);
      
      Logger.info('원격 설정 적용 완료');
      return { success: true, message: '원격 설정이 성공적으로 적용되었습니다.' };

    } catch (error) {
      Logger.error('원격 동기화 실패:', error);
      return { success: false, message: '원격 동기화 중 오류가 발생했습니다.' };
    }
  }

  // 현재 설정 수집
  private async collectCurrentConfiguration(): Promise<ConfigurationData> {
    const workspaceConfig = vscode.workspace.getConfiguration();
    
    return {
      settings: {
        // VS Code 설정
        'editor.fontSize': workspaceConfig.get('editor.fontSize'),
        'editor.tabSize': workspaceConfig.get('editor.tabSize'),
        'editor.insertSpaces': workspaceConfig.get('editor.insertSpaces'),
        'files.autoSave': workspaceConfig.get('files.autoSave'),
        // 추가 설정들...
      },
      extensions: await this.getInstalledExtensions(),
      keybindings: await this.getKeybindings(),
      snippets: await this.getSnippets()
    };
  }

  // 설정 적용
  private async applyConfiguration(config: ConfigurationData): Promise<void> {
    const workspaceConfig = vscode.workspace.getConfiguration();

    // 설정 적용
    if (config.settings) {
      for (const [key, value] of Object.entries(config.settings)) {
        await workspaceConfig.update(key, value, vscode.ConfigurationTarget.Global);
      }
    }

    // 확장 설치 권장
    if (config.extensions) {
      await this.recommendExtensions(config.extensions);
    }

    // 키바인딩 적용 (향후 구현)
    // 스니펫 적용 (향후 구현)
  }
}
```

#### 4.2.2 자동 동기화
```typescript
// 자동 동기화 시작
async startAutoSync(): Promise<void> {
  const config = vscode.workspace.getConfiguration('teamsync');
  const autoSync = config.get<boolean>('autoSync', true);
  const interval = config.get<number>('syncInterval', 300) * 1000; // 초를 밀리초로

  if (!autoSync) {
    return;
  }

  this.autoSyncTimer = setInterval(async () => {
    try {
      await this.syncFromRemote();
      Logger.info('자동 동기화 완료');
    } catch (error) {
      Logger.error('자동 동기화 실패:', error);
    }
  }, interval);

  Logger.info(`자동 동기화 시작 (${interval / 1000}초 간격)`);
}

// 자동 동기화 중지
stopAutoSync(): void {
  if (this.autoSyncTimer) {
    clearInterval(this.autoSyncTimer);
    this.autoSyncTimer = undefined;
    Logger.info('자동 동기화 중지');
  }
}
```

### 4.3 사용자 인터페이스

#### 4.3.1 명령어 등록
```typescript
// commands.ts
export function registerCommands(
  context: vscode.ExtensionContext,
  authProvider: AuthProvider,
  syncEngine: SyncEngine
): void {
  
  // 로그인 명령어
  const loginCommand = vscode.commands.registerCommand('teamsync.login', async () => {
    const success = await authProvider.login();
    if (success) {
      await syncEngine.startAutoSync();
      vscode.commands.executeCommand('teamsync.updateStatusBar');
    }
  });

  // 팀 선택 명령어
  const selectTeamCommand = vscode.commands.registerCommand('teamsync.selectTeam', async () => {
    const isAuthenticated = await authProvider.isAuthenticated();
    if (!isAuthenticated) {
      vscode.window.showWarningMessage('먼저 로그인해주세요.');
      return;
    }

    try {
      const teams = await fetchUserTeams(authProvider);
      
      if (teams.length === 0) {
        vscode.window.showInformationMessage('참여 중인 팀이 없습니다.');
        return;
      }

      const teamItems = teams.map(team => ({
        label: team.name,
        description: team.description,
        team
      }));

      const selected = await vscode.window.showQuickPick(teamItems, {
        placeHolder: '동기화할 팀을 선택하세요'
      });

      if (selected) {
        context.globalState.update('teamsync.selectedTeam', selected.team.id);
        vscode.window.showInformationMessage(`팀 '${selected.team.name}'이 선택되었습니다.`);
      }
    } catch (error) {
      Logger.error('팀 선택 실패:', error);
      vscode.window.showErrorMessage('팀 목록을 가져오는데 실패했습니다.');
    }
  });

  // 동기화 명령어들
  const syncToRemoteCommand = vscode.commands.registerCommand('teamsync.syncToRemote', async () => {
    vscode.window.withProgress({
      location: vscode.ProgressLocation.Notification,
      title: '설정을 원격으로 동기화 중...',
      cancellable: false
    }, async () => {
      const result = await syncEngine.syncToRemote();
      
      if (result.success) {
        vscode.window.showInformationMessage(result.message);
      } else {
        vscode.window.showErrorMessage(result.message);
      }
    });
  });

  // 컨텍스트에 명령어 등록
  context.subscriptions.push(
    loginCommand,
    selectTeamCommand,
    syncToRemoteCommand
  );
}
```

#### 4.3.2 상태바 관리
```typescript
// statusBar.ts
export class StatusBarManager {
  private statusBarItem: vscode.StatusBarItem;

  constructor() {
    this.statusBarItem = vscode.window.createStatusBarItem(
      vscode.StatusBarAlignment.Right,
      100
    );
  }

  initialize(): void {
    this.statusBarItem.command = 'teamsync.showPanel';
    this.updateStatus(false);
    this.statusBarItem.show();
  }

  setAuthenticated(authenticated: boolean): void {
    this.updateStatus(authenticated);
  }

  setSyncing(syncing: boolean): void {
    if (syncing) {
      this.statusBarItem.text = '$(sync~spin) TeamSync';
      this.statusBarItem.tooltip = '동기화 중...';
    } else {
      this.updateStatus(true);
    }
  }

  private updateStatus(authenticated: boolean): void {
    if (authenticated) {
      this.statusBarItem.text = '$(cloud) TeamSync';
      this.statusBarItem.tooltip = 'TeamSync Pro - 연결됨';
      this.statusBarItem.backgroundColor = undefined;
    } else {
      this.statusBarItem.text = '$(cloud-offline) TeamSync';
      this.statusBarItem.tooltip = 'TeamSync Pro - 로그인 필요';
      this.statusBarItem.backgroundColor = new vscode.ThemeColor('statusBarItem.warningBackground');
    }
  }

  dispose(): void {
    this.statusBarItem.dispose();
  }
}
```

## 5. 설정 및 데이터 타입

### 5.1 TypeScript 인터페이스
```typescript
// types.ts
export interface AuthTokens {
  accessToken: string;
  refreshToken: string;
  expiresAt: number;
}

export interface DeviceCodeResponse {
  device_code: string;
  user_code: string;
  verification_uri: string;
  expires_in: number;
  interval: number;
}

export interface ConfigurationData {
  settings?: Record<string, any>;
  extensions?: string[];
  keybindings?: KeyBinding[];
  snippets?: Record<string, Snippet>;
  tasks?: TaskDefinition[];
}

export interface SyncResult {
  success: boolean;
  message: string;
  data?: any;
}

export interface Team {
  id: string;
  name: string;
  description?: string;
  memberRole: 'owner' | 'admin' | 'member';
  joinedAt: string;
}

export interface User {
  id: string;
  email: string;
  name: string;
  avatar?: string;
}
```

### 5.2 설정 스키마
```typescript
// configuration schema
export const configurationSchema = {
  type: 'object',
  properties: {
    'teamsync.autoSync': {
      type: 'boolean',
      default: true,
      description: '자동 동기화 활성화'
    },
    'teamsync.syncInterval': {
      type: 'number',
      default: 300,
      minimum: 60,
      maximum: 3600,
      description: '동기화 간격 (초)'
    },
    'teamsync.notifications': {
      type: 'boolean',
      default: true,
      description: '동기화 알림 표시'
    },
    'teamsync.conflictResolution': {
      type: 'string',
      enum: ['ask', 'local', 'remote'],
      default: 'ask',
      description: '설정 충돌 해결 방법'
    }
  }
};
```

## 6. 에러 처리 및 로깅

### 6.1 Logger 유틸리티
```typescript
// logger.ts
export class Logger {
  private static outputChannel: vscode.OutputChannel;

  static initialize(): void {
    this.outputChannel = vscode.window.createOutputChannel('TeamSync Pro');
  }

  static info(message: string, ...args: any[]): void {
    const timestamp = new Date().toISOString();
    const logMessage = `[${timestamp}] INFO: ${message}`;
    
    this.outputChannel.appendLine(logMessage);
    if (args.length > 0) {
      this.outputChannel.appendLine(JSON.stringify(args, null, 2));
    }
    
    console.log(logMessage, ...args);
  }

  static error(message: string, error?: any): void {
    const timestamp = new Date().toISOString();
    const logMessage = `[${timestamp}] ERROR: ${message}`;
    
    this.outputChannel.appendLine(logMessage);
    if (error) {
      this.outputChannel.appendLine(error.stack || error.toString());
    }
    
    console.error(logMessage, error);
  }

  static warn(message: string, ...args: any[]): void {
    const timestamp = new Date().toISOString();
    const logMessage = `[${timestamp}] WARN: ${message}`;
    
    this.outputChannel.appendLine(logMessage);
    console.warn(logMessage, ...args);
  }

  static show(): void {
    this.outputChannel.show();
  }
}
```

### 6.2 에러 처리 패턴
```typescript
// 네트워크 에러 처리
async function handleApiCall<T>(apiCall: () => Promise<T>): Promise<T> {
  try {
    return await apiCall();
  } catch (error) {
    if (error instanceof TypeError && error.message.includes('fetch')) {
      throw new Error('서버에 연결할 수 없습니다. 네트워크 연결을 확인해주세요.');
    }
    
    if (error.status === 401) {
      throw new Error('인증이 만료되었습니다. 다시 로그인해주세요.');
    }
    
    if (error.status === 403) {
      throw new Error('권한이 없습니다.');
    }
    
    if (error.status >= 500) {
      throw new Error('서버 오류가 발생했습니다. 잠시 후 다시 시도해주세요.');
    }
    
    throw error;
  }
}
```

## 7. 테스트 및 디버깅

### 7.1 디버깅 설정
```json
// .vscode/launch.json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Extension",
      "type": "extensionHost",
      "request": "launch",
      "runtimeExecutable": "${execPath}",
      "args": ["--extensionDevelopmentPath=${workspaceFolder}"],
      "outFiles": ["${workspaceFolder}/out/**/*.js"],
      "stopOnEntry": false
    }
  ]
}
```

### 7.2 단위 테스트
```typescript
// auth.test.ts
import * as assert from 'assert';
import { AuthProvider } from '../src/auth/authProvider';

suite('AuthProvider Tests', () => {
  test('should validate token expiration', () => {
    const tokens = {
      accessToken: 'test-token',
      refreshToken: 'refresh-token',
      expiresAt: Date.now() + 3600000 // 1시간 후
    };
    
    const authProvider = new AuthProvider(mockContext);
    const isValid = authProvider.isTokenValid(tokens);
    
    assert.strictEqual(isValid, true);
  });

  test('should detect expired token', () => {
    const tokens = {
      accessToken: 'test-token',
      refreshToken: 'refresh-token',
      expiresAt: Date.now() - 1000 // 1초 전
    };
    
    const authProvider = new AuthProvider(mockContext);
    const isValid = authProvider.isTokenValid(tokens);
    
    assert.strictEqual(isValid, false);
  });
});
```

## 8. 배포 및 패키징

### 8.1 빌드 스크립트
```json
// package.json scripts
{
  "scripts": {
    "compile": "tsc -p ./",
    "watch": "tsc -watch -p ./",
    "package": "vsce package",
    "publish": "vsce publish",
    "test": "npm run compile && node ./out/test/runTest.js"
  }
}
```

### 8.2 VSIX 패키징
```bash
# VSCE 설치
npm install -g vsce

# 패키지 생성
vsce package

# 마켓플레이스 게시
vsce publish
```

## 9. TODO 및 향후 계획

### 9.1 단기 목표 (1주)
- [ ] 설정 충돌 해결 UI
- [ ] 확장 자동 설치 기능
- [ ] 키바인딩 동기화
- [ ] 스니펫 동기화

### 9.2 중기 목표 (1개월)
- [ ] 실시간 동기화 (WebSocket)
- [ ] 설정 백업/복원
- [ ] 팀 템플릿 적용
- [ ] 사용 통계 수집

### 9.3 장기 목표 (3개월)
- [ ] 다중 워크스페이스 지원
- [ ] 플러그인 시스템
- [ ] AI 기반 설정 추천
- [ ] 엔터프라이즈 기능
