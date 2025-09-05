import * as vscode from 'vscode';

// Types
interface DeviceCodeResponse {
  device_code: string;
  user_code: string;
  verification_uri: string;
  expires_in: number;
  interval: number;
}

interface AuthTokens {
  accessToken: string;
  refreshToken: string;
  expiresAt: number;
}

interface Team {
  id: string;
  name: string;
  description?: string;
  memberRole: string;
  joinedAt: string;
}

// AuthProvider class
class AuthProvider {
  private context: vscode.ExtensionContext;
  private readonly API_BASE_URL = 'http://localhost:3001/api/v1';

  constructor(context: vscode.ExtensionContext) {
    this.context = context;
  }

  async login(): Promise<boolean> {
    try {
      console.log('TeamSync Pro Extension is now active!');
      
      // Device Code Flow 시작
      const deviceCode = await this.requestDeviceCode();
      
      // 사용자에게 인증 URL 표시
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

      // 토큰 폴링
      const tokens = await this.pollForTokens(deviceCode.device_code, deviceCode.interval);
      
      if (tokens) {
        await this.saveTokens(tokens);
        vscode.window.showInformationMessage('TeamSync 로그인 성공!');
        
        // 인증 상태 컨텍스트 설정
        await vscode.commands.executeCommand('setContext', 'teamsync.authenticated', true);
        
        console.log('로그인 성공');
        return true;
      }

      return false;
    } catch (error) {
      console.error('로그인 실패:', error);
      vscode.window.showErrorMessage(`로그인 실패: ${error instanceof Error ? error.message : '알 수 없는 오류'}`);
      return false;
    }
  }

  async logout(): Promise<void> {
    try {
      // 로컬 토큰 삭제
      await this.clearTokens();
      
      // 인증 상태 컨텍스트 해제
      await vscode.commands.executeCommand('setContext', 'teamsync.authenticated', false);
      
      vscode.window.showInformationMessage('로그아웃되었습니다.');
      console.log('로그아웃 완료');
    } catch (error) {
      console.error('로그아웃 실패:', error);
      vscode.window.showErrorMessage('로그아웃 중 오류가 발생했습니다.');
    }
  }

  async isAuthenticated(): Promise<boolean> {
    const tokens = await this.getTokens();
    return tokens !== null && tokens.expiresAt > Date.now();
  }

  async getAccessToken(): Promise<string | null> {
    const tokens = await this.getTokens();
    if (!tokens) return null;
    
    if (tokens.expiresAt <= Date.now()) {
      // 토큰이 만료됨
      return null;
    }
    
    return tokens.accessToken;
  }

  private async requestDeviceCode(): Promise<DeviceCodeResponse> {
    const response = await fetch(`${this.API_BASE_URL}/auth/device`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        client_id: 'vscode-extension'
      })
    });

    if (!response.ok) {
      throw new Error('Device code 요청 실패');
    }

    return response.json() as Promise<DeviceCodeResponse>;
  }

  private async pollForTokens(deviceCode: string, interval: number): Promise<AuthTokens | null> {
    const maxAttempts = 60; // 5분 (5초 * 60)
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
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              grant_type: 'device_code',
              device_code: deviceCode
            })
          });

          if (response.ok) {
            const tokens = await response.json() as any;
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
          console.error('토큰 폴링 오류:', error);
          setTimeout(poll, interval * 1000);
        }
      };

      poll();
    });
  }

  private async saveTokens(tokens: AuthTokens): Promise<void> {
    await this.context.secrets.store('teamsync.tokens', JSON.stringify(tokens));
  }

  private async getTokens(): Promise<AuthTokens | null> {
    const stored = await this.context.secrets.get('teamsync.tokens');
    if (stored) {
      return JSON.parse(stored);
    }
    return null;
  }

  private async clearTokens(): Promise<void> {
    await this.context.secrets.delete('teamsync.tokens');
  }
}

// SyncEngine class
class SyncEngine {
  private context: vscode.ExtensionContext;
  private authProvider: AuthProvider;
  private readonly API_BASE_URL = 'http://localhost:3001';

  constructor(context: vscode.ExtensionContext, authProvider: AuthProvider) {
    this.context = context;
    this.authProvider = authProvider;
  }

  async syncToRemote(): Promise<{ success: boolean; message: string }> {
    try {
      const accessToken = await this.authProvider.getAccessToken();
      if (!accessToken) {
        return { success: false, message: '로그인이 필요합니다.' };
      }

      // 현재 설정 수집
      const configuration = await this.collectCurrentConfiguration();
      
      // 팀 ID 가져오기
      const teamId = this.context.globalState.get<string>('teamsync.selectedTeam') || 'team-1';

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
        const error = await response.json() as any;
        return { success: false, message: error.message || '동기화 실패' };
      }

      console.log('원격 동기화 완료');
      return { success: true, message: '설정이 성공적으로 동기화되었습니다.' };

    } catch (error) {
      console.error('동기화 실패:', error);
      return { success: false, message: '동기화 중 오류가 발생했습니다.' };
    }
  }

  async syncFromRemote(): Promise<{ success: boolean; message: string }> {
    try {
      const accessToken = await this.authProvider.getAccessToken();
      if (!accessToken) {
        return { success: false, message: '로그인이 필요합니다.' };
      }

      const teamId = this.context.globalState.get<string>('teamsync.selectedTeam') || 'team-1';

      // 원격 설정 가져오기
      const response = await fetch(`${this.API_BASE_URL}/api/v1/configurations/teams/${teamId}/latest`, {
        headers: {
          'Authorization': `Bearer ${accessToken}`
        }
      });

      if (!response.ok) {
        const error = await response.json() as any;
        return { success: false, message: error.message || '설정 가져오기 실패' };
      }

      const remoteConfig = await response.json() as any;
      
      // 로컬에 적용
      await this.applyConfiguration(remoteConfig.configuration);
      
      console.log('원격 설정 적용 완료');
      return { success: true, message: '원격 설정이 성공적으로 적용되었습니다.' };

    } catch (error) {
      console.error('원격 동기화 실패:', error);
      return { success: false, message: '원격 동기화 중 오류가 발생했습니다.' };
    }
  }

  private async collectCurrentConfiguration(): Promise<any> {
    const workspaceConfig = vscode.workspace.getConfiguration();
    
    return {
      settings: {
        'editor.fontSize': workspaceConfig.get('editor.fontSize'),
        'editor.tabSize': workspaceConfig.get('editor.tabSize'),
        'editor.insertSpaces': workspaceConfig.get('editor.insertSpaces'),
        'files.autoSave': workspaceConfig.get('files.autoSave'),
      },
      extensions: [], // TODO: 설치된 확장 목록 수집
      keybindings: [],
      snippets: {}
    };
  }

  private async applyConfiguration(config: any): Promise<void> {
    const workspaceConfig = vscode.workspace.getConfiguration();

    // 설정 적용
    if (config.settings) {
      for (const [key, value] of Object.entries(config.settings)) {
        await workspaceConfig.update(key, value, vscode.ConfigurationTarget.Global);
      }
    }

    vscode.window.showInformationMessage('설정이 적용되었습니다.');
  }
}

// 팀 목록 가져오기
async function fetchUserTeams(authProvider: AuthProvider): Promise<Team[]> {
  const accessToken = await authProvider.getAccessToken();
  if (!accessToken) {
    throw new Error('Authentication required');
  }

  const response = await fetch('http://localhost:3001/api/v1/teams', {
    headers: {
      'Authorization': `Bearer ${accessToken}`
    }
  });

  if (!response.ok) {
    throw new Error('Failed to fetch teams');
  }

  return response.json() as Promise<Team[]>;
}

// 명령어 등록
function registerCommands(
  context: vscode.ExtensionContext,
  authProvider: AuthProvider,
  syncEngine: SyncEngine
): void {
  
  // 로그인 명령어
  const loginCommand = vscode.commands.registerCommand('teamsync.login', async () => {
    const success = await authProvider.login();
    if (success) {
      vscode.commands.executeCommand('teamsync.updateStatusBar');
    }
  });

  // 로그아웃 명령어
  const logoutCommand = vscode.commands.registerCommand('teamsync.logout', async () => {
    await authProvider.logout();
    vscode.commands.executeCommand('teamsync.updateStatusBar');
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
      console.error('팀 선택 실패:', error);
      vscode.window.showErrorMessage('팀 목록을 가져오는데 실패했습니다.');
    }
  });

  // 원격으로 동기화 명령어
  const syncToRemoteCommand = vscode.commands.registerCommand('teamsync.syncToRemote', async () => {
    const isAuthenticated = await authProvider.isAuthenticated();
    if (!isAuthenticated) {
      vscode.window.showWarningMessage('먼저 로그인해주세요.');
      return;
    }

    vscode.window.withProgress({
      location: vscode.ProgressLocation.Notification,
      title: '설정을 원격으로 동기화 중...',
      cancellable: false
    }, async (progress) => {
      const result = await syncEngine.syncToRemote();
      
      if (result.success) {
        vscode.window.showInformationMessage(result.message);
      } else {
        vscode.window.showErrorMessage(result.message);
      }
    });
  });

  // 원격에서 동기화 명령어
  const syncFromRemoteCommand = vscode.commands.registerCommand('teamsync.syncFromRemote', async () => {
    const isAuthenticated = await authProvider.isAuthenticated();
    if (!isAuthenticated) {
      vscode.window.showWarningMessage('먼저 로그인해주세요.');
      return;
    }

    vscode.window.withProgress({
      location: vscode.ProgressLocation.Notification,
      title: '원격에서 설정 가져오는 중...',
      cancellable: false
    }, async (progress) => {
      const result = await syncEngine.syncFromRemote();
      
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
    logoutCommand,
    selectTeamCommand,
    syncToRemoteCommand,
    syncFromRemoteCommand
  );
}

// Extension 활성화
export async function activate(context: vscode.ExtensionContext) {
  console.log('TeamSync Pro Extension is now active!');

  try {
    // 핵심 서비스 초기화
    const authProvider = new AuthProvider(context);
    const syncEngine = new SyncEngine(context, authProvider);

    // 명령어 등록
    registerCommands(context, authProvider, syncEngine);

    // 인증 상태 확인
    if (await authProvider.isAuthenticated()) {
      await vscode.commands.executeCommand('setContext', 'teamsync.authenticated', true);
    }

    console.log('TeamSync Pro 초기화 완료');
    vscode.window.showInformationMessage('TeamSync Pro가 활성화되었습니다!');
  } catch (error) {
    console.error('TeamSync Pro 초기화 실패:', error);
    vscode.window.showErrorMessage('TeamSync Pro 초기화에 실패했습니다.');
  }
}

// Extension 비활성화
export function deactivate() {
  console.log('TeamSync Pro Extension is deactivated');
}
