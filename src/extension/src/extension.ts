import * as vscode from 'vscode';
import { ExtensionApiClient, Team, UserProfile } from './api';

// AuthProvider class
class AuthProvider {
  private context: vscode.ExtensionContext;
  public apiClient: ExtensionApiClient;

  constructor(context: vscode.ExtensionContext) {
    this.context = context;
    this.apiClient = new ExtensionApiClient(context);
  }

  async register(): Promise<boolean> {
    try {
      // Get user information
      const name = await vscode.window.showInputBox({
        prompt: '이름을 입력하세요',
        placeHolder: '홍길동'
      });

      if (!name) return false;

      const email = await vscode.window.showInputBox({
        prompt: '이메일을 입력하세요',
        placeHolder: 'user@example.com'
      });

      if (!email) return false;

      const password = await vscode.window.showInputBox({
        prompt: '비밀번호를 입력하세요',
        password: true
      });

      if (!password) return false;

      const confirmPassword = await vscode.window.showInputBox({
        prompt: '비밀번호를 다시 입력하세요',
        password: true
      });

      if (password !== confirmPassword) {
        vscode.window.showErrorMessage('비밀번호가 일치하지 않습니다.');
        return false;
      }

      // Register via API
      await this.apiClient.register(email, password, name);
      
      vscode.window.showInformationMessage(`회원가입 성공! ${name}님, 이제 로그인해주세요.`);
      
      // Auto login after registration
      const loginResult = await vscode.window.showInformationMessage(
        '바로 로그인하시겠습니까?',
        '예', '아니오'
      );
      
      if (loginResult === '예') {
        const tokens = await this.apiClient.login(email, password);
        await this.context.globalState.update('userEmail', email);
        await this.context.globalState.update('userName', name);
        vscode.window.showInformationMessage(`로그인 완료! 환영합니다, ${name}님`);
      }
      
      return true;
    } catch (error) {
      console.error('Registration failed:', error);
      vscode.window.showErrorMessage(`회원가입 실패: ${error}`);
      return false;
    }
  }

  async login(): Promise<boolean> {
    try {
      console.log('TeamSync Pro Extension is now active!');
      
      // Get credentials from user
      const email = await vscode.window.showInputBox({
        prompt: '이메일을 입력하세요',
        placeHolder: 'user@example.com'
      });

      if (!email) return false;

      const password = await vscode.window.showInputBox({
        prompt: '비밀번호를 입력하세요',
        password: true
      });

      if (!password) return false;

      // Login via API
      const tokens = await this.apiClient.login(email, password);
      
      // Store user info
      await this.context.globalState.update('userEmail', email);
      await this.context.globalState.update('userName', tokens.user?.name || 'User');
      
      vscode.window.showInformationMessage(`로그인 성공! 환영합니다, ${tokens.user?.name || email}님`);
      return true;
    } catch (error) {
      console.error('Login failed:', error);
      vscode.window.showErrorMessage(`로그인 실패: ${error}`);
      return false;
    }
  }

  async selectTeam(): Promise<Team | null> {
    try {
      const teams = await this.apiClient.getMyTeams();
      
      if (teams.length === 0) {
        vscode.window.showInformationMessage('참여한 팀이 없습니다.');
        return null;
      }

      const teamItems = teams.map(team => ({
        label: team.name,
        description: team.description,
        team: team
      }));

      const selected = await vscode.window.showQuickPick(teamItems, {
        placeHolder: '동기화할 팀을 선택하세요'
      });

      if (selected) {
        await this.context.globalState.update('selectedTeam', selected.team);
        vscode.window.showInformationMessage(`팀 선택됨: ${selected.team.name}`);
        return selected.team;
      }

      return null;
    } catch (error) {
      console.error('Team selection failed:', error);
      vscode.window.showErrorMessage(`팀 선택 실패: ${error}`);
      return null;
    }
  }

  async syncSettings(): Promise<void> {
    try {
      const config = vscode.workspace.getConfiguration();
      const settings = {
        'editor.fontSize': config.get('editor.fontSize'),
        'editor.tabSize': config.get('editor.tabSize'),
        'workbench.colorTheme': config.get('workbench.colorTheme'),
        'files.autoSave': config.get('files.autoSave')
      };

      const result = await this.apiClient.syncApply(settings);
      
      vscode.window.showInformationMessage(
        `설정 동기화 완료! ${result.applied_count}개 설정이 적용되었습니다.`
      );
    } catch (error) {
      console.error('Settings sync failed:', error);
      vscode.window.showErrorMessage(`설정 동기화 실패: ${error}`);
    }
  }

  async showBookmarks(): Promise<void> {
    try {
      const bookmarks = await this.apiClient.getBookmarks();
      
      if (bookmarks.length === 0) {
        vscode.window.showInformationMessage('북마크가 없습니다.');
        return;
      }

      const bookmarkItems = bookmarks.map(bookmark => ({
        label: bookmark.name,
        description: bookmark.description,
        detail: `Tags: ${bookmark.tags.join(', ')}`,
        bookmark: bookmark
      }));

      const selected = await vscode.window.showQuickPick(bookmarkItems, {
        placeHolder: '북마크를 선택하세요'
      });

      if (selected) {
        vscode.window.showInformationMessage(`선택된 북마크: ${selected.bookmark.name}`);
      }
    } catch (error) {
      console.error('Bookmarks loading failed:', error);
      vscode.window.showErrorMessage(`북마크 로딩 실패: ${error}`);
    }
  }
}

// Extension activation
export function activate(context: vscode.ExtensionContext) {
  console.log('TeamSync Pro Extension is now active!');
  
  const authProvider = new AuthProvider(context);

  // Register commands
  const registerCommand = vscode.commands.registerCommand('teamsync.register', async () => {
    await authProvider.register();
  });

  const loginCommand = vscode.commands.registerCommand('teamsync.login', async () => {
    await authProvider.login();
  });

  const selectTeamCommand = vscode.commands.registerCommand('teamsync.selectTeam', async () => {
    await authProvider.selectTeam();
  });

  const syncCommand = vscode.commands.registerCommand('teamsync.sync', async () => {
    await authProvider.syncSettings();
  });

  const bookmarksCommand = vscode.commands.registerCommand('teamsync.bookmarks', async () => {
    await authProvider.showBookmarks();
  });

  const statusCommand = vscode.commands.registerCommand('teamsync.status', async () => {
    try {
      const userEmail = context.globalState.get<string>('userEmail');
      const userName = context.globalState.get<string>('userName');
      const selectedTeam = context.globalState.get<Team>('selectedTeam');
      
      if (!userEmail) {
        vscode.window.showInformationMessage('로그인되지 않았습니다. 먼저 회원가입 또는 로그인해주세요.');
        return;
      }
      
      vscode.window.showInformationMessage(
        `사용자: ${userName} (${userEmail})\n` +
        `선택된 팀: ${selectedTeam ? selectedTeam.name : '없음'}`
      );
    } catch (error) {
      vscode.window.showErrorMessage('상태 확인 실패');
    }
  });

  const logoutCommand = vscode.commands.registerCommand('teamsync.logout', async () => {
    await context.globalState.update('authTokens', undefined);
    await context.globalState.update('userEmail', undefined);
    await context.globalState.update('userName', undefined);
    await context.globalState.update('selectedTeam', undefined);
    vscode.window.showInformationMessage('로그아웃되었습니다.');
  });

  // Add commands to subscriptions
  context.subscriptions.push(
    registerCommand,
    loginCommand,
    selectTeamCommand,
    syncCommand,
    bookmarksCommand,
    statusCommand,
    logoutCommand
  );

  // Status bar item
  const statusBarItem = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Right, 100);
  statusBarItem.text = "$(sync) TeamSync";
  statusBarItem.command = 'teamsync.status';
  statusBarItem.tooltip = 'TeamSync Pro 상태 확인';
  statusBarItem.show();
  
  context.subscriptions.push(statusBarItem);
}

export function deactivate() {
  console.log('TeamSync Pro Extension is now deactivated!');
}
