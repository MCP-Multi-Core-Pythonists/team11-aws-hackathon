import simpleGit, { SimpleGit } from 'simple-git';
import * as path from 'path';
import * as fs from 'fs';
import * as vscode from 'vscode';
import * as os from 'os';

export class GitService {
  private git: SimpleGit;
  private localConfigPath: string;

  constructor() {
    const workspaceFolder = vscode.workspace.workspaceFolders?.[0];
    if (workspaceFolder) {
      this.localConfigPath = path.join(workspaceFolder.uri.fsPath, '.teamsync');
    } else {
      // 워크스페이스가 없으면 임시 디렉토리 사용
      this.localConfigPath = path.join(os.tmpdir(), 'teamsync-config');
    }
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

  private async cloneConfig(repositoryUrl: string): Promise<string> {
    vscode.window.showInformationMessage('팀 설정을 다운로드 중...');
    
    // 부모 디렉토리 생성
    const parentDir = path.dirname(this.localConfigPath);
    if (!fs.existsSync(parentDir)) {
      fs.mkdirSync(parentDir, { recursive: true });
    }
    
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
}
