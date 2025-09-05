# Backend Service 구현 명세서

## 1. 서비스 개요

### 1.1 목적
TeamSync Pro의 백엔드 API 서버로, 사용자 인증, 팀 관리, 설정 동기화를 담당합니다.

### 1.2 기술 스택
- **Runtime**: Node.js 18+
- **Framework**: Express.js
- **Database**: SQLite (개발), PostgreSQL (운영)
- **Cache**: Redis (메모리 저장소로 대체)
- **Authentication**: JWT + OAuth 2.0 (Device Flow)
- **ORM**: Sequelize

## 2. 아키텍처 설계

### 2.1 디렉토리 구조
```
src/backend/
├── src/
│   ├── controllers/     # API 컨트롤러
│   ├── models/         # 데이터 모델
│   ├── routes/         # 라우트 정의
│   ├── services/       # 비즈니스 로직
│   ├── middleware/     # 미들웨어
│   ├── config/         # 설정 파일
│   └── utils/          # 유틸리티
├── package.json
└── tsconfig.json
```

### 2.2 핵심 컴포넌트

#### 2.2.1 인증 시스템 (Auth System)
- **Device Flow**: VS Code Extension용 OAuth 2.0 Device Flow
- **JWT 토큰**: Access Token + Refresh Token
- **OAuth 연동**: Google, GitHub (향후 확장)

#### 2.2.2 팀 관리 시스템 (Team Management)
- **팀 생성/수정/삭제**: 팀 CRUD 작업
- **멤버 관리**: 초대, 권한 관리, 제거
- **권한 시스템**: Owner, Admin, Member 역할

#### 2.2.3 설정 동기화 시스템 (Configuration Sync)
- **설정 저장**: VS Code 설정, 확장, 스니펫 등
- **버전 관리**: 설정 변경 이력 추적
- **실시간 동기화**: WebSocket 기반 (향후)

## 3. API 명세

### 3.1 인증 API

#### Device Flow 시작
```http
POST /api/v1/auth/device
Content-Type: application/json

{
  "client_id": "vscode-extension"
}

Response:
{
  "device_code": "string",
  "user_code": "string",
  "verification_uri": "http://localhost:3000/device",
  "expires_in": 600,
  "interval": 5
}
```

#### 토큰 폴링
```http
POST /api/v1/auth/token
Content-Type: application/json

{
  "grant_type": "device_code",
  "device_code": "string"
}

Response:
{
  "access_token": "string",
  "refresh_token": "string",
  "token_type": "Bearer",
  "expires_in": 3600
}
```

### 3.2 팀 관리 API

#### 팀 목록 조회
```http
GET /api/v1/teams
Authorization: Bearer {access_token}

Response:
[
  {
    "id": "string",
    "name": "string",
    "description": "string",
    "memberRole": "owner|admin|member",
    "joinedAt": "datetime"
  }
]
```

#### 팀 생성
```http
POST /api/v1/teams
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "name": "string",
  "description": "string",
  "settings": {
    "visibility": "public|private",
    "allowMemberInvite": boolean
  }
}
```

### 3.3 설정 동기화 API

#### 설정 업로드
```http
POST /api/v1/configurations/sync
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "teamId": "string",
  "configuration": {
    "settings": {},
    "extensions": [],
    "keybindings": [],
    "snippets": {}
  }
}
```

#### 설정 다운로드
```http
GET /api/v1/configurations/teams/{teamId}/latest
Authorization: Bearer {access_token}

Response:
{
  "id": "string",
  "teamId": "string",
  "configuration": {},
  "version": "string",
  "createdAt": "datetime"
}
```

## 4. 데이터 모델

### 4.1 User 모델
```typescript
interface User {
  id: string;
  email: string;
  name: string;
  avatar?: string;
  provider: 'google' | 'github' | 'email';
  providerId?: string;
  createdAt: Date;
  updatedAt: Date;
}
```

### 4.2 Team 모델
```typescript
interface Team {
  id: string;
  name: string;
  description?: string;
  ownerId: string;
  settings: TeamSettings;
  createdAt: Date;
  updatedAt: Date;
}

interface TeamSettings {
  visibility: 'public' | 'private';
  allowMemberInvite: boolean;
  requireApproval: boolean;
  maxMembers?: number;
}
```

### 4.3 Configuration 모델
```typescript
interface Configuration {
  id: string;
  teamId: string;
  configuration: ConfigurationData;
  version: string;
  createdBy: string;
  createdAt: Date;
}

interface ConfigurationData {
  settings?: Record<string, any>;
  extensions?: string[];
  keybindings?: KeyBinding[];
  snippets?: Record<string, Snippet>;
  tasks?: TaskDefinition[];
}
```

## 5. 보안 고려사항

### 5.1 인증 보안
- JWT 토큰 만료 시간 설정 (Access: 1시간, Refresh: 30일)
- Refresh Token 로테이션
- Device Code 만료 시간 (10분)

### 5.2 API 보안
- Rate Limiting (IP당 분당 100 요청)
- CORS 설정 (VS Code Extension, Frontend 허용)
- Input Validation (Joi 스키마)
- SQL Injection 방지 (Sequelize ORM)

### 5.3 데이터 보안
- 민감 정보 암호화
- 환경 변수로 시크릿 관리
- HTTPS 강제 (운영 환경)

## 6. 성능 최적화

### 6.1 데이터베이스 최적화
- 인덱스 설정 (사용자 ID, 팀 ID, 이메일)
- 쿼리 최적화 (N+1 문제 해결)
- 커넥션 풀 설정

### 6.2 캐싱 전략
- Redis 캐싱 (세션, 설정 데이터)
- 메모리 캐시 (자주 조회되는 데이터)
- HTTP 캐시 헤더 설정

### 6.3 모니터링
- 응답 시간 로깅
- 에러 추적 (Winston Logger)
- 헬스 체크 엔드포인트

## 7. 배포 및 운영

### 7.1 개발 환경
```bash
# 의존성 설치
npm install

# 개발 서버 실행
npm run dev

# 테스트 실행
npm test
```

### 7.2 환경 변수
```env
NODE_ENV=development
PORT=3001
JWT_ACCESS_SECRET=your-access-secret
JWT_REFRESH_SECRET=your-refresh-secret
DB_HOST=localhost
DB_PORT=5432
DB_NAME=teamsync
DB_USER=postgres
DB_PASSWORD=password
REDIS_URL=redis://localhost:6379
```

### 7.3 Docker 배포
```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
RUN npm run build
EXPOSE 3001
CMD ["npm", "start"]
```

## 8. 테스트 전략

### 8.1 단위 테스트
- 컨트롤러 테스트
- 서비스 로직 테스트
- 모델 검증 테스트

### 8.2 통합 테스트
- API 엔드포인트 테스트
- 데이터베이스 연동 테스트
- 인증 플로우 테스트

### 8.3 E2E 테스트
- 전체 사용자 시나리오 테스트
- Extension과의 연동 테스트

## 9. TODO 및 향후 계획

### 9.1 단기 목표 (1주)
- [ ] OAuth 실제 연동 (Google, GitHub)
- [ ] WebSocket 실시간 동기화
- [ ] 설정 충돌 해결 로직
- [ ] 팀 초대 시스템

### 9.2 중기 목표 (1개월)
- [ ] 설정 버전 관리 시스템
- [ ] 팀 템플릿 기능
- [ ] 사용 통계 및 분석
- [ ] 백업 및 복구 시스템

### 9.3 장기 목표 (3개월)
- [ ] 멀티 테넌트 지원
- [ ] 엔터프라이즈 기능
- [ ] 플러그인 시스템
- [ ] 클라우드 배포 자동화
