import * as fs from 'fs';
import * as path from 'path';
import { PromptTemplate, PromptCategory } from '../types/prompt';
import { TeamConfig } from '../types/config';

export class PromptLoader {
  async loadPrompts(configDir: string, teamConfig: TeamConfig): Promise<PromptTemplate[]> {
    const prompts: PromptTemplate[] = [];

    for (const promptConfig of teamConfig.prompts) {
      try {
        const promptPath = path.join(configDir, promptConfig.file);
        const content = fs.readFileSync(promptPath, 'utf8');
        
        const prompt: PromptTemplate = {
          id: promptConfig.name,
          name: this.extractTitle(content) || promptConfig.name,
          description: this.extractDescription(content) || '',
          category: promptConfig.category,
          content: content,
          tags: this.extractTags(content)
        };

        prompts.push(prompt);
      } catch (error) {
        console.error(`프롬프트 로드 실패: ${promptConfig.file}`, error);
      }
    }

    return prompts;
  }

  private extractTitle(content: string): string | null {
    const titleMatch = content.match(/^#\s+(.+)$/m);
    return titleMatch ? titleMatch[1] : null;
  }

  private extractDescription(content: string): string {
    const descMatch = content.match(/^##\s+(.+)$/m);
    return descMatch ? descMatch[1] : '';
  }

  private extractTags(content: string): string[] {
    const tagMatch = content.match(/tags:\s*\[([^\]]+)\]/i);
    if (tagMatch) {
      return tagMatch[1].split(',').map(tag => tag.trim());
    }
    return [];
  }

  groupByCategory(prompts: PromptTemplate[]): PromptCategory[] {
    const categories = new Map<string, PromptTemplate[]>();

    prompts.forEach(prompt => {
      if (!categories.has(prompt.category)) {
        categories.set(prompt.category, []);
      }
      categories.get(prompt.category)!.push(prompt);
    });

    return Array.from(categories.entries()).map(([categoryId, prompts]) => ({
      id: categoryId,
      name: this.formatCategoryName(categoryId),
      description: `${prompts.length}개의 프롬프트`,
      prompts
    }));
  }

  private formatCategoryName(categoryId: string): string {
    const names: { [key: string]: string } = {
      'development': '개발',
      'review': '코드 리뷰',
      'testing': '테스트',
      'documentation': '문서화',
      'deployment': '배포'
    };
    return names[categoryId] || categoryId;
  }
}
