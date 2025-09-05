# 002 - 설정 파일 구조 설계

## 📋 개발 목표
팀 설정을 관리하기 위한 YAML 기반 설정 파일 구조를 설계하고 파싱 로직을 구현합니다.

## 🎯 구현 범위
- config.yaml 스키마 정의
- 설정 파일 파싱 로직
- 설정 검증 및 기본값 처리
- 타입 정의 (TypeScript interfaces)

## 🛠️ 기술 스택
- YAML 파싱 (js-yaml)
- JSON Schema 검증
- TypeScript 타입 시스템

## 📝 구현 단계

### 1단계: 설정 파일 스키마 정의
```yaml
# config.yaml
version: "1.0"
organization:
  name: "TeamSync Pro"
  repository: "https://github.com/org/teamsync-config"

settings:
  vscode:
    settings: "./settings/settings.json"
    keybindings: "./settings/keybindings.json"
    extensions: "./settings/extensions.json"
  
  code_quality:
    editorconfig: "./.editorconfig"
    prettier: "./settings/.prettierrc"
    eslint: "./settings/.eslintrc.json"

prompts:
  - name: "code-review"
    file: "./prompts/review-prompt.md"
    category: "development"
  - name: "refactoring"
    file: "./prompts/refactor-prompt.md"
    category: "development"

policies:
  sync_mode: "recommended"  # recommended | force
  auto_update: true
  backup_local: true
```

### 2단계: TypeScript 타입 정의
```typescript
// src/types/config.ts
export interface TeamConfig {
  version: string;
  organization: {
    name: string;
    repository: string;
  };
  settings: {
    vscode: {
      settings?: string;
      keybindings?: string;
      extensions?: string;
    };
    code_quality?: {
      editorconfig?: string;
      prettier?: string;
      eslint?: string;
    };
  };
  prompts: PromptConfig[];
  policies: {
    sync_mode: 'recommended' | 'force';
    auto_update: boolean;
    backup_local: boolean;
  };
}

export interface PromptConfig {
  name: string;
  file: string;
  category: string;
}
```

### 3단계: 설정 파일 파싱 로직
```typescript
// src/utils/configParser.ts
import * as yaml from 'js-yaml';
import * as fs from 'fs';
import { TeamConfig } from '../types/config';

export class ConfigParser {
  static async parseConfig(configPath: string): Promise<TeamConfig> {
    try {
      const fileContent = fs.readFileSync(configPath, 'utf8');
      const config = yaml.load(fileContent) as TeamConfig;
      
      // 기본값 설정
      return this.applyDefaults(config);
    } catch (error) {
      throw new Error(`설정 파일 파싱 실패: ${error}`);
    }
  }

  private static applyDefaults(config: Partial<TeamConfig>): TeamConfig {
    return {
      version: config.version || "1.0",
      organization: config.organization || { name: "", repository: "" },
      settings: {
        vscode: config.settings?.vscode || {},
        code_quality: config.settings?.code_quality || {}
      },
      prompts: config.prompts || [],
      policies: {
        sync_mode: config.policies?.sync_mode || 'recommended',
        auto_update: config.policies?.auto_update ?? true,
        backup_local: config.policies?.backup_local ?? true
      }
    };
  }
}
```

### 4단계: 설정 검증 로직
```typescript
// src/utils/configValidator.ts
import { TeamConfig } from '../types/config';

export class ConfigValidator {
  static validate(config: TeamConfig): string[] {
    const errors: string[] = [];

    if (!config.version) {
      errors.push('version 필드가 필요합니다');
    }

    if (!config.organization?.name) {
      errors.push('organization.name 필드가 필요합니다');
    }

    if (!config.organization?.repository) {
      errors.push('organization.repository 필드가 필요합니다');
    }

    return errors;
  }
}
```

## ✅ 완료 기준
- [ ] config.yaml 스키마 정의 완료
- [ ] TypeScript 타입 정의 완료
- [ ] 설정 파일 파싱 로직 구현
- [ ] 기본값 처리 및 검증 로직 구현

## 🔗 다음 단계
003-git-repository-integration.md - Git 저장소 연동 기본 로직

## 📚 참고 자료
- [js-yaml Documentation](https://github.com/nodeca/js-yaml)
- [JSON Schema](https://json-schema.org/)
