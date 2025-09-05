# 보안 프롬프트 (Security Prompt)

## OWASP Top 10 기반 보안 체크리스트

### 1. 인젝션 (Injection)
```javascript
// ❌ SQL 인젝션 취약점
const query = `SELECT * FROM users WHERE id = ${userId}`;

// ✅ 매개변수화된 쿼리 사용
const query = 'SELECT * FROM users WHERE id = ?';
const result = await db.query(query, [userId]);

// ❌ NoSQL 인젝션 취약점
const user = await User.findOne({ email: req.body.email });

// ✅ 입력 검증 및 스키마 사용
const { error, value } = userSchema.validate(req.body);
if (error) throw new ValidationError(error.details[0].message);
const user = await User.findOne({ email: value.email });
```

### 2. 인증 실패 (Broken Authentication)
```javascript
// ✅ 안전한 패스워드 해싱
const bcrypt = require('bcrypt');
const saltRounds = 12;

async function hashPassword(password) {
  // 패스워드 강도 검증
  if (password.length < 8) {
    throw new Error('패스워드는 최소 8자 이상이어야 합니다');
  }
  
  const hashedPassword = await bcrypt.hash(password, saltRounds);
  return hashedPassword;
}

// ✅ JWT 토큰 보안 설정
const jwt = require('jsonwebtoken');

function generateToken(user) {
  return jwt.sign(
    { 
      userId: user.id, 
      email: user.email 
    },
    process.env.JWT_SECRET,
    { 
      expiresIn: '15m',  // 짧은 만료 시간
      issuer: 'your-app',
      audience: 'your-app-users'
    }
  );
}

// ✅ 세션 관리
const session = require('express-session');
const MongoStore = require('connect-mongo');

app.use(session({
  secret: process.env.SESSION_SECRET,
  resave: false,
  saveUninitialized: false,
  store: MongoStore.create({
    mongoUrl: process.env.MONGODB_URI
  }),
  cookie: {
    secure: process.env.NODE_ENV === 'production', // HTTPS에서만
    httpOnly: true, // XSS 방지
    maxAge: 1000 * 60 * 15 // 15분
  }
}));
```

### 3. 민감한 데이터 노출 (Sensitive Data Exposure)
```javascript
// ✅ 데이터 암호화
const crypto = require('crypto');

class DataEncryption {
  constructor() {
    this.algorithm = 'aes-256-gcm';
    this.secretKey = process.env.ENCRYPTION_KEY;
  }

  encrypt(text) {
    const iv = crypto.randomBytes(16);
    const cipher = crypto.createCipher(this.algorithm, this.secretKey, iv);
    
    let encrypted = cipher.update(text, 'utf8', 'hex');
    encrypted += cipher.final('hex');
    
    const authTag = cipher.getAuthTag();
    
    return {
      encrypted,
      iv: iv.toString('hex'),
      authTag: authTag.toString('hex')
    };
  }

  decrypt(encryptedData) {
    const decipher = crypto.createDecipher(
      this.algorithm, 
      this.secretKey, 
      Buffer.from(encryptedData.iv, 'hex')
    );
    
    decipher.setAuthTag(Buffer.from(encryptedData.authTag, 'hex'));
    
    let decrypted = decipher.update(encryptedData.encrypted, 'hex', 'utf8');
    decrypted += decipher.final('utf8');
    
    return decrypted;
  }
}

// ✅ 민감한 정보 로깅 방지
const winston = require('winston');

const logger = winston.createLogger({
  format: winston.format.combine(
    winston.format.timestamp(),
    winston.format.json(),
    winston.format.printf(info => {
      // 민감한 정보 마스킹
      const sensitiveFields = ['password', 'ssn', 'creditCard'];
      const logData = { ...info };
      
      sensitiveFields.forEach(field => {
        if (logData[field]) {
          logData[field] = '***MASKED***';
        }
      });
      
      return JSON.stringify(logData);
    })
  ),
  transports: [
    new winston.transports.File({ filename: 'app.log' })
  ]
});
```

### 4. XML 외부 엔티티 (XXE)
```javascript
// ✅ 안전한 XML 파싱
const libxmljs = require('libxmljs');

function parseXMLSafely(xmlString) {
  const options = {
    noent: false,    // 외부 엔티티 비활성화
    nonet: true,     // 네트워크 접근 비활성화
    noblanks: true   // 공백 노드 제거
  };
  
  try {
    const xmlDoc = libxmljs.parseXml(xmlString, options);
    return xmlDoc;
  } catch (error) {
    throw new Error('Invalid XML format');
  }
}
```

### 5. 접근 제어 실패 (Broken Access Control)
```javascript
// ✅ 역할 기반 접근 제어 (RBAC)
const permissions = {
  admin: ['read', 'write', 'delete', 'manage_users'],
  editor: ['read', 'write'],
  viewer: ['read']
};

function hasPermission(userRole, requiredPermission) {
  const userPermissions = permissions[userRole] || [];
  return userPermissions.includes(requiredPermission);
}

// ✅ 리소스 소유권 검증
async function checkResourceOwnership(userId, resourceId, resourceType) {
  const resource = await db.collection(resourceType).findOne({ 
    _id: resourceId 
  });
  
  if (!resource) {
    throw new Error('Resource not found');
  }
  
  if (resource.ownerId !== userId) {
    throw new Error('Access denied: Not resource owner');
  }
  
  return resource;
}

// ✅ 미들웨어로 권한 검사
function requirePermission(permission) {
  return (req, res, next) => {
    const userRole = req.user?.role;
    
    if (!hasPermission(userRole, permission)) {
      return res.status(403).json({ 
        error: 'Insufficient permissions' 
      });
    }
    
    next();
  };
}

// 사용 예시
app.delete('/api/users/:id', 
  authenticateToken,
  requirePermission('manage_users'),
  deleteUser
);
```

### 6. 보안 설정 오류 (Security Misconfiguration)
```javascript
// ✅ 보안 헤더 설정
const helmet = require('helmet');

app.use(helmet({
  contentSecurityPolicy: {
    directives: {
      defaultSrc: ["'self'"],
      styleSrc: ["'self'", "'unsafe-inline'"],
      scriptSrc: ["'self'"],
      imgSrc: ["'self'", "data:", "https:"],
    },
  },
  hsts: {
    maxAge: 31536000,
    includeSubDomains: true,
    preload: true
  }
}));

// ✅ CORS 설정
const cors = require('cors');

app.use(cors({
  origin: process.env.ALLOWED_ORIGINS?.split(',') || 'http://localhost:3000',
  credentials: true,
  methods: ['GET', 'POST', 'PUT', 'DELETE'],
  allowedHeaders: ['Content-Type', 'Authorization']
}));

// ✅ 환경별 설정 분리
const config = {
  development: {
    debug: true,
    logLevel: 'debug'
  },
  production: {
    debug: false,
    logLevel: 'error',
    ssl: true
  }
};

const currentConfig = config[process.env.NODE_ENV] || config.development;
```

### 7. 크로스 사이트 스크립팅 (XSS)
```javascript
// ✅ 입력 검증 및 출력 인코딩
const validator = require('validator');
const xss = require('xss');

function sanitizeInput(input) {
  if (typeof input !== 'string') {
    return input;
  }
  
  // HTML 태그 제거
  const sanitized = xss(input, {
    whiteList: {}, // 모든 HTML 태그 제거
    stripIgnoreTag: true,
    stripIgnoreTagBody: ['script']
  });
  
  return validator.escape(sanitized);
}

// ✅ CSP (Content Security Policy) 설정
app.use((req, res, next) => {
  res.setHeader(
    'Content-Security-Policy',
    "default-src 'self'; " +
    "script-src 'self' 'unsafe-inline'; " +
    "style-src 'self' 'unsafe-inline'; " +
    "img-src 'self' data: https:;"
  );
  next();
});

// ✅ 템플릿 엔진 자동 이스케이프
// Handlebars 예시
const handlebars = require('handlebars');

// 자동 이스케이프 활성화 (기본값)
const template = handlebars.compile('Hello {{name}}!');
const result = template({ name: '<script>alert("xss")</script>' });
// 결과: Hello &lt;script&gt;alert(&quot;xss&quot;)&lt;/script&gt;!
```

### 8. 안전하지 않은 역직렬화 (Insecure Deserialization)
```javascript
// ❌ 안전하지 않은 역직렬화
const data = JSON.parse(untrustedInput);

// ✅ 스키마 검증을 통한 안전한 역직렬화
const Joi = require('joi');

const userSchema = Joi.object({
  name: Joi.string().max(100).required(),
  email: Joi.string().email().required(),
  age: Joi.number().integer().min(0).max(150)
});

function safeDeserialize(jsonString, schema) {
  try {
    const data = JSON.parse(jsonString);
    const { error, value } = schema.validate(data);
    
    if (error) {
      throw new Error(`Validation error: ${error.details[0].message}`);
    }
    
    return value;
  } catch (error) {
    throw new Error('Invalid JSON or validation failed');
  }
}

// 사용 예시
const userData = safeDeserialize(req.body, userSchema);
```

### 9. 알려진 취약점이 있는 구성요소 사용
```javascript
// ✅ 의존성 보안 검사 자동화
// package.json scripts
{
  "scripts": {
    "audit": "npm audit",
    "audit:fix": "npm audit fix",
    "security:check": "npm audit --audit-level moderate"
  }
}

// ✅ Snyk를 통한 취약점 모니터링
// .github/workflows/security.yml
name: Security Scan

on: [push, pull_request]

jobs:
  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run Snyk to check for vulnerabilities
        uses: snyk/actions/node@master
        env:
          SNYK_TOKEN: ${{ secrets.SNYK_TOKEN }}
```

### 10. 부족한 로깅 및 모니터링
```javascript
// ✅ 보안 이벤트 로깅
const winston = require('winston');

const securityLogger = winston.createLogger({
  level: 'info',
  format: winston.format.combine(
    winston.format.timestamp(),
    winston.format.json()
  ),
  transports: [
    new winston.transports.File({ 
      filename: 'security.log',
      level: 'warn'
    })
  ]
});

// 보안 이벤트 로깅 함수
function logSecurityEvent(event, details) {
  securityLogger.warn('Security Event', {
    event,
    timestamp: new Date().toISOString(),
    ip: details.ip,
    userAgent: details.userAgent,
    userId: details.userId,
    details
  });
}

// 사용 예시
app.post('/api/login', async (req, res) => {
  try {
    const user = await authenticateUser(req.body);
    
    // 성공적인 로그인 로깅
    logSecurityEvent('LOGIN_SUCCESS', {
      ip: req.ip,
      userAgent: req.get('User-Agent'),
      userId: user.id
    });
    
    res.json({ token: generateToken(user) });
  } catch (error) {
    // 실패한 로그인 시도 로깅
    logSecurityEvent('LOGIN_FAILURE', {
      ip: req.ip,
      userAgent: req.get('User-Agent'),
      email: req.body.email,
      error: error.message
    });
    
    res.status(401).json({ error: 'Authentication failed' });
  }
});
```

## 보안 테스트

### 1. 정적 보안 분석 (SAST)
```javascript
// ESLint 보안 규칙 설정
// .eslintrc.js
module.exports = {
  extends: [
    'eslint:recommended',
    'plugin:security/recommended'
  ],
  plugins: ['security'],
  rules: {
    'security/detect-object-injection': 'error',
    'security/detect-non-literal-regexp': 'error',
    'security/detect-unsafe-regex': 'error',
    'security/detect-buffer-noassert': 'error',
    'security/detect-child-process': 'error',
    'security/detect-disable-mustache-escape': 'error',
    'security/detect-eval-with-expression': 'error',
    'security/detect-no-csrf-before-method-override': 'error',
    'security/detect-non-literal-fs-filename': 'error',
    'security/detect-non-literal-require': 'error',
    'security/detect-possible-timing-attacks': 'error',
    'security/detect-pseudoRandomBytes': 'error'
  }
};
```

### 2. 동적 보안 테스트 (DAST)
```javascript
// OWASP ZAP 자동화 스크립트
const ZapClient = require('zaproxy');

async function runSecurityScan(targetUrl) {
  const zaproxy = new ZapClient({
    proxy: 'http://localhost:8080'
  });

  try {
    // 스파이더링으로 URL 수집
    await zaproxy.spider.scan(targetUrl);
    
    // 능동적 스캔 실행
    const scanId = await zaproxy.ascan.scan(targetUrl);
    
    // 스캔 완료 대기
    let progress = 0;
    while (progress < 100) {
      await new Promise(resolve => setTimeout(resolve, 5000));
      progress = await zaproxy.ascan.status(scanId);
      console.log(`Scan progress: ${progress}%`);
    }
    
    // 결과 리포트 생성
    const report = await zaproxy.core.htmlreport();
    require('fs').writeFileSync('security-report.html', report);
    
    console.log('Security scan completed. Report saved to security-report.html');
  } catch (error) {
    console.error('Security scan failed:', error);
  }
}
```

### 3. 침투 테스트 체크리스트
```markdown
## 웹 애플리케이션 침투 테스트 체크리스트

### 인증 및 세션 관리
- [ ] 약한 패스워드 정책 테스트
- [ ] 브루트 포스 공격 방어 테스트
- [ ] 세션 고정 공격 테스트
- [ ] 세션 하이재킹 테스트
- [ ] 로그아웃 후 세션 무효화 테스트

### 입력 검증
- [ ] SQL 인젝션 테스트
- [ ] XSS (Cross-Site Scripting) 테스트
- [ ] CSRF (Cross-Site Request Forgery) 테스트
- [ ] 파일 업로드 취약점 테스트
- [ ] 경로 순회 공격 테스트

### 접근 제어
- [ ] 수직 권한 상승 테스트
- [ ] 수평 권한 상승 테스트
- [ ] 직접 객체 참조 테스트
- [ ] 관리자 기능 접근 테스트

### 비즈니스 로직
- [ ] 가격 조작 테스트
- [ ] 수량 조작 테스트
- [ ] 워크플로우 우회 테스트
- [ ] 레이스 컨디션 테스트
```

## 보안 모니터링

### 1. 실시간 위협 탐지
```javascript
// 비정상적인 로그인 시도 탐지
const loginAttempts = new Map();

function detectSuspiciousLogin(ip, email) {
  const key = `${ip}:${email}`;
  const attempts = loginAttempts.get(key) || { count: 0, firstAttempt: Date.now() };
  
  attempts.count++;
  attempts.lastAttempt = Date.now();
  
  loginAttempts.set(key, attempts);
  
  // 5분 내 5회 이상 실패 시 알림
  if (attempts.count >= 5 && (attempts.lastAttempt - attempts.firstAttempt) < 300000) {
    alertSecurityTeam('BRUTE_FORCE_DETECTED', {
      ip,
      email,
      attempts: attempts.count,
      timeWindow: attempts.lastAttempt - attempts.firstAttempt
    });
    
    // IP 차단
    blockIP(ip, 3600000); // 1시간 차단
  }
}

// 비정상적인 API 호출 패턴 탐지
const apiCallTracker = new Map();

function detectAbnormalAPIUsage(userId, endpoint) {
  const key = `${userId}:${endpoint}`;
  const calls = apiCallTracker.get(key) || [];
  const now = Date.now();
  
  // 최근 1분간의 호출만 유지
  const recentCalls = calls.filter(timestamp => now - timestamp < 60000);
  recentCalls.push(now);
  
  apiCallTracker.set(key, recentCalls);
  
  // 1분에 100회 이상 호출 시 알림
  if (recentCalls.length > 100) {
    alertSecurityTeam('API_ABUSE_DETECTED', {
      userId,
      endpoint,
      callCount: recentCalls.length
    });
    
    // 사용자 일시 차단
    temporarilyBlockUser(userId, 300000); // 5분 차단
  }
}
```

### 2. 보안 대시보드
```javascript
// 보안 메트릭 수집
const securityMetrics = {
  loginFailures: 0,
  blockedIPs: new Set(),
  suspiciousActivities: 0,
  vulnerabilityScans: 0
};

function updateSecurityMetrics(event, data) {
  switch (event) {
    case 'LOGIN_FAILURE':
      securityMetrics.loginFailures++;
      break;
    case 'IP_BLOCKED':
      securityMetrics.blockedIPs.add(data.ip);
      break;
    case 'SUSPICIOUS_ACTIVITY':
      securityMetrics.suspiciousActivities++;
      break;
    case 'VULNERABILITY_SCAN':
      securityMetrics.vulnerabilityScans++;
      break;
  }
  
  // 실시간 대시보드 업데이트
  broadcastMetricsUpdate(securityMetrics);
}

// WebSocket을 통한 실시간 알림
const WebSocket = require('ws');
const wss = new WebSocket.Server({ port: 8080 });

function broadcastSecurityAlert(alert) {
  const message = JSON.stringify({
    type: 'SECURITY_ALERT',
    timestamp: new Date().toISOString(),
    alert
  });
  
  wss.clients.forEach(client => {
    if (client.readyState === WebSocket.OPEN) {
      client.send(message);
    }
  });
}
```

## 보안 체크리스트

### 개발 단계
- [ ] 입력 검증 구현
- [ ] 출력 인코딩 적용
- [ ] 인증 및 권한 부여 구현
- [ ] 보안 헤더 설정
- [ ] 에러 처리 및 로깅

### 테스트 단계
- [ ] 정적 보안 분석 실행
- [ ] 동적 보안 테스트 실행
- [ ] 침투 테스트 수행
- [ ] 의존성 취약점 검사
- [ ] 보안 코드 리뷰

### 배포 단계
- [ ] 보안 설정 검토
- [ ] 모니터링 시스템 구성
- [ ] 인시던트 대응 계획 수립
- [ ] 백업 및 복구 계획 수립
- [ ] 보안 교육 및 문서화
