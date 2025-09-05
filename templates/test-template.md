# 테스트 템플릿 (Test Template)

## 테스트 계획서

### 기본 정보
- **테스트 대상**: [기능/모듈명]
- **테스트 담당자**: [담당자명]
- **테스트 기간**: [시작일 - 종료일]
- **테스트 환경**: [개발/스테이징/프로덕션]

### 테스트 목표
- **주요 목표**: [테스트의 주요 목적]
- **성공 기준**: [테스트 성공을 판단하는 기준]
- **위험 요소**: [예상되는 위험 요소들]

## 테스트 전략

### 테스트 피라미드
```
        /\
       /  \
      / E2E \     10% - 사용자 시나리오 검증
     /______\
    /        \
   /Integration\ 20% - 컴포넌트 간 상호작용
  /____________\
 /              \
/   Unit Tests   \ 70% - 개별 함수/클래스 검증
/________________\
```

### 테스트 유형별 전략

#### 1. 단위 테스트 (Unit Tests)
```javascript
// 테스트 파일 구조: [모듈명].test.js
describe('UserService', () => {
  let userService;
  let mockDatabase;

  beforeEach(() => {
    mockDatabase = {
      findById: jest.fn(),
      create: jest.fn(),
      update: jest.fn(),
      delete: jest.fn()
    };
    userService = new UserService(mockDatabase);
  });

  describe('createUser', () => {
    it('should create user with valid data', async () => {
      // Given
      const userData = {
        name: 'John Doe',
        email: 'john@example.com',
        password: 'securePassword123'
      };
      mockDatabase.create.mockResolvedValue({ id: 1, ...userData });

      // When
      const result = await userService.createUser(userData);

      // Then
      expect(result).toHaveProperty('id');
      expect(result.name).toBe(userData.name);
      expect(mockDatabase.create).toHaveBeenCalledWith(userData);
    });

    it('should throw error for invalid email', async () => {
      // Given
      const invalidUserData = {
        name: 'John Doe',
        email: 'invalid-email',
        password: 'securePassword123'
      };

      // When & Then
      await expect(userService.createUser(invalidUserData))
        .rejects.toThrow('Invalid email format');
    });
  });
});
```

#### 2. 통합 테스트 (Integration Tests)
```javascript
// API 통합 테스트
describe('User API Integration', () => {
  let app;
  let testDb;

  beforeAll(async () => {
    testDb = await setupTestDatabase();
    app = createApp(testDb);
  });

  afterAll(async () => {
    await cleanupTestDatabase(testDb);
  });

  beforeEach(async () => {
    await testDb.users.deleteMany({});
  });

  describe('POST /api/users', () => {
    it('should create user and return 201', async () => {
      const userData = {
        name: 'John Doe',
        email: 'john@example.com',
        password: 'securePassword123'
      };

      const response = await request(app)
        .post('/api/users')
        .send(userData)
        .expect(201);

      expect(response.body).toHaveProperty('id');
      expect(response.body.name).toBe(userData.name);
      expect(response.body.email).toBe(userData.email);
      expect(response.body).not.toHaveProperty('password');

      // 데이터베이스 확인
      const savedUser = await testDb.users.findById(response.body.id);
      expect(savedUser).toBeTruthy();
    });
  });
});
```

#### 3. E2E 테스트 (End-to-End Tests)
```javascript
// Playwright E2E 테스트
import { test, expect } from '@playwright/test';

test.describe('사용자 등록 플로우', () => {
  test('사용자가 회원가입을 완료할 수 있다', async ({ page }) => {
    // 회원가입 페이지로 이동
    await page.goto('/signup');

    // 폼 입력
    await page.fill('#name', 'John Doe');
    await page.fill('#email', 'john@example.com');
    await page.fill('#password', 'securePassword123');
    await page.fill('#confirmPassword', 'securePassword123');

    // 약관 동의
    await page.check('#terms-agreement');

    // 회원가입 버튼 클릭
    await page.click('#signup-button');

    // 성공 메시지 확인
    await expect(page.locator('#success-message')).toBeVisible();
    await expect(page.locator('#success-message')).toContainText('회원가입이 완료되었습니다');

    // 로그인 페이지로 리다이렉트 확인
    await expect(page).toHaveURL('/login');
  });

  test('잘못된 이메일 형식으로 회원가입 시 에러 메시지가 표시된다', async ({ page }) => {
    await page.goto('/signup');

    await page.fill('#name', 'John Doe');
    await page.fill('#email', 'invalid-email');
    await page.fill('#password', 'securePassword123');
    await page.click('#signup-button');

    await expect(page.locator('#email-error')).toBeVisible();
    await expect(page.locator('#email-error')).toContainText('올바른 이메일 형식을 입력해주세요');
  });
});
```

## 테스트 자동화 도구 연동

### 1. Jest 설정
```javascript
// jest.config.js
module.exports = {
  testEnvironment: 'node',
  collectCoverageFrom: [
    'src/**/*.{js,jsx,ts,tsx}',
    '!src/**/*.test.{js,jsx,ts,tsx}',
    '!src/index.js',
    '!src/config/**'
  ],
  coverageThreshold: {
    global: {
      branches: 80,
      functions: 80,
      lines: 80,
      statements: 80
    }
  },
  setupFilesAfterEnv: ['<rootDir>/src/test/setup.js'],
  testMatch: [
    '<rootDir>/src/**/__tests__/**/*.{js,jsx,ts,tsx}',
    '<rootDir>/src/**/*.{spec,test}.{js,jsx,ts,tsx}'
  ]
};
```

### 2. 테스트 데이터 팩토리
```javascript
// test/factories/userFactory.js
const { faker } = require('@faker-js/faker');

class UserFactory {
  static create(overrides = {}) {
    return {
      id: faker.datatype.uuid(),
      name: faker.name.fullName(),
      email: faker.internet.email(),
      password: faker.internet.password(),
      createdAt: faker.date.recent(),
      ...overrides
    };
  }

  static createMany(count, overrides = {}) {
    return Array.from({ length: count }, () => this.create(overrides));
  }

  static createAdmin(overrides = {}) {
    return this.create({
      role: 'admin',
      permissions: ['read', 'write', 'delete'],
      ...overrides
    });
  }
}

module.exports = UserFactory;
```

### 3. 테스트 유틸리티
```javascript
// test/utils/testHelpers.js
const request = require('supertest');

class TestHelpers {
  static async createAuthenticatedUser(app, userData = {}) {
    const user = UserFactory.create(userData);
    
    // 사용자 생성
    await request(app)
      .post('/api/users')
      .send(user);

    // 로그인하여 토큰 획득
    const loginResponse = await request(app)
      .post('/api/auth/login')
      .send({
        email: user.email,
        password: user.password
      });

    return {
      user,
      token: loginResponse.body.token
    };
  }

  static async cleanupDatabase(db) {
    const collections = await db.listCollections().toArray();
    
    for (const collection of collections) {
      await db.collection(collection.name).deleteMany({});
    }
  }

  static mockExternalAPI(url, response) {
    return jest.fn().mockImplementation(() => 
      Promise.resolve({
        status: 200,
        data: response
      })
    );
  }
}

module.exports = TestHelpers;
```

## 커버리지 추적

### 1. 커버리지 설정
```json
{
  "scripts": {
    "test": "jest",
    "test:watch": "jest --watch",
    "test:coverage": "jest --coverage",
    "test:coverage:watch": "jest --coverage --watchAll"
  },
  "jest": {
    "coverageReporters": ["text", "lcov", "html"],
    "coverageDirectory": "coverage"
  }
}
```

### 2. 커버리지 리포트 분석
```bash
# 커버리지 리포트 생성
npm run test:coverage

# HTML 리포트 확인
open coverage/lcov-report/index.html

# 특정 파일의 커버리지 확인
npx jest --coverage --collectCoverageFrom="src/services/userService.js"
```

### 3. CI/CD 통합
```yaml
# .github/workflows/test.yml
name: Test Coverage

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v2
      
      - name: Setup Node.js
        uses: actions/setup-node@v2
        with:
          node-version: '16'
          
      - name: Install dependencies
        run: npm ci
        
      - name: Run tests with coverage
        run: npm run test:coverage
        
      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v2
        with:
          file: ./coverage/lcov.info
          
      - name: Check coverage threshold
        run: |
          COVERAGE=$(cat coverage/coverage-summary.json | jq '.total.lines.pct')
          if (( $(echo "$COVERAGE < 80" | bc -l) )); then
            echo "Coverage $COVERAGE% is below threshold 80%"
            exit 1
          fi
```

## 성능 테스트

### 1. 부하 테스트 (Load Testing)
```javascript
// k6 성능 테스트 스크립트
import http from 'k6/http';
import { check, sleep } from 'k6';

export let options = {
  stages: [
    { duration: '2m', target: 100 }, // 2분간 100명까지 증가
    { duration: '5m', target: 100 }, // 5분간 100명 유지
    { duration: '2m', target: 200 }, // 2분간 200명까지 증가
    { duration: '5m', target: 200 }, // 5분간 200명 유지
    { duration: '2m', target: 0 },   // 2분간 0명까지 감소
  ],
  thresholds: {
    http_req_duration: ['p(99)<1500'], // 99%의 요청이 1.5초 이내
    http_req_failed: ['rate<0.1'],     // 에러율 10% 미만
  },
};

export default function () {
  // 사용자 생성 테스트
  let createUserResponse = http.post('http://localhost:3000/api/users', {
    name: 'Test User',
    email: `test${Math.random()}@example.com`,
    password: 'password123'
  });

  check(createUserResponse, {
    'user creation status is 201': (r) => r.status === 201,
    'user creation response time < 500ms': (r) => r.timings.duration < 500,
  });

  sleep(1);

  // 사용자 조회 테스트
  if (createUserResponse.status === 201) {
    let userId = JSON.parse(createUserResponse.body).id;
    let getUserResponse = http.get(`http://localhost:3000/api/users/${userId}`);

    check(getUserResponse, {
      'user retrieval status is 200': (r) => r.status === 200,
      'user retrieval response time < 200ms': (r) => r.timings.duration < 200,
    });
  }

  sleep(1);
}
```

### 2. 스트레스 테스트
```javascript
// Artillery.js 스트레스 테스트
module.exports = {
  config: {
    target: 'http://localhost:3000',
    phases: [
      {
        duration: 60,
        arrivalRate: 10,
        name: 'Warm up'
      },
      {
        duration: 120,
        arrivalRate: 50,
        name: 'Ramp up load'
      },
      {
        duration: 300,
        arrivalRate: 100,
        name: 'Sustained load'
      }
    ],
    payload: {
      path: './test-data.csv',
      fields: ['email', 'password']
    }
  },
  scenarios: [
    {
      name: 'User authentication flow',
      weight: 70,
      flow: [
        {
          post: {
            url: '/api/auth/login',
            json: {
              email: '{{ email }}',
              password: '{{ password }}'
            },
            capture: {
              json: '$.token',
              as: 'authToken'
            }
          }
        },
        {
          get: {
            url: '/api/users/profile',
            headers: {
              'Authorization': 'Bearer {{ authToken }}'
            }
          }
        }
      ]
    }
  ]
};
```

## 테스트 환경 관리

### 1. Docker 테스트 환경
```dockerfile
# Dockerfile.test
FROM node:16-alpine

WORKDIR /app

COPY package*.json ./
RUN npm ci --only=production

COPY . .

# 테스트 데이터베이스 설정
ENV NODE_ENV=test
ENV DB_URL=mongodb://test-db:27017/testdb

CMD ["npm", "test"]
```

```yaml
# docker-compose.test.yml
version: '3.8'

services:
  app-test:
    build:
      context: .
      dockerfile: Dockerfile.test
    depends_on:
      - test-db
      - test-redis
    environment:
      - NODE_ENV=test
      - DB_URL=mongodb://test-db:27017/testdb
      - REDIS_URL=redis://test-redis:6379

  test-db:
    image: mongo:5.0
    environment:
      - MONGO_INITDB_DATABASE=testdb

  test-redis:
    image: redis:6.2-alpine
```

### 2. 테스트 데이터 시딩
```javascript
// test/seeds/testData.js
const UserFactory = require('../factories/userFactory');
const ProductFactory = require('../factories/productFactory');

class TestDataSeeder {
  static async seedDatabase(db) {
    // 사용자 데이터 생성
    const users = UserFactory.createMany(10);
    await db.collection('users').insertMany(users);

    // 상품 데이터 생성
    const products = ProductFactory.createMany(50);
    await db.collection('products').insertMany(products);

    // 주문 데이터 생성
    const orders = this.createOrdersForUsers(users, products);
    await db.collection('orders').insertMany(orders);

    return { users, products, orders };
  }

  static createOrdersForUsers(users, products) {
    return users.flatMap(user => 
      Array.from({ length: Math.floor(Math.random() * 5) + 1 }, () => ({
        userId: user.id,
        productId: products[Math.floor(Math.random() * products.length)].id,
        quantity: Math.floor(Math.random() * 3) + 1,
        status: 'completed',
        createdAt: new Date()
      }))
    );
  }
}

module.exports = TestDataSeeder;
```

## 테스트 체크리스트

### 테스트 작성 전
- [ ] 테스트 계획 수립
- [ ] 테스트 환경 구성
- [ ] 테스트 데이터 준비
- [ ] Mock 객체 설계

### 테스트 실행 중
- [ ] 단위 테스트 작성 및 실행
- [ ] 통합 테스트 작성 및 실행
- [ ] E2E 테스트 작성 및 실행
- [ ] 성능 테스트 실행

### 테스트 완료 후
- [ ] 커버리지 목표 달성 확인
- [ ] 테스트 결과 문서화
- [ ] CI/CD 파이프라인 통합
- [ ] 테스트 유지보수 계획 수립
