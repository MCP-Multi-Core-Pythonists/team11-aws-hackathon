import * as vscode from 'vscode';

export class StatusBarManager {
    private statusBarItem: vscode.StatusBarItem;
    private isAuthenticated: boolean = false;
    private currentTeam: string | null = null;
    private syncStatus: 'idle' | 'syncing' | 'error' = 'idle';

    constructor() {
        this.statusBarItem = vscode.window.createStatusBarItem(
            vscode.StatusBarAlignment.Right,
            100
        );
    }

    initialize(): void {
        this.statusBarItem.command = 'teamsync.showPanel';
        this.statusBarItem.show();
        this.updateDisplay();
    }

    setAuthenticated(authenticated: boolean): void {
        this.isAuthenticated = authenticated;
        this.updateDisplay();
    }

    setCurrentTeam(teamName: string | null): void {
        this.currentTeam = teamName;
        this.updateDisplay();
    }

    setSyncStatus(status: 'idle' | 'syncing' | 'error'): void {
        this.syncStatus = status;
        this.updateDisplay();
    }

    private updateDisplay(): void {
        let text = '$(sync)';
        let tooltip = 'TeamSync Pro';
        let color: string | undefined;

        if (!this.isAuthenticated) {
            text += ' 로그인 필요';
            tooltip = 'TeamSync Pro - 로그인이 필요합니다';
            color = '#FFA500'; // 주황색
        } else if (this.syncStatus === 'syncing') {
            text += ' 동기화 중...';
            tooltip = 'TeamSync Pro - 동기화 중';
            color = '#00BFFF'; // 파란색
        } else if (this.syncStatus === 'error') {
            text += ' 오류';
            tooltip = 'TeamSync Pro - 동기화 오류';
            color = '#FF6B6B'; // 빨간색
        } else if (this.currentTeam) {
            text += ` ${this.currentTeam}`;
            tooltip = `TeamSync Pro - 현재 팀: ${this.currentTeam}`;
            color = '#4CAF50'; // 초록색
        } else {
            text += ' 팀 선택';
            tooltip = 'TeamSync Pro - 팀을 선택해주세요';
            color = '#FFA500'; // 주황색
        }

        this.statusBarItem.text = text;
        this.statusBarItem.tooltip = tooltip;
        this.statusBarItem.color = color;
    }

    dispose(): void {
        this.statusBarItem.dispose();
    }
}
