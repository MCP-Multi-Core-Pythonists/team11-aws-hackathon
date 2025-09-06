# 문서화 프롬프트 (Documentation Prompt)

## 효과적인 문서화 원칙

### 1. 문서화 계층 구조
```
프로젝트 문서화 계층
├── README.md (프로젝트 개요)
├── docs/
│   ├── api/ (API 문서)
│   ├── guides/ (사용자 가이드)
│   ├── architecture/ (아키텍처 문서)
│   ├── deployment/ (배포 가이드)
│   └── contributing/ (기여 가이드)
├── CHANGELOG.md (변경 이력)
└── LICENSE (라이선스)
```

### 2. 문서 작성 원칙
- **명확성**: 기술적 배경이 다른 독자도 이해할 수 있도록 작성
- **완전성**: 필요한 모든 정보를 포함
- **최신성**: 코드 변경과 함께 문서도 업데이트
- **실용성**: 실제 사용 가능한 예시와 코드 포함

## README.md 템플릿

```markdown
# 프로젝트명

간단한 프로젝트 설명과 주요 기능을 한 문장으로 요약합니다.

## 목차
- [설치](#설치)
- [사용법](#사용법)
- [API 문서](#api-문서)
- [기여하기](#기여하기)
- [라이선스](#라이선스)

## 주요 기능
- ✨ 기능 1: 간단한 설명
- 🚀 기능 2: 간단한 설명
- 🔒 기능 3: 간단한 설명

## 설치

### 요구사항
- Node.js 16.0 이상
- MongoDB 4.4 이상
- Redis 6.0 이상

### 설치 과정
```bash
# 저장소 클론
git clone https://github.com/username/project-name.git
cd project-name

# 의존성 설치
npm install

# 환경 변수 설정
cp .env.example .env
# .env 파일을 편집하여 필요한 값들을 설정하세요

# 데이터베이스 마이그레이션
npm run migrate

# 개발 서버 실행
npm run dev
```

## 사용법

### 기본 사용법
```javascript
const { UserService } = require('./src/services');

const userService = new UserService();

// 사용자 생성
const user = await userService.create({
  name: 'John Doe',
  email: 'john@example.com'
});

console.log('생성된 사용자:', user);
```

### 고급 사용법
```javascript
// 사용자 검색 (페이지네이션 포함)
const users = await userService.search({
  query: 'john',
  page: 1,
  limit: 10,
  sortBy: 'createdAt',
  sortOrder: 'desc'
});
```

## API 문서
자세한 API 문서는 [API 문서](./docs/api/README.md)를 참조하세요.

## 기여하기
기여 방법은 [기여 가이드](./CONTRIBUTING.md)를 참조하세요.

## 라이선스
이 프로젝트는 MIT 라이선스 하에 배포됩니다. 자세한 내용은 [LICENSE](./LICENSE) 파일을 참조하세요.
```

## API 문서화

### 1. OpenAPI/Swagger 문서
```yaml
# swagger.yml
openapi: 3.0.0
info:
  title: User Management API
  description: 사용자 관리를 위한 RESTful API
  version: 1.0.0
  contact:
    name: API Support
    email: support@example.com

servers:
  - url: https://api.example.com/v1
    description: Production server
  - url: https://staging-api.example.com/v1
    description: Staging server

paths:
  /users:
    get:
      summary: 사용자 목록 조회
      description: 페이지네이션을 지원하는 사용자 목록을 조회합니다.
      parameters:
        - name: page
          in: query
          description: 페이지 번호 (1부터 시작)
          required: false
          schema:
            type: integer
            minimum: 1
            default: 1
        - name: limit
          in: query
          description: 페이지당 항목 수
          required: false
          schema:
            type: integer
            minimum: 1
            maximum: 100
            default: 20
      responses:
        '200':
          description: 성공적으로 사용자 목록을 조회했습니다.
          content:
            application/json:
              schema:
                type: object
                properties:
                  users:
                    type: array
                    items:
                      $ref: '#/components/schemas/User'
                  pagination:
                    $ref: '#/components/schemas/Pagination'
        '400':
          description: 잘못된 요청 매개변수
        '500':
          description: 서버 내부 오류

    post:
      summary: 새 사용자 생성
      description: 새로운 사용자를 생성합니다.
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/CreateUserRequest'
      responses:
        '201':
          description: 사용자가 성공적으로 생성되었습니다.
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/User'
        '400':
          description: 잘못된 요청 데이터
        '409':
          description: 이미 존재하는 이메일

components:
  schemas:
    User:
      type: object
      properties:
        id:
          type: string
          description: 사용자 고유 식별자
          example: "507f1f77bcf86cd799439011"
        name:
          type: string
          description: 사용자 이름
          example: "홍길동"
        email:
          type: string
          format: email
          description: 사용자 이메일
          example: "hong@example.com"
        createdAt:
          type: string
          format: date-time
          description: 생성 일시
          example: "2023-01-01T00:00:00Z"
        updatedAt:
          type: string
          format: date-time
          description: 수정 일시
          example: "2023-01-01T00:00:00Z"

    CreateUserRequest:
      type: object
      required:
        - name
        - email
        - password
      properties:
        name:
          type: string
          minLength: 2
          maxLength: 50
          description: 사용자 이름
          example: "홍길동"
        email:
          type: string
          format: email
          description: 사용자 이메일
          example: "hong@example.com"
        password:
          type: string
          minLength: 8
          description: 비밀번호 (최소 8자)
          example: "securePassword123"

    Pagination:
      type: object
      properties:
        page:
          type: integer
          description: 현재 페이지
          example: 1
        limit:
          type: integer
          description: 페이지당 항목 수
          example: 20
        total:
          type: integer
          description: 전체 항목 수
          example: 150
        totalPages:
          type: integer
          description: 전체 페이지 수
          example: 8
```

### 2. JSDoc을 활용한 코드 문서화
```javascript
/**
 * 사용자 관리 서비스
 * @class UserService
 */
class UserService {
  /**
   * UserService 생성자
   * @param {Object} database - 데이터베이스 연결 객체
   * @param {Object} logger - 로거 인스턴스
   */
  constructor(database, logger) {
    this.db = database;
    this.logger = logger;
  }

  /**
   * 새로운 사용자를 생성합니다.
   * @async
   * @param {Object} userData - 사용자 데이터
   * @param {string} userData.name - 사용자 이름 (2-50자)
   * @param {string} userData.email - 사용자 이메일
   * @param {string} userData.password - 비밀번호 (최소 8자)
   * @returns {Promise<Object>} 생성된 사용자 객체
   * @throws {ValidationError} 입력 데이터가 유효하지 않은 경우
   * @throws {ConflictError} 이미 존재하는 이메일인 경우
   * @example
   * const user = await userService.createUser({
   *   name: '홍길동',
   *   email: 'hong@example.com',
   *   password: 'securePassword123'
   * });
   * console.log(user.id); // 생성된 사용자 ID
   */
  async createUser(userData) {
    this.logger.info('사용자 생성 시작', { email: userData.email });

    // 입력 검증
    const validationResult = this.validateUserData(userData);
    if (!validationResult.isValid) {
      throw new ValidationError(validationResult.errors);
    }

    // 중복 이메일 확인
    const existingUser = await this.db.users.findOne({ 
      email: userData.email 
    });
    if (existingUser) {
      throw new ConflictError('이미 존재하는 이메일입니다.');
    }

    // 비밀번호 해싱
    const hashedPassword = await this.hashPassword(userData.password);

    // 사용자 생성
    const user = await this.db.users.create({
      ...userData,
      password: hashedPassword,
      createdAt: new Date(),
      updatedAt: new Date()
    });

    this.logger.info('사용자 생성 완료', { userId: user.id });

    // 비밀번호 제외하고 반환
    const { password, ...userWithoutPassword } = user;
    return userWithoutPassword;
  }

  /**
   * 사용자 데이터의 유효성을 검증합니다.
   * @private
   * @param {Object} userData - 검증할 사용자 데이터
   * @returns {Object} 검증 결과 { isValid: boolean, errors: string[] }
   */
  validateUserData(userData) {
    const errors = [];

    if (!userData.name || userData.name.length < 2 || userData.name.length > 50) {
      errors.push('이름은 2-50자 사이여야 합니다.');
    }

    if (!userData.email || !this.isValidEmail(userData.email)) {
      errors.push('올바른 이메일 형식이 아닙니다.');
    }

    if (!userData.password || userData.password.length < 8) {
      errors.push('비밀번호는 최소 8자 이상이어야 합니다.');
    }

    return {
      isValid: errors.length === 0,
      errors
    };
  }
}
```

## 아키텍처 문서화

### 1. 시스템 아키텍처 다이어그램
```markdown
# 시스템 아키텍처

## 전체 아키텍처
```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Client    │    │   Load      │    │   API       │
│ (React App) │◄──►│  Balancer   │◄──►│  Gateway    │
└─────────────┘    └─────────────┘    └─────────────┘
                                              │
                   ┌─────────────────────────────┼─────────────────────────────┐
                   │                             │                             │
            ┌─────────────┐              ┌─────────────┐              ┌─────────────┐
            │   User      │              │   Product   │              │   Order     │
            │  Service    │              │   Service   │              │   Service   │
            └─────────────┘              └─────────────┘              └─────────────┘
                   │                             │                             │
            ┌─────────────┐              ┌─────────────┐              ┌─────────────┐
            │   User DB   │              │  Product DB │              │   Order DB  │
            │ (MongoDB)   │              │ (MongoDB)   │              │ (MongoDB)   │
            └─────────────┘              └─────────────┘              └─────────────┘
```

## 마이크로서비스 구조

### 사용자 서비스 (User Service)
- **책임**: 사용자 인증, 프로필 관리
- **기술 스택**: Node.js, Express, MongoDB
- **포트**: 3001
- **엔드포인트**: `/api/users/*`

### 상품 서비스 (Product Service)
- **책임**: 상품 정보 관리, 재고 관리
- **기술 스택**: Node.js, Express, MongoDB
- **포트**: 3002
- **엔드포인트**: `/api/products/*`

### 주문 서비스 (Order Service)
- **책임**: 주문 처리, 결제 연동
- **기술 스택**: Node.js, Express, MongoDB
- **포트**: 3003
- **엔드포인트**: `/api/orders/*`

## 데이터 플로우
1. 클라이언트가 API Gateway로 요청 전송
2. API Gateway가 인증 토큰 검증
3. 해당 마이크로서비스로 요청 라우팅
4. 서비스가 데이터베이스에서 데이터 조회/수정
5. 응답을 클라이언트로 반환
```

### 2. 데이터베이스 스키마 문서
```markdown
# 데이터베이스 스키마

## 사용자 컬렉션 (users)
```javascript
{
  _id: ObjectId,           // 고유 식별자
  name: String,            // 사용자 이름 (필수, 2-50자)
  email: String,           // 이메일 (필수, 유니크)
  password: String,        // 해싱된 비밀번호 (필수)
  role: String,            // 역할 (user, admin) 기본값: user
  profile: {
    avatar: String,        // 프로필 이미지 URL
    bio: String,           // 자기소개 (최대 500자)
    phone: String          // 전화번호
  },
  preferences: {
    language: String,      // 언어 설정 (기본값: ko)
    timezone: String,      // 시간대 (기본값: Asia/Seoul)
    notifications: {
      email: Boolean,      // 이메일 알림 (기본값: true)
      push: Boolean        // 푸시 알림 (기본값: true)
    }
  },
  createdAt: Date,         // 생성 일시
  updatedAt: Date,         // 수정 일시
  lastLoginAt: Date        // 마지막 로그인 일시
}
```

## 인덱스
```javascript
// 이메일 유니크 인덱스
db.users.createIndex({ email: 1 }, { unique: true });

// 역할별 조회를 위한 인덱스
db.users.createIndex({ role: 1 });

// 생성일 기준 정렬을 위한 인덱스
db.users.createIndex({ createdAt: -1 });
```

## 관계
- 사용자 → 주문 (1:N)
- 사용자 → 리뷰 (1:N)
- 사용자 → 위시리스트 (1:N)
```

## 배포 문서화

### 1. 배포 가이드
```markdown
# 배포 가이드

## 환경별 배포

### 개발 환경 (Development)
```bash
# 환경 변수 설정
export NODE_ENV=development
export DB_URL=mongodb://localhost:27017/myapp_dev
export REDIS_URL=redis://localhost:6379

# 애플리케이션 실행
npm run dev
```

### 스테이징 환경 (Staging)
```bash
# Docker Compose를 사용한 배포
docker-compose -f docker-compose.staging.yml up -d

# 헬스 체크
curl http://staging.example.com/health
```

### 프로덕션 환경 (Production)
```bash
# Kubernetes를 사용한 배포
kubectl apply -f k8s/namespace.yml
kubectl apply -f k8s/configmap.yml
kubectl apply -f k8s/secret.yml
kubectl apply -f k8s/deployment.yml
kubectl apply -f k8s/service.yml
kubectl apply -f k8s/ingress.yml

# 배포 상태 확인
kubectl get pods -n myapp-production
kubectl get services -n myapp-production
```

## 롤백 절차
```bash
# 이전 버전으로 롤백
kubectl rollout undo deployment/myapp-api -n myapp-production

# 특정 버전으로 롤백
kubectl rollout undo deployment/myapp-api --to-revision=2 -n myapp-production

# 롤백 상태 확인
kubectl rollout status deployment/myapp-api -n myapp-production
```

## 모니터링
- **애플리케이션 로그**: `/var/log/myapp/`
- **시스템 메트릭**: Prometheus + Grafana
- **에러 추적**: Sentry
- **업타임 모니터링**: Pingdom
```

### 2. 운영 가이드
```markdown
# 운영 가이드

## 일상적인 운영 작업

### 로그 확인
```bash
# 애플리케이션 로그 확인
kubectl logs -f deployment/myapp-api -n myapp-production

# 특정 시간대 로그 확인
kubectl logs --since=1h deployment/myapp-api -n myapp-production

# 에러 로그만 필터링
kubectl logs deployment/myapp-api -n myapp-production | grep ERROR
```

### 데이터베이스 백업
```bash
# MongoDB 백업
mongodump --host mongodb.example.com --db myapp_production --out /backup/$(date +%Y%m%d)

# 백업 파일 압축
tar -czf /backup/myapp_backup_$(date +%Y%m%d).tar.gz /backup/$(date +%Y%m%d)

# S3에 백업 파일 업로드
aws s3 cp /backup/myapp_backup_$(date +%Y%m%d).tar.gz s3://myapp-backups/
```

### 성능 모니터링
```bash
# CPU 및 메모리 사용량 확인
kubectl top pods -n myapp-production

# 네트워크 트래픽 확인
kubectl get --raw /api/v1/nodes/node-name/proxy/stats/summary

# 데이터베이스 성능 확인
mongo --eval "db.runCommand({serverStatus: 1})"
```

## 장애 대응

### 일반적인 장애 시나리오

#### 1. 애플리케이션 응답 없음
```bash
# 1. 파드 상태 확인
kubectl get pods -n myapp-production

# 2. 파드 재시작
kubectl rollout restart deployment/myapp-api -n myapp-production

# 3. 로그 확인
kubectl logs -f deployment/myapp-api -n myapp-production
```

#### 2. 데이터베이스 연결 실패
```bash
# 1. 데이터베이스 상태 확인
kubectl get pods -l app=mongodb -n myapp-production

# 2. 연결 테스트
kubectl exec -it mongodb-pod -n myapp-production -- mongo --eval "db.adminCommand('ping')"

# 3. 연결 풀 재설정
kubectl rollout restart deployment/myapp-api -n myapp-production
```

#### 3. 높은 메모리 사용량
```bash
# 1. 메모리 사용량 확인
kubectl top pods -n myapp-production

# 2. 힙 덤프 생성 (Node.js)
kubectl exec -it myapp-api-pod -n myapp-production -- kill -USR2 1

# 3. 파드 스케일링
kubectl scale deployment myapp-api --replicas=5 -n myapp-production
```
```

## 문서화 도구 및 자동화

### 1. 자동 문서 생성
```javascript
// JSDoc을 사용한 API 문서 자동 생성
// package.json
{
  "scripts": {
    "docs:generate": "jsdoc -c jsdoc.conf.json",
    "docs:serve": "http-server ./docs -p 8080"
  }
}

// jsdoc.conf.json
{
  "source": {
    "include": ["./src/"],
    "includePattern": "\\.(js|jsx)$",
    "exclude": ["node_modules/", "test/"]
  },
  "opts": {
    "destination": "./docs/api/"
  },
  "plugins": ["plugins/markdown"]
}
```

### 2. 문서 버전 관리
```markdown
# CHANGELOG.md

## [1.2.0] - 2023-12-01

### Added
- 사용자 프로필 이미지 업로드 기능
- 이메일 알림 설정 기능
- API 응답 캐싱 기능

### Changed
- 사용자 검색 성능 개선 (응답 시간 50% 단축)
- 에러 메시지 다국어 지원

### Fixed
- 비밀번호 재설정 이메일 발송 오류 수정
- 페이지네이션 계산 오류 수정

### Security
- JWT 토큰 만료 시간 단축 (24시간 → 1시간)
- 비밀번호 복잡도 요구사항 강화

## [1.1.0] - 2023-11-15

### Added
- 사용자 역할 기반 접근 제어
- API 요청 제한 기능

### Fixed
- 동시 로그인 시 세션 충돌 문제 해결
```

### 3. 문서 품질 관리
```javascript
// 문서 링크 검증 스크립트
const fs = require('fs');
const path = require('path');
const axios = require('axios');

async function validateDocumentLinks(docsDir) {
  const markdownFiles = getMarkdownFiles(docsDir);
  const brokenLinks = [];

  for (const file of markdownFiles) {
    const content = fs.readFileSync(file, 'utf8');
    const links = extractLinks(content);

    for (const link of links) {
      try {
        if (link.startsWith('http')) {
          await axios.head(link, { timeout: 5000 });
        } else {
          const filePath = path.resolve(path.dirname(file), link);
          if (!fs.existsSync(filePath)) {
            brokenLinks.push({ file, link });
          }
        }
      } catch (error) {
        brokenLinks.push({ file, link, error: error.message });
      }
    }
  }

  if (brokenLinks.length > 0) {
    console.error('깨진 링크 발견:');
    brokenLinks.forEach(({ file, link, error }) => {
      console.error(`${file}: ${link} ${error ? `(${error})` : ''}`);
    });
    process.exit(1);
  }

  console.log('모든 링크가 유효합니다.');
}
```

## 문서화 체크리스트

### 프로젝트 시작 시
- [ ] README.md 작성
- [ ] 기본 문서 구조 설정
- [ ] API 문서 템플릿 준비
- [ ] 기여 가이드 작성

### 개발 진행 중
- [ ] 코드 주석 작성 (JSDoc)
- [ ] API 변경사항 문서 업데이트
- [ ] 아키텍처 변경사항 반영
- [ ] 사용 예시 코드 업데이트

### 릴리스 전
- [ ] CHANGELOG.md 업데이트
- [ ] 배포 가이드 검토
- [ ] 문서 링크 검증
- [ ] 사용자 가이드 최신화

### 릴리스 후
- [ ] 문서 피드백 수집
- [ ] FAQ 업데이트
- [ ] 트러블슈팅 가이드 보완
- [ ] 문서 사용성 개선
