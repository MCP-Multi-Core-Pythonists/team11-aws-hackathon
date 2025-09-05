# 리팩토링 프롬프트 (Refactoring Prompt)

## 리팩토링 우선순위 매트릭스

### 영향도와 난이도 기반 분류
```
높은 영향도, 낮은 난이도 → 즉시 실행 (Quick Wins)
높은 영향도, 높은 난이도 → 계획적 실행 (Major Projects)
낮은 영향도, 낮은 난이도 → 여유시간 활용 (Fill-ins)
낮은 영향도, 높은 난이도 → 실행 보류 (Questionable)
```

## 단계별 마이그레이션 전략

### 1. 점진적 리팩토링 방법
```javascript
// Phase 1: 기존 코드 유지하며 새 인터페이스 추가
class LegacyUserService {
  // 기존 메서드 유지
  getUserById(id) { /* legacy code */ }
  
  // 새 메서드 추가
  async getUserByIdV2(id) {
    // 개선된 로직
    return this.userRepository.findById(id);
  }
}

// Phase 2: 점진적 마이그레이션
// 새 코드에서는 V2 메서드 사용
// 기존 코드는 단계적으로 마이그레이션

// Phase 3: 레거시 코드 제거
```

### 2. 브랜치 전략
```bash
# Feature Flag를 활용한 안전한 배포
git checkout -b refactor/user-service
# 리팩토링 작업 수행
git checkout main
git merge refactor/user-service --no-ff
```

## 자동화 도구 활용법

### 1. 린터 설정 (ESLint)
```json
{
  "extends": ["eslint:recommended"],
  "rules": {
    "complexity": ["error", 10],
    "max-lines-per-function": ["error", 50],
    "no-duplicate-code": "error"
  }
}
```

### 2. 코드 품질 분석 도구
```bash
# SonarQube 실행
sonar-scanner \
  -Dsonar.projectKey=my-project \
  -Dsonar.sources=./src \
  -Dsonar.host.url=http://localhost:9000

# 코드 복잡도 측정
npx complexity-report src/ --format json
```

## Before/After 성능 비교 지표

### 1. 측정 항목
- **응답 시간 (Response Time)**: 평균, 95th percentile
- **처리량 (Throughput)**: 초당 요청 수 (RPS)
- **메모리 사용량**: 힙 메모리, 가비지 컬렉션 빈도
- **CPU 사용률**: 평균 CPU 점유율

### 2. 성능 테스트 예시
```javascript
// Before 측정
console.time('legacy-function');
const result1 = legacyFunction(data);
console.timeEnd('legacy-function');

// After 측정
console.time('refactored-function');
const result2 = refactoredFunction(data);
console.timeEnd('refactored-function');

// 메모리 사용량 측정
const memBefore = process.memoryUsage();
refactoredFunction(data);
const memAfter = process.memoryUsage();
console.log('Memory diff:', memAfter.heapUsed - memBefore.heapUsed);
```

## 테스트 유지 및 개선 방법

### 1. 테스트 우선 리팩토링
```javascript
// 1단계: 기존 동작을 보장하는 테스트 작성
describe('UserService', () => {
  it('should return user data for valid ID', async () => {
    const user = await userService.getUserById(1);
    expect(user).toHaveProperty('id', 1);
    expect(user).toHaveProperty('name');
  });
});

// 2단계: 리팩토링 수행
// 3단계: 테스트가 여전히 통과하는지 확인
```

### 2. 테스트 커버리지 유지
```bash
# 리팩토링 전 커버리지 측정
npm run test:coverage

# 리팩토링 후 커버리지 비교
# 커버리지가 감소하지 않도록 보장
```

## 롤백 계획

### 1. 안전한 배포 전략
```yaml
# Blue-Green 배포
apiVersion: apps/v1
kind: Deployment
metadata:
  name: app-blue
spec:
  replicas: 3
  selector:
    matchLabels:
      app: myapp
      version: blue
```

### 2. 모니터링 및 알림
```javascript
// 에러율 모니터링
const errorRate = errors / totalRequests;
if (errorRate > 0.05) {
  // 5% 이상 에러 발생 시 롤백
  triggerRollback();
}
```

## 리팩토링 체크리스트

### 시작 전
- [ ] 현재 코드의 테스트 커버리지 확인
- [ ] 성능 기준선(baseline) 측정
- [ ] 리팩토링 범위 및 목표 명확화
- [ ] 롤백 계획 수립

### 진행 중
- [ ] 작은 단위로 점진적 변경
- [ ] 각 단계마다 테스트 실행
- [ ] 코드 리뷰 진행
- [ ] 성능 영향도 측정

### 완료 후
- [ ] 전체 테스트 스위트 실행
- [ ] 성능 개선 효과 측정
- [ ] 문서 업데이트
- [ ] 팀원들에게 변경사항 공유

## 실제 리팩토링 예시

### Before: 복잡한 조건문
```javascript
function calculateDiscount(user, product, quantity) {
  if (user.type === 'premium' && product.category === 'electronics' && quantity > 10) {
    return product.price * quantity * 0.15;
  } else if (user.type === 'premium' && quantity > 5) {
    return product.price * quantity * 0.10;
  } else if (product.category === 'electronics' && quantity > 20) {
    return product.price * quantity * 0.08;
  }
  return 0;
}
```

### After: 전략 패턴 적용
```javascript
class DiscountCalculator {
  constructor() {
    this.strategies = [
      new PremiumElectronicsDiscount(),
      new PremiumDiscount(),
      new BulkElectronicsDiscount()
    ];
  }

  calculate(user, product, quantity) {
    const strategy = this.strategies.find(s => s.applies(user, product, quantity));
    return strategy ? strategy.calculate(user, product, quantity) : 0;
  }
}
```
