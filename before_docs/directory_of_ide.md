# IDE 설정 파일 위치 가이드

## 📁 VS Code 설정 파일 위치

### macOS
```bash
# 사용자 설정 (전역)
~/Library/Application Support/Code/User/settings.json
~/Library/Application Support/Code/User/keybindings.json
~/Library/Application Support/Code/User/snippets/

# 확장 설치 위치
~/.vscode/extensions/

# 워크스페이스 설정 (프로젝트별)
프로젝트폴더/.vscode/settings.json
프로젝트폴더/.vscode/extensions.json
프로젝트폴더/.vscode/launch.json
프로젝트폴더/.vscode/tasks.json
프로젝트폴더/.vscode/keybindings.json

# 기타 설정
~/Library/Application Support/Code/User/globalStorage/
~/Library/Application Support/Code/User/workspaceStorage/
~/Library/Application Support/Code/User/History/
```

### Windows
```bash
# 사용자 설정 (전역)
%APPDATA%\Code\User\settings.json
%APPDATA%\Code\User\keybindings.json
%APPDATA%\Code\User\snippets\

# 확장 설치 위치
%USERPROFILE%\.vscode\extensions\

# 워크스페이스 설정 (프로젝트별)
프로젝트폴더\.vscode\settings.json
프로젝트폴더\.vscode\extensions.json
프로젝트폴더\.vscode\launch.json
프로젝트폴더\.vscode\tasks.json
프로젝트폴더\.vscode\keybindings.json

# 기타 설정
%APPDATA%\Code\User\globalStorage\
%APPDATA%\Code\User\workspaceStorage\
%APPDATA%\Code\User\History\
```

## 📁 Cursor 설정 파일 위치

### macOS
```bash
# 사용자 설정 (전역)
~/Library/Application Support/Cursor/User/settings.json
~/Library/Application Support/Cursor/User/keybindings.json
~/Library/Application Support/Cursor/User/snippets/

# 확장 설치 위치
~/.cursor/extensions/
~/.cursor/extensions/extensions.json

# 워크스페이스 설정 (프로젝트별)
프로젝트폴더/.vscode/settings.json
프로젝트폴더/.vscode/extensions.json
프로젝트폴더/.vscode/launch.json
프로젝트폴더/.vscode/tasks.json

# 기타 설정
~/Library/Application Support/Cursor/User/globalStorage/
~/Library/Application Support/Cursor/User/workspaceStorage/
~/Library/Application Support/Cursor/User/History/
~/.cursor/argv.json
~/.cursor/ide_state.json
```

### Windows
```bash
# 사용자 설정 (전역)
%APPDATA%\Cursor\User\settings.json
%APPDATA%\Cursor\User\keybindings.json
%APPDATA%\Cursor\User\snippets\

# 확장 설치 위치
%USERPROFILE%\.cursor\extensions\
%USERPROFILE%\.cursor\extensions\extensions.json

# 워크스페이스 설정 (프로젝트별)
프로젝트폴더\.vscode\settings.json
프로젝트폴더\.vscode\extensions.json
프로젝트폴더\.vscode\launch.json
프로젝트폴더\.vscode\tasks.json

# 기타 설정
%APPDATA%\Cursor\User\globalStorage\
%APPDATA%\Cursor\User\workspaceStorage\
%APPDATA%\Cursor\User\History\
%USERPROFILE%\.cursor\argv.json
%USERPROFILE%\.cursor\ide_state.json
```

## 📁 Cursor Nightly 설정 파일 위치

### macOS
```bash
# 사용자 설정 (전역)
~/Library/Application Support/Cursor Nightly/User/settings.json
~/Library/Application Support/Cursor Nightly/User/keybindings.json
~/Library/Application Support/Cursor Nightly/User/snippets/

# 확장 설치 위치
~/.cursor-nightly/extensions/
~/.cursor-nightly/extensions/extensions.json

# 워크스페이스 설정 (프로젝트별)
프로젝트폴더/.vscode/settings.json (VS Code와 공유)
```

### Windows
```bash
# 사용자 설정 (전역)
%APPDATA%\Cursor Nightly\User\settings.json
%APPDATA%\Cursor Nightly\User\keybindings.json
%APPDATA%\Cursor Nightly\User\snippets\

# 확장 설치 위치
%USERPROFILE%\.cursor-nightly\extensions\
%USERPROFILE%\.cursor-nightly\extensions\extensions.json

# 워크스페이스 설정 (프로젝트별)
프로젝트폴더\.vscode\settings.json (VS Code와 공유)
```

## 🔧 SyncHub에서 관리할 주요 파일들

### 1. 사용자 설정 (User Settings)
| 파일 | 설명 | VS Code | Cursor | Cursor Nightly |
|------|------|---------|--------|----------------|
| `settings.json` | 에디터 설정 | ✅ | ✅ | ✅ |
| `keybindings.json` | 키바인딩 설정 | ✅ | ✅ | ✅ |
| `snippets/` | 코드 스니펫 | ✅ | ✅ | ✅ |

### 2. 확장 관리 (Extensions)
| 파일 | 설명 | VS Code | Cursor | Cursor Nightly |
|------|------|---------|--------|----------------|
| `extensions.json` | 설치된 확장 목록 | ❌ | ✅ | ✅ |
| `extensions/` | 확장 설치 디렉토리 | ✅ | ✅ | ✅ |

### 3. 워크스페이스 설정 (Workspace Settings)
| 파일 | 설명 | 모든 에디터 공통 |
|------|------|------------------|
| `.vscode/settings.json` | 프로젝트별 설정 | ✅ |
| `.vscode/extensions.json` | 권장 확장 목록 | ✅ |
| `.vscode/launch.json` | 디버그 설정 | ✅ |
| `.vscode/tasks.json` | 태스크 설정 | ✅ |

## 📊 에디터별 특징 비교

### VS Code
- **장점**: 가장 표준적인 구조, 광범위한 문서화
- **단점**: 확장 목록을 JSON으로 직접 관리하지 않음
- **호환성**: 모든 VS Code 호환 에디터의 기준

### Cursor
- **장점**: VS Code와 95% 호환, 확장 목록 JSON 제공
- **특징**: AI 기능 관련 추가 설정 존재
- **호환성**: VS Code 확장 완전 호환

### Cursor Nightly
- **장점**: 최신 기능 테스트 가능
- **단점**: 불안정할 수 있음
- **특징**: 별도 설정 디렉토리 사용

## 🛠️ SyncHub 구현 시 고려사항

### 1. 에디터 감지 로직
```typescript
const editorDetection = {
  vscode: {
    check: () => fs.existsSync('~/Library/Application Support/Code'),
    priority: 1
  },
  cursor: {
    check: () => fs.existsSync('~/Library/Application Support/Cursor'),
    priority: 2
  },
  cursorNightly: {
    check: () => fs.existsSync('~/Library/Application Support/Cursor Nightly'),
    priority: 3
  }
};
```

### 2. 설정 파일 매핑
```typescript
const configPaths = {
  macos: {
    vscode: {
      settings: '~/Library/Application Support/Code/User/settings.json',
      keybindings: '~/Library/Application Support/Code/User/keybindings.json',
      extensions: '~/.vscode/extensions/'
    },
    cursor: {
      settings: '~/Library/Application Support/Cursor/User/settings.json',
      keybindings: '~/Library/Application Support/Cursor/User/keybindings.json',
      extensions: '~/.cursor/extensions/extensions.json'
    }
  },
  windows: {
    vscode: {
      settings: '%APPDATA%\\Code\\User\\settings.json',
      keybindings: '%APPDATA%\\Code\\User\\keybindings.json',
      extensions: '%USERPROFILE%\\.vscode\\extensions\\'
    },
    cursor: {
      settings: '%APPDATA%\\Cursor\\User\\settings.json',
      keybindings: '%APPDATA%\\Cursor\\User\\keybindings.json',
      extensions: '%USERPROFILE%\\.cursor\\extensions\\extensions.json'
    }
  }
};
```

### 3. 권한 및 접근성
- **macOS**: 모든 파일 sudo 없이 읽기/쓰기 가능
- **Windows**: 사용자 프로필 내 파일들은 관리자 권한 불필요
- **워크스페이스**: 프로젝트 폴더 권한에 따라 달라짐

### 4. 백업 전략
```typescript
const backupStrategy = {
  beforeSync: [
    'settings.json',
    'keybindings.json', 
    'extensions.json'
  ],
  location: '~/.synchub/backups/{timestamp}/',
  retention: '30 days'
};
```

## 🎯 동기화 우선순위

### High Priority (필수)
1. `settings.json` - 에디터 기본 설정
2. `extensions.json` - 확장 목록 (Cursor만)
3. `.vscode/settings.json` - 프로젝트 설정

### Medium Priority (권장)
1. `keybindings.json` - 키바인딩
2. `.vscode/extensions.json` - 권장 확장
3. `snippets/` - 사용자 스니펫

### Low Priority (선택)
1. `.vscode/launch.json` - 디버그 설정
2. `.vscode/tasks.json` - 태스크 설정
3. `globalStorage/` - 확장별 전역 데이터

## 📝 주의사항

### 1. 민감 정보 필터링
- API 키, 토큰이 포함된 설정값 제외
- 로컬 경로 정보 마스킹
- 개인 식별 정보 제거

### 2. 에디터별 호환성
- VS Code → Cursor: 거의 100% 호환
- Cursor → VS Code: AI 관련 설정 제외하고 호환
- 버전별 설정 차이 고려

### 3. 플랫폼별 차이
- 경로 구분자 (/ vs \)
- 환경변수 형식 (~ vs %USERPROFILE%)
- 권한 시스템 차이

---

**문서 버전**: v1.0  
**작성일**: 2025-09-05  
**지원 플랫폼**: macOS, Windows  
**지원 에디터**: VS Code, Cursor, Cursor Nightly
