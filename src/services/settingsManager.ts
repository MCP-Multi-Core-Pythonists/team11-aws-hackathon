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
    throw new Error('워크스페이스를 찾을 수 없습니다. VS Code에서 폴더를 열어주세요.');
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
    
    if (!fs.existsSync(vscodePath)) {
      fs.mkdirSync(vscodePath, { recursive: true });
    }
    
    fs.writeFileSync(this.settingsPath, JSON.stringify(settings, null, 2));
    vscode.window.showInformationMessage('설정이 적용되었습니다');
  }

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
}
