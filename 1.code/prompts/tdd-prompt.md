# TDD 프롬프트 (Test-Driven Development Prompt)

## 개발자 레벨별 TDD 접근법

### 초급 개발자 (Junior)
**목표**: TDD 기본 사이클 익히기
```javascript
// 1. Red: 실패하는 테스트 작성
describe('Calculator', () => {
  it('should add two numbers', () => {
    const calculator = new Calculator();
    expect(calculator.add(2, 3)).toBe(5);
  });
});

// 2. Green: 테스트를 통과하는 최소한의 코드
class Calculator {
  add(a, b) {
    return a + b;
  }
}

// 3. Refactor: 코드 개선
class Calculator {
  add(a, b) {
    if (typeof a !== 'number' || typeof b !== 'number') {
      throw new Error('Arguments must be numbers');
    }
    return a + b;
  }
}
```

### 중급 개발자 (Mid-level)
**목표**: 복잡한 비즈니스 로직에 TDD 적용
```javascript
// 사용자 스토리: 할인 계산 기능
describe('DiscountCalculator', () => {
  describe('when user is premium member', () => {
    it('should apply 20% discount for orders over $100', () => {
      const calculator = new DiscountCalculator();
      const user = { type: 'premium' };
      const order = { amount: 150 };
      
      expect(calculator.calculate(user, order)).toBe(120);
    });
  });
});
```

### 고급 개발자 (Senior)
**목표**: 아키텍처 설계와 TDD 통합
```javascript
// 도메인 주도 설계와 TDD 결합
describe('OrderService', () => {
  let orderService;
  let mockPaymentGateway;
  let mockInventoryService;

  beforeEach(() => {
    mockPaymentGateway = jest.fn();
    mockInventoryService = jest.fn();
    orderService = new OrderService(mockPaymentGateway, mockInventoryService);
  });

  it('should process order with payment and inventory check', async () => {
    // Given
    const order = new Order({ items: [{ id: 1, quantity: 2 }] });
    mockInventoryService.checkAvailability.mockResolvedValue(true);
    mockPaymentGateway.charge.mockResolvedValue({ success: true });

    // When
    const result = await orderService.processOrder(order);

    // Then
    expect(result.status).toBe('completed');
    expect(mockInventoryService.checkAvailability).toHaveBeenCalled();
    expect(mockPaymentGateway.charge).toHaveBeenCalled();
  });
});
```

## 테스트 더블 사용법

### 1. Mock - 행위 검증
```javascript
// 외부 서비스 호출 검증
describe('EmailService', () => {
  it('should send welcome email to new user', async () => {
    const mockMailer = jest.fn();
    const emailService = new EmailService(mockMailer);
    const user = { email: 'test@example.com', name: 'John' };

    await emailService.sendWelcomeEmail(user);

    expect(mockMailer).toHaveBeenCalledWith({
      to: 'test@example.com',
      subject: 'Welcome John!',
      template: 'welcome'
    });
  });
});
```

### 2. Stub - 상태 반환
```javascript
// 외부 API 응답 시뮬레이션
describe('WeatherService', () => {
  it('should return weather data for given city', async () => {
    const stubApiClient = {
      get: jest.fn().mockResolvedValue({
        data: { temperature: 25, condition: 'sunny' }
      })
    };
    
    const weatherService = new WeatherService(stubApiClient);
    const weather = await weatherService.getWeather('Seoul');

    expect(weather.temperature).toBe(25);
    expect(weather.condition).toBe('sunny');
  });
});
```

### 3. Spy - 기존 객체 감시
```javascript
// 실제 객체의 메서드 호출 감시
describe('Logger', () => {
  it('should log error messages', () => {
    const consoleSpy = jest.spyOn(console, 'error').mockImplementation();
    const logger = new Logger();

    logger.error('Test error message');

    expect(consoleSpy).toHaveBeenCalledWith('[ERROR]', 'Test error message');
    consoleSpy.mockRestore();
  });
});
```

## 테스트 피라미드 균형

### 1. Unit Tests (70%)
```javascript
// 단위 테스트 - 빠르고 격리된 테스트
describe('UserValidator', () => {
  it('should validate email format', () => {
    const validator = new UserValidator();
    
    expect(validator.isValidEmail('test@example.com')).toBe(true);
    expect(validator.isValidEmail('invalid-email')).toBe(false);
  });
});
```

### 2. Integration Tests (20%)
```javascript
// 통합 테스트 - 컴포넌트 간 상호작용 테스트
describe('UserService Integration', () => {
  let userService;
  let testDatabase;

  beforeAll(async () => {
    testDatabase = await setupTestDatabase();
    userService = new UserService(testDatabase);
  });

  it('should create user and save to database', async () => {
    const userData = { name: 'John', email: 'john@example.com' };
    
    const user = await userService.createUser(userData);
    const savedUser = await testDatabase.users.findById(user.id);

    expect(savedUser.name).toBe('John');
    expect(savedUser.email).toBe('john@example.com');
  });
});
```

### 3. E2E Tests (10%)
```javascript
// E2E 테스트 - 전체 시스템 동작 검증
describe('User Registration Flow', () => {
  it('should allow user to register and login', async () => {
    await page.goto('/register');
    await page.fill('#email', 'test@example.com');
    await page.fill('#password', 'password123');
    await page.click('#register-button');
    
    await expect(page).toHaveURL('/dashboard');
    await expect(page.locator('#welcome-message')).toContainText('Welcome');
  });
});
```

## 레거시 코드에 TDD 적용

### 1. 특성화 테스트 (Characterization Tests)
```javascript
// 기존 코드의 현재 동작을 테스트로 고정
describe('Legacy calculateTax function', () => {
  it('should maintain current behavior', () => {
    // 현재 동작을 그대로 테스트
    expect(calculateTax(100, 'US')).toBe(8.5);
    expect(calculateTax(100, 'CA')).toBe(12.0);
    expect(calculateTax(0, 'US')).toBe(0);
  });
});
```

### 2. 점진적 리팩토링
```javascript
// 1단계: 기존 함수를 래핑
class TaxCalculator {
  calculate(amount, region) {
    return calculateTax(amount, region); // 기존 함수 호출
  }
}

// 2단계: 새로운 구현으로 점진적 교체
class TaxCalculator {
  calculate(amount, region) {
    if (this.useNewImplementation) {
      return this.calculateTaxNew(amount, region);
    }
    return calculateTax(amount, region);
  }
}
```

## 빠르고 안정적인 테스트 작성법

### 1. 테스트 격리
```javascript
// ❌ 테스트 간 의존성 있음
let sharedUser;

describe('UserService', () => {
  it('should create user', () => {
    sharedUser = userService.create({ name: 'John' });
    expect(sharedUser.name).toBe('John');
  });

  it('should update user', () => {
    userService.update(sharedUser.id, { name: 'Jane' });
    expect(sharedUser.name).toBe('Jane'); // 이전 테스트에 의존
  });
});

// ✅ 각 테스트가 독립적
describe('UserService', () => {
  let user;

  beforeEach(() => {
    user = userService.create({ name: 'John' });
  });

  it('should create user', () => {
    expect(user.name).toBe('John');
  });

  it('should update user', () => {
    userService.update(user.id, { name: 'Jane' });
    const updatedUser = userService.findById(user.id);
    expect(updatedUser.name).toBe('Jane');
  });
});
```

### 2. 테스트 데이터 팩토리
```javascript
// 테스트 데이터 생성 유틸리티
class UserFactory {
  static create(overrides = {}) {
    return {
      id: Math.random().toString(36),
      name: 'Test User',
      email: 'test@example.com',
      createdAt: new Date(),
      ...overrides
    };
  }

  static createMany(count, overrides = {}) {
    return Array.from({ length: count }, () => this.create(overrides));
  }
}

// 사용 예시
describe('UserService', () => {
  it('should handle multiple users', () => {
    const users = UserFactory.createMany(5, { role: 'admin' });
    const result = userService.processUsers(users);
    expect(result).toHaveLength(5);
  });
});
```

## 테스트 도구별 최적화

### 1. Jest 최적화
```javascript
// jest.config.js
module.exports = {
  // 병렬 실행으로 속도 향상
  maxWorkers: '50%',
  
  // 캐시 활용
  cache: true,
  cacheDirectory: '<rootDir>/.jest-cache',
  
  // 불필요한 파일 제외
  testPathIgnorePatterns: ['/node_modules/', '/build/'],
  
  // 빠른 실패로 피드백 개선
  bail: 1,
  
  // 테스트 환경 최적화
  testEnvironment: 'node', // DOM이 필요없는 경우
};
```

### 2. 테스트 실행 전략
```bash
# 변경된 파일만 테스트
npm test -- --onlyChanged

# 실패한 테스트만 재실행
npm test -- --onlyFailures

# 특정 패턴의 테스트만 실행
npm test -- --testNamePattern="should calculate"

# 커버리지 없이 빠른 실행
npm test -- --passWithNoTests --watchAll=false
```

## TDD 체크리스트

### 테스트 작성 전
- [ ] 요구사항 명확히 이해
- [ ] 테스트 케이스 시나리오 작성
- [ ] 테스트 데이터 준비
- [ ] 의존성 식별 및 모킹 계획

### Red 단계
- [ ] 실패하는 테스트 작성
- [ ] 테스트가 올바른 이유로 실패하는지 확인
- [ ] 테스트 코드의 가독성 검토

### Green 단계
- [ ] 테스트를 통과하는 최소한의 코드 작성
- [ ] 모든 기존 테스트가 여전히 통과하는지 확인
- [ ] 코드 중복 최소화

### Refactor 단계
- [ ] 코드 품질 개선
- [ ] 테스트 코드도 함께 리팩토링
- [ ] 성능 최적화 고려
- [ ] 문서화 업데이트
