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
