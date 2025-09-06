# 디버깅 프롬프트 (Debugging Prompt)

## 체계적 디버깅 방법론

### 1. 문제 정의 및 재현
```markdown
## 버그 리포트 템플릿
- **현상**: 무엇이 잘못되었는가?
- **예상 결과**: 어떻게 동작해야 하는가?
- **재현 단계**: 어떻게 문제를 재현할 수 있는가?
- **환경 정보**: OS, 브라우저, 버전 등
- **발생 빈도**: 항상/가끔/특정 조건에서만
```

### 2. 가설 수립 및 검증
```javascript
// 가설 기반 디버깅 예시
function debugUserLogin(email, password) {
  console.log('=== 디버깅 시작 ===');
  
  // 가설 1: 입력값 문제
  console.log('입력값 검증:', { email, password: '***' });
  if (!email || !password) {
    console.log('❌ 가설 1 확인: 입력값 누락');
    return;
  }
  
  // 가설 2: 네트워크 문제
  console.log('API 호출 시작');
  fetch('/api/login', { method: 'POST', body: JSON.stringify({ email, password }) })
    .then(response => {
      console.log('응답 상태:', response.status);
      if (!response.ok) {
        console.log('❌ 가설 2 확인: 서버 응답 오류');
      }
      return response.json();
    })
    .catch(error => {
      console.log('❌ 네트워크 오류:', error);
    });
}
```

## 디버깅 도구 활용법

### 1. 브라우저 개발자 도구
```javascript
// Console API 활용
console.group('사용자 인증 프로세스');
console.time('로그인 시간');
console.log('사용자 입력:', { email });
console.warn('비밀번호 강도 약함');
console.error('인증 실패');
console.timeEnd('로그인 시간');
console.groupEnd();

// 조건부 로깅
const DEBUG = process.env.NODE_ENV === 'development';
DEBUG && console.log('디버그 정보:', debugData);

// 스택 트레이스
console.trace('함수 호출 경로 추적');
```

### 2. Node.js 디버깅
```javascript
// 내장 디버거 사용
const util = require('util');

function debugFunction(data) {
  // 객체 상세 출력
  console.log(util.inspect(data, { depth: null, colors: true }));
  
  // 디버거 중단점
  debugger;
  
  // 성능 측정
  console.time('처리 시간');
  processData(data);
  console.timeEnd('처리 시간');
}

// 메모리 사용량 모니터링
setInterval(() => {
  const memUsage = process.memoryUsage();
  console.log('메모리 사용량:', {
    rss: Math.round(memUsage.rss / 1024 / 1024) + 'MB',
    heapUsed: Math.round(memUsage.heapUsed / 1024 / 1024) + 'MB'
  });
}, 5000);
```

### 3. VS Code 디버깅 설정
```json
// .vscode/launch.json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Node.js 디버그",
      "type": "node",
      "request": "launch",
      "program": "${workspaceFolder}/src/index.js",
      "env": {
        "NODE_ENV": "development"
      },
      "console": "integratedTerminal",
      "skipFiles": ["<node_internals>/**"]
    },
    {
      "name": "Jest 테스트 디버그",
      "type": "node",
      "request": "launch",
      "program": "${workspaceFolder}/node_modules/.bin/jest",
      "args": ["--runInBand", "--testNamePattern=특정테스트"],
      "console": "integratedTerminal"
    }
  ]
}
```

## 로깅 전략

### 1. 구조화된 로깅
```javascript
// Winston 로거 설정
const winston = require('winston');

const logger = winston.createLogger({
  level: 'info',
  format: winston.format.combine(
    winston.format.timestamp(),
    winston.format.errors({ stack: true }),
    winston.format.json()
  ),
  transports: [
    new winston.transports.File({ filename: 'error.log', level: 'error' }),
    new winston.transports.File({ filename: 'combined.log' })
  ]
});

// 사용 예시
logger.info('사용자 로그인 시도', {
  userId: user.id,
  email: user.email,
  timestamp: new Date().toISOString(),
  userAgent: req.headers['user-agent']
});
```

### 2. 컨텍스트 기반 로깅
```javascript
// 요청별 추적 ID 생성
const { v4: uuidv4 } = require('uuid');

function createRequestContext(req, res, next) {
  req.traceId = uuidv4();
  res.setHeader('X-Trace-ID', req.traceId);
  
  logger.info('요청 시작', {
    traceId: req.traceId,
    method: req.method,
    url: req.url,
    ip: req.ip
  });
  
  next();
}

// 비즈니스 로직에서 사용
function processOrder(req, orderId) {
  logger.info('주문 처리 시작', {
    traceId: req.traceId,
    orderId,
    action: 'process_order'
  });
  
  try {
    // 주문 처리 로직
    logger.info('주문 처리 완료', {
      traceId: req.traceId,
      orderId,
      status: 'success'
    });
  } catch (error) {
    logger.error('주문 처리 실패', {
      traceId: req.traceId,
      orderId,
      error: error.message,
      stack: error.stack
    });
  }
}
```

## 성능 디버깅

### 1. 프로파일링
```javascript
// CPU 프로파일링
const v8Profiler = require('v8-profiler-next');

function startProfiling(name) {
  v8Profiler.startProfiling(name, true);
}

function stopProfiling(name) {
  const profile = v8Profiler.stopProfiling(name);
  profile.export((error, result) => {
    if (!error) {
      require('fs').writeFileSync(`${name}.cpuprofile`, result);
    }
  });
}

// 사용 예시
startProfiling('heavy-computation');
performHeavyComputation();
stopProfiling('heavy-computation');
```

### 2. 메모리 누수 탐지
```javascript
// 메모리 사용량 추적
function trackMemoryUsage() {
  const usage = process.memoryUsage();
  return {
    rss: usage.rss / 1024 / 1024, // MB
    heapUsed: usage.heapUsed / 1024 / 1024,
    heapTotal: usage.heapTotal / 1024 / 1024,
    external: usage.external / 1024 / 1024
  };
}

// 주기적 메모리 체크
setInterval(() => {
  const memory = trackMemoryUsage();
  if (memory.heapUsed > 100) { // 100MB 초과 시 경고
    logger.warn('높은 메모리 사용량 감지', memory);
  }
}, 30000);
```

## 네트워크 디버깅

### 1. HTTP 요청 추적
```javascript
// Axios 인터셉터로 요청/응답 로깅
axios.interceptors.request.use(
  config => {
    logger.info('HTTP 요청', {
      method: config.method,
      url: config.url,
      headers: config.headers,
      data: config.data
    });
    return config;
  },
  error => {
    logger.error('HTTP 요청 오류', error);
    return Promise.reject(error);
  }
);

axios.interceptors.response.use(
  response => {
    logger.info('HTTP 응답', {
      status: response.status,
      statusText: response.statusText,
      data: response.data
    });
    return response;
  },
  error => {
    logger.error('HTTP 응답 오류', {
      status: error.response?.status,
      statusText: error.response?.statusText,
      data: error.response?.data
    });
    return Promise.reject(error);
  }
);
```

### 2. 데이터베이스 쿼리 디버깅
```javascript
// Sequelize 쿼리 로깅
const sequelize = new Sequelize(database, username, password, {
  host: 'localhost',
  dialect: 'postgres',
  logging: (sql, timing) => {
    logger.info('DB 쿼리 실행', {
      sql,
      timing,
      timestamp: new Date().toISOString()
    });
  }
});

// 느린 쿼리 감지
const originalQuery = sequelize.query;
sequelize.query = function(...args) {
  const start = Date.now();
  return originalQuery.apply(this, args).then(result => {
    const duration = Date.now() - start;
    if (duration > 1000) { // 1초 이상 소요된 쿼리
      logger.warn('느린 쿼리 감지', {
        sql: args[0],
        duration: `${duration}ms`
      });
    }
    return result;
  });
};
```

## 에러 추적 및 모니터링

### 1. 전역 에러 핸들러
```javascript
// 처리되지 않은 예외 캐치
process.on('uncaughtException', (error) => {
  logger.error('처리되지 않은 예외', {
    error: error.message,
    stack: error.stack
  });
  
  // 안전한 종료
  process.exit(1);
});

process.on('unhandledRejection', (reason, promise) => {
  logger.error('처리되지 않은 Promise 거부', {
    reason,
    promise
  });
});

// Express 에러 미들웨어
function errorHandler(err, req, res, next) {
  logger.error('Express 에러', {
    traceId: req.traceId,
    error: err.message,
    stack: err.stack,
    url: req.url,
    method: req.method
  });
  
  res.status(500).json({
    error: '서버 내부 오류',
    traceId: req.traceId
  });
}
```

### 2. 에러 분류 및 알림
```javascript
// 에러 심각도 분류
const ErrorSeverity = {
  LOW: 'low',
  MEDIUM: 'medium',
  HIGH: 'high',
  CRITICAL: 'critical'
};

function classifyError(error) {
  if (error.name === 'ValidationError') return ErrorSeverity.LOW;
  if (error.name === 'AuthenticationError') return ErrorSeverity.MEDIUM;
  if (error.name === 'DatabaseError') return ErrorSeverity.HIGH;
  if (error.name === 'SystemError') return ErrorSeverity.CRITICAL;
  return ErrorSeverity.MEDIUM;
}

function handleError(error, context = {}) {
  const severity = classifyError(error);
  
  logger.error('에러 발생', {
    ...context,
    error: error.message,
    stack: error.stack,
    severity
  });
  
  // 심각한 에러는 즉시 알림
  if (severity === ErrorSeverity.CRITICAL) {
    sendAlert({
      message: `심각한 에러 발생: ${error.message}`,
      context
    });
  }
}
```

## 디버깅 체크리스트

### 문제 발생 시
- [ ] 에러 메시지 및 스택 트레이스 확인
- [ ] 재현 가능한 최소 케이스 작성
- [ ] 관련 로그 및 모니터링 데이터 수집
- [ ] 최근 변경사항 검토

### 디버깅 진행 시
- [ ] 가설 수립 및 체계적 검증
- [ ] 적절한 디버깅 도구 활용
- [ ] 중간 결과 문서화
- [ ] 팀원과 진행상황 공유

### 문제 해결 후
- [ ] 근본 원인 분석 및 문서화
- [ ] 재발 방지 대책 수립
- [ ] 모니터링 및 알림 개선
- [ ] 팀 지식 공유
