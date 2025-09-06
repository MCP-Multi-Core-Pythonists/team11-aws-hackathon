import * as vscode from 'vscode';
import { CursorSettingsManager } from './cursorSettings';
import { ApiService } from './apiService';

let apiService: ApiService;
let settingsManager: CursorSettingsManager;

export function activate(context: vscode.ExtensionContext) {
  apiService = new ApiService();
  settingsManager = new CursorSettingsManager();

  // Login 명령어
  const loginCommand = vscode.commands.registerCommand('teamsync.login', async () => {
    try {
      const response = await apiService.login();
      vscode.window.showInformationMessage(`Logged in as ${response.user.email}`);
    } catch (error) {
      vscode.window.showErrorMessage(`Login failed: ${error}`);
    }
  });

  // Push Settings 명령어
  const pushCommand = vscode.commands.registerCommand('teamsync.pushSettings', async () => {
    try {
      // is_public 선택
      const isPublic = await vscode.window.showQuickPick(
        [
          { label: 'Private', value: false },
          { label: 'Public', value: true }
        ],
        { placeHolder: 'Make settings public?' }
      );

      if (isPublic === undefined) {
        return; // 사용자가 취소함
      }

      // 설정 파일들을 tmp로 복사
      const tmpDir = await settingsManager.copySettingsToTemp();
      vscode.window.showInformationMessage(`Settings copied to: ${tmpDir}`);

      // 설정 읽기
      const settings = await settingsManager.readAllSettings();
      
      // 서버로 push
      const result = await apiService.pushSettings(settings, isPublic.value);
      vscode.window.showInformationMessage(`Settings pushed: ${result.message}`);
    } catch (error) {
      vscode.window.showErrorMessage(`Failed to push settings: ${error}`);
    }
  });

  // Pull Settings 명령어
  const pullCommand = vscode.commands.registerCommand('teamsync.pullSettings', async () => {
    try {
      // 서버에서 설정 pull
      const settings = await apiService.pullSettings();
      
      // 로컬에 적용
      await settingsManager.writeSettings(settings);
      
      vscode.window.showInformationMessage('Settings pulled and applied successfully');
    } catch (error) {
      vscode.window.showErrorMessage(`Failed to pull settings: ${error}`);
    }
  });

  context.subscriptions.push(loginCommand, pushCommand, pullCommand);
}

export function deactivate() {}
