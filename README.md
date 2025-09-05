# TeamSync Pro

팀 개발 환경 설정 동기화 및 협업 도구

## 🚀 빠른 시작

### 1. 개발 환경 설정

```bash
# 의존성 설치
./scripts/dev-setup.sh

# 환경 변수 설정
cp src/backend/.env.example src/backend/.env
# .env 파일을 편집하여 데이터베이스 및 OAuth 설정
```

### 2. 데이터베이스 설정

```bash
# PostgreSQL 설치 (macOS)
brew install postgresql
brew services start postgresql

# 데이터베이스 생성
createdb teamsync

# Redis 설치 및 시작
brew install redis
brew services start redis
```

### 3. 개발 서버 실행

```bash
# Backend (터미널 1)
cd src/backend
npm run dev

# Frontend (터미널 2)
cd src/frontend
npm run dev

# VS Code Extension (VS Code에서)
# 1. src/extension 폴더를 VS Code로 열기
# 2. F5 키를 눌러 Extension Development Host 실행
```

## 📁 프로젝트 구조

```
├── src/
│   ├── extension/          # VS Code Extension
│   ├── backend/           # Node.js API Server
│   └── frontend/          # React Web Console
├── docs/                  # 상세 구현 문서
├── prompts/              # AI 프롬프트 템플릿
├── templates/            # 개발 템플릿
└── scripts/              # 개발 스크립트
```

## 🎯 핵심 기능

### ✅ 구현 완료
- **VS Code Extension**: 인증, 동기화, UI 컴포넌트
- **Backend API**: 인증, 팀 관리, 설정 동기화
- **데이터베이스**: PostgreSQL 모델 및 관계
- **보안**: JWT, OAuth 2.0, 권한 관리

### 🔄 진행 중
- **Frontend UI**: React 컴포넌트 구현
- **실시간 동기화**: WebSocket 구현
- **OAuth 연동**: Google, GitHub 실제 연동

## 🛠️ 기술 스택

- **Frontend**: React 18, TypeScript, Vite
- **Backend**: Node.js, Express, TypeScript
- **Database**: PostgreSQL, Redis
- **Extension**: VS Code API, TypeScript
- **Auth**: JWT, OAuth 2.0

## 📖 문서

상세한 구현 문서는 `docs/` 폴더에서 확인할 수 있습니다:

1. [프로젝트 아키텍처](docs/001-프로젝트아키텍처.md)
2. [VS Code 확장 개발](docs/002-VS코드확장개발.md)
3. [웹 콘솔 개발](docs/003-웹콘솔개발.md)
4. [백엔드 API 개발](docs/004-백엔드API개발.md)
5. [데이터베이스 설계](docs/005-데이터베이스설계.md)
6. [인증 보안 구현](docs/006-인증보안구현.md)

## 🎮 데모

### VS Code Extension
1. Command Palette에서 "TeamSync: 로그인" 실행
2. 브라우저에서 인증 완료
3. "TeamSync: 팀 선택"으로 동기화할 팀 선택
4. "TeamSync: 설정을 원격으로 동기화" 실행

### Web Console
1. http://localhost:3000 접속
2. Google/GitHub으로 로그인
3. 팀 생성 및 멤버 초대
4. 설정 히스토리 확인

## 🤝 개발 팀

**MCP (Multi-Core Pythonists)**
- 해커톤 프로젝트: Amazon Q Developer Hackathon

## 📄 라이선스

MIT License
