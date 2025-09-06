# TeamSync VSCode Extension - 아키텍처 문서

## 📋 프로젝트 개요

TeamSync는 Cursor 설정을 팀과 공유할 수 있는 VSCode Extension입니다. 사용자는 로그인 후 자신의 Cursor 설정을 서버에 업로드하거나 다른 사용자의 설정을 다운로드하여 적용할 수 있습니다.

## 🏗️ 전체 아키텍처

```
┌─────────────────────────────────────────────────────────────────┐
│                    TeamSync Extension                           │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  │
│  │   extension.ts  │  │  apiService.ts  │  │cursorSettings.ts│  │
│  │                 │  │                 │  │                 │  │
│  │ • 명령어 등록      │  │ • 인증 처리       │  │ • 파일 읽기/쓰기    │  │
│  │ • UI 상호작용     │  │ • API 통신       │  │ • 설정 관리        │  │
│  │ • 워크플로우       │  │ • 토큰 관리       │  │ • 임시 파일       │  │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                         AWS 백엔드                                │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐           ┌─────────────────┐              │
│  │   Cognito       │           │   API Gateway   │              │
│  │                 │           │                 │              │
│  │ • Google OAuth  │◄──────────┤ • REST API      │              │
│  │ • 사용자 인증      │           │ • 인증/인가       │              │
│  │ • 토큰 발급       │           │ • 요청 라우팅      │              │
│  └─────────────────┘           └─────────────────┘              │
│                                         │                       │
│                                         ▼                       │
│                               ┌─────────────────┐               │
│                               │     Lambda      │               │
│                               │                 │               │
│                               │ • 설정 저장       │               │
│                               │ • 설정 조회       │               │
│                               │ • 비즈니스 로직    │               │
│                               └─────────────────┘               │
│                                         │                       │
│                                         ▼                       │
│                               ┌─────────────────┐               │
│                               │    DynamoDB     │               │
│                               │                 │               │
│                               │ • 설정 데이터      │              │
│                               │ • 사용자 정보      │              │
│                               │ • 메타데이터       │              │
│                               └─────────────────┘              │
└─────────────────────────────────────────────────────────────────┘
```

## 📁 파일 구조

```
TeamSync/
├── src/
│   ├── extension.ts          # 메인 확장 프로그램 진입점
│   ├── apiService.ts         # API 통신 및 인증 서비스
│   └── cursorSettings.ts     # Cursor 설정 파일 관리
├── out/                      # 컴파일된 JavaScript 파일
├── package.json              # 확장 프로그램 매니페스트
├── tsconfig.json            # TypeScript 설정
└── .vscode/
    └── launch.json          # 디버깅 설정
```

## 🔧 핵심 컴포넌트

### 1. extension.ts - 메인 컨트롤러

**역할**: VSCode Extension의 진입점이자 메인 컨트롤러

**주요 기능**:
- 확장 프로그램 활성화/비활성화
- 명령어 등록 및 처리
- UI 상호작용 관리
- 컴포넌트 간 조율

**등록된 명령어**:
- `teamsync.login` - 사용자 로그인
- `teamsync.pushSettings` - 설정 업로드
- `teamsync.pullSettings` - 설정 다운로드

### 2. apiService.ts - API 통신 서비스

**역할**: 외부 API와의 모든 통신을 담당

**주요 기능**:
- **인증 처리**: Google OAuth를 통한 Cognito 인증
- **토큰 관리**: Access Token 저장 및 관리
- **API 호출**: AWS API Gateway를 통한 백엔드 통신
- **로컬 서버**: OAuth 콜백을 위한 임시 HTTP 서버

**인증 플로우**:
```
1. 브라우저에서 Google OAuth 페이지 열기
2. 사용자 로그인 후 authorization code 받기
3. Code를 Access Token으로 교환
4. 사용자 정보 조회
5. Token을 메모리에 저장
```

### 3. cursorSettings.ts - 설정 파일 관리

**역할**: Cursor 설정 파일의 읽기/쓰기 및 관리

**관리하는 파일들**:
- `settings.json` - 메인 설정 파일
- `argv.json` - 실행 인자 설정
- `mcp.json` - MCP(Model Context Protocol) 설정
- `extensions.json` - 확장 프로그램 목록

**주요 기능**:
- 설정 파일 읽기/쓰기
- 임시 디렉토리에 백업 생성
- 파일 존재 여부 확인
- 디렉토리 자동 생성

## 🔄 워크플로우

### 로그인 프로세스

```
사용자 → Extension → 브라우저 → Google OAuth → Cognito → Extension
  │         │           │           │            │         │
  │    명령어 실행    브라우저 열기   사용자 인증   토큰 발급   토큰 저장
  │         │           │           │            │         │
  └─────────┴───────────┴───────────┴────────────┴─────────┘
```

### Push Settings 프로세스

```
1. 사용자가 Public/Private 선택
2. 로컬 Cursor 설정 파일들을 임시 디렉토리에 복사
3. 설정 파일들을 JSON으로 파싱
4. 각 설정 파일을 개별적으로 API에 업로드
5. 성공 메시지 표시
```

### Pull Settings 프로세스

```
1. 서버에서 사용자의 최신 설정 조회
2. 응답 데이터를 CursorSettings 형태로 변환
3. 임시 파일 생성
4. 실제 Cursor 설정 경로에 파일 쓰기
5. 성공 메시지 표시
```

## 🗂️ 데이터 구조

### CursorSettings Interface

```typescript
interface CursorSettings {
  settings: any;      // settings.json 내용
  argv: any;          // argv.json 내용
  mcp: any;           // mcp.json 내용
  extensions: any;    // extensions.json 내용
}
```

### AuthResponse Interface

```typescript
interface AuthResponse {
  token: string;
  user: {
    id: string;
    email: string;
  };
}
```

## 📍 파일 경로 (macOS)

```
~/Library/Application Support/Cursor/User/settings.json
~/.cursor/argv.json
~/.cursor/mcp.json
~/.cursor/extensions/extensions.json
```

## 🔐 보안 고려사항

1. **토큰 관리**: Access Token은 메모리에만 저장 (영구 저장 안함)
2. **HTTPS 통신**: 모든 API 통신은 HTTPS로 암호화
3. **OAuth 2.0**: 표준 OAuth 2.0 프로토콜 사용
4. **임시 파일**: 민감한 설정은 임시 디렉토리에서만 처리

## 🚀 확장 가능성

1. **다른 에디터 지원**: VSCode, Sublime Text 등
2. **팀 관리 기능**: 팀 생성, 멤버 관리
3. **설정 버전 관리**: Git과 유사한 버전 관리
4. **설정 템플릿**: 프로젝트별 설정 템플릿

## 🐛 에러 처리

- 네트워크 오류 시 사용자에게 명확한 메시지 표시
- 파일 접근 권한 오류 처리
- 인증 실패 시 재로그인 유도
- API 응답 오류에 대한 적절한 피드백

## 📊 성능 최적화

- 설정 파일 크기 제한
- 비동기 처리로 UI 블로킹 방지
- 임시 파일 자동 정리
- API 호출 최소화

이 아키텍처는 확장성과 유지보수성을 고려하여 설계되었으며, 각 컴포넌트가 명확한 책임을 가지도록 분리되어 있습니다.
