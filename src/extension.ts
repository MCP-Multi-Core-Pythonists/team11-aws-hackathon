import * as vscode from 'vscode';
import { Logger } from './utils/logger';
import { StatusBarManager } from './ui/statusBar';

export function activate(context: vscode.ExtensionContext) {
    console.log('TeamSync Pro 확장 활성화 시작');
    
    try {
        // Logger 초기화
        Logger.initialize();
        Logger.info('TeamSync Pro 확장이 활성화되었습니다');

        // 상태바 관리자 초기화
        const statusBarManager = new StatusBarManager();
        statusBarManager.updateStatus('not-synced');

        // 테스트 명령어
        const testCommand = vscode.commands.registerCommand('teamsync.test', () => {
            Logger.info('테스트 명령어 실행됨');
            statusBarManager.updateStatus('syncing');
            
            setTimeout(() => {
                statusBarManager.updateStatus('synced');
                vscode.window.showInformationMessage('TeamSync Pro 테스트 성공!');
            }, 2000);
        });

        // 상태 명령어
        const statusCommand = vscode.commands.registerCommand('teamsync.showStatus', () => {
            Logger.info('상태 명령어 실행됨');
            const message = `TeamSync Pro 상태:
- 마지막 동기화: 없음
- 설정: 0개
- 확장: 0개
- 프롬프트: 0개`;
            vscode.window.showInformationMessage(message);
        });

        // 로그 표시 명령어
        const logCommand = vscode.commands.registerCommand('teamsync.showLogs', () => {
            Logger.show();
        });

        // 명령어 등록
        context.subscriptions.push(testCommand, statusCommand, logCommand, statusBarManager);
        
        Logger.info('모든 명령어 등록 완료');
        vscode.window.showInformationMessage('TeamSync Pro가 활성화되었습니다!');
        
    } catch (error) {
        console.error('TeamSync Pro 활성화 실패:', error);
        vscode.window.showErrorMessage(`TeamSync Pro 활성화 실패: ${error}`);
    }
}

export function deactivate() {
    Logger.info('TeamSync Pro 확장이 비활성화되었습니다');
}
