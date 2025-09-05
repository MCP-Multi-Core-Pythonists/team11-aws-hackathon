# 001 - VS Code 확장 프로젝트 스캐폴딩

## 📋 개발 목표
VS Code 확장 프로젝트의 기본 구조를 생성하고 개발 환경을 설정합니다.

## 🎯 구현 범위
- VS Code Extension 프로젝트 초기화
- 기본 파일 구조 설정
- package.json 설정
- 기본 명령어 등록

## 🛠️ 기술 스택
- Node.js
- TypeScript
- VS Code Extension API
- Yeoman Generator

## 📝 구현 단계

### 1단계: 개발 환경 준비
```bash
# 필요한 도구 설치
npm install -g yo generator-code

# VS Code 확장 프로젝트 생성
yo code
```

### 2단계: 프로젝트 구조 설정
```
teamsync-pro/
├── src/
│   ├── extension.ts          # 메인 확장 파일
│   ├── commands/             # 명령어 모듈
│   ├── providers/            # 데이터 제공자
│   └── utils/                # 유틸리티 함수
├── package.json              # 확장 메타데이터
├── tsconfig.json            # TypeScript 설정
└── README.md                # 프로젝트 문서
```

### 3단계: package.json 기본 설정
```json
{
  "name": "teamsync-pro",
  "displayName": "TeamSync Pro",
  "description": "팀 개발 환경 표준화 솔루션",
  "version": "0.0.1",
  "engines": {
    "vscode": "^1.74.0"
  },
  "categories": ["Other"],
  "activationEvents": [
    "onCommand:teamsync.syncSettings"
  ],
  "main": "./out/extension.js",
  "contributes": {
    "commands": [
      {
        "command": "teamsync.syncSettings",
        "title": "Sync Team Settings"
      }
    ]
  }
}
```

### 4단계: 기본 확장 로직 구현
```typescript
// src/extension.ts
import * as vscode from 'vscode';

export function activate(context: vscode.ExtensionContext) {
    const disposable = vscode.commands.registerCommand('teamsync.syncSettings', () => {
        vscode.window.showInformationMessage('TeamSync Pro 활성화됨!');
    });

    context.subscriptions.push(disposable);
}

export function deactivate() {}
```

## ✅ 완료 기준
- [ ] VS Code 확장 프로젝트 생성 완료
- [ ] 기본 명령어 등록 및 실행 가능
- [ ] TypeScript 컴파일 정상 동작
- [ ] F5로 디버그 모드 실행 가능

## 🔗 다음 단계
002-config-structure-design.md - 설정 파일 구조 설계

## 📚 참고 자료
- [VS Code Extension API](https://code.visualstudio.com/api)
- [Extension Guidelines](https://code.visualstudio.com/api/references/extension-guidelines)
