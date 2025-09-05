import { PromptLoader } from './promptLoader';
import { PromptPalette } from '../ui/promptPalette';
import { TeamConfig } from '../types/config';
import { PromptCategory } from '../types/prompt';
import * as vscode from 'vscode';

export class PromptSyncService {
  private promptLoader: PromptLoader;
  private promptPalette: PromptPalette;
  private storedCategories: PromptCategory[] = [];

  constructor() {
    this.promptLoader = new PromptLoader();
    this.promptPalette = new PromptPalette();
  }

  async syncPrompts(configDir: string, teamConfig: TeamConfig): Promise<void> {
    try {
      const prompts = await this.promptLoader.loadPrompts(configDir, teamConfig);
      const categories = this.promptLoader.groupByCategory(prompts);
      
      this.storedCategories = categories;
      
      vscode.window.showInformationMessage(`${prompts.length}개의 프롬프트를 로드했습니다`);
    } catch (error) {
      throw new Error(`프롬프트 동기화 실패: ${error}`);
    }
  }

  async showPromptPalette(): Promise<void> {
    if (this.storedCategories.length === 0) {
      vscode.window.showWarningMessage('로드된 프롬프트가 없습니다. 먼저 팀 설정을 동기화하세요.');
      return;
    }

    await this.promptPalette.showPromptPalette(this.storedCategories);
  }
}
