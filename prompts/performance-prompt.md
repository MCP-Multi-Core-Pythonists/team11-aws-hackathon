# 성능 최적화 프롬프트 (Performance Optimization Prompt)

## 성능 측정 기준

### 1. 웹 성능 지표 (Web Vitals)
```javascript
// Core Web Vitals 측정
function measureWebVitals() {
  // Largest Contentful Paint (LCP)
  new PerformanceObserver((entryList) => {
    const entries = entryList.getEntries();
    const lastEntry = entries[entries.length - 1];
    console.log('LCP:', lastEntry.startTime);
  }).observe({ entryTypes: ['largest-contentful-paint'] });

  // First Input Delay (FID)
  new PerformanceObserver((entryList) => {
    const entries = entryList.getEntries();
    entries.forEach((entry) => {
      console.log('FID:', entry.processingStart - entry.startTime);
    });
  }).observe({ entryTypes: ['first-input'] });

  // Cumulative Layout Shift (CLS)
  let clsValue = 0;
  new PerformanceObserver((entryList) => {
    for (const entry of entryList.getEntries()) {
      if (!entry.hadRecentInput) {
        clsValue += entry.value;
      }
    }
    console.log('CLS:', clsValue);
  }).observe({ entryTypes: ['layout-shift'] });
}
```

### 2. 서버 성능 지표
```javascript
// 응답 시간 측정
const responseTimeMiddleware = (req, res, next) => {
  const start = Date.now();
  
  res.on('finish', () => {
    const duration = Date.now() - start;
    console.log(`${req.method} ${req.url} - ${duration}ms`);
    
    // 느린 요청 감지
    if (duration > 1000) {
      logger.warn('느린 응답 감지', {
        method: req.method,
        url: req.url,
        duration: `${duration}ms`
      });
    }
  });
  
  next();
};

// 메모리 사용량 모니터링
function monitorMemoryUsage() {
  const usage = process.memoryUsage();
  return {
    rss: Math.round(usage.rss / 1024 / 1024), // MB
    heapUsed: Math.round(usage.heapUsed / 1024 / 1024),
    heapTotal: Math.round(usage.heapTotal / 1024 / 1024)
  };
}
```

## 프론트엔드 최적화 전략

### 1. 렌더링 최적화
```javascript
// React 컴포넌트 최적화
const ExpensiveComponent = memo(({ data, onUpdate }) => {
  // 복잡한 계산을 메모이제이션
  const processedData = useMemo(() => {
    return data.map(item => ({
      ...item,
      computed: heavyComputation(item)
    }));
  }, [data]);

  // 콜백 함수 메모이제이션
  const handleClick = useCallback((id) => {
    onUpdate(id);
  }, [onUpdate]);

  return (
    <div>
      {processedData.map(item => (
        <Item 
          key={item.id} 
          data={item} 
          onClick={() => handleClick(item.id)} 
        />
      ))}
    </div>
  );
});

// 가상화를 통한 대용량 리스트 최적화
import { FixedSizeList as List } from 'react-window';

const VirtualizedList = ({ items }) => (
  <List
    height={600}
    itemCount={items.length}
    itemSize={50}
    itemData={items}
  >
    {({ index, style, data }) => (
      <div style={style}>
        {data[index].name}
      </div>
    )}
  </List>
);
```

### 2. 번들 최적화
```javascript
// 웹팩 설정 최적화
module.exports = {
  optimization: {
    splitChunks: {
      chunks: 'all',
      cacheGroups: {
        vendor: {
          test: /[\\/]node_modules[\\/]/,
          name: 'vendors',
          chunks: 'all',
        },
        common: {
          name: 'common',
          minChunks: 2,
          chunks: 'all',
          enforce: true,
        },
      },
    },
    usedExports: true, // Tree shaking 활성화
    sideEffects: false,
  },
  
  // 압축 설정
  plugins: [
    new CompressionPlugin({
      algorithm: 'gzip',
      test: /\.(js|css|html|svg)$/,
      threshold: 8192,
      minRatio: 0.8,
    }),
  ],
};

// 동적 import를 통한 코드 스플리팅
const LazyComponent = lazy(() => 
  import('./HeavyComponent').then(module => ({
    default: module.HeavyComponent
  }))
);
```

### 3. 이미지 최적화
```javascript
// 이미지 지연 로딩
const LazyImage = ({ src, alt, ...props }) => {
  const [imageSrc, setImageSrc] = useState('');
  const [imageRef, isIntersecting] = useIntersectionObserver({
    threshold: 0.1,
  });

  useEffect(() => {
    if (isIntersecting) {
      setImageSrc(src);
    }
  }, [isIntersecting, src]);

  return (
    <img
      ref={imageRef}
      src={imageSrc}
      alt={alt}
      loading="lazy"
      {...props}
    />
  );
};

// WebP 형식 지원 확인
function supportsWebP() {
  const canvas = document.createElement('canvas');
  canvas.width = 1;
  canvas.height = 1;
  return canvas.toDataURL('image/webp').indexOf('webp') > -1;
}

// 적응형 이미지 로딩
const AdaptiveImage = ({ src, alt }) => {
  const webpSrc = src.replace(/\.(jpg|jpeg|png)$/, '.webp');
  const isWebPSupported = supportsWebP();
  
  return (
    <picture>
      {isWebPSupported && <source srcSet={webpSrc} type="image/webp" />}
      <img src={src} alt={alt} />
    </picture>
  );
};
```

## 백엔드 최적화 전략

### 1. 데이터베이스 최적화
```sql
-- 인덱스 최적화
CREATE INDEX CONCURRENTLY idx_users_email ON users(email);
CREATE INDEX CONCURRENTLY idx_orders_user_id_created_at ON orders(user_id, created_at);

-- 복합 인덱스 활용
CREATE INDEX CONCURRENTLY idx_products_category_price ON products(category, price);

-- 쿼리 최적화 (N+1 문제 해결)
-- Before: N+1 쿼리 발생
SELECT * FROM users;
-- 각 사용자마다 별도 쿼리
SELECT * FROM orders WHERE user_id = ?;

-- After: JOIN을 통한 최적화
SELECT u.*, o.* 
FROM users u 
LEFT JOIN orders o ON u.id = o.user_id;
```

```javascript
// ORM 최적화 (Sequelize 예시)
// Before: N+1 문제
const users = await User.findAll();
for (const user of users) {
  user.orders = await Order.findAll({ where: { userId: user.id } });
}

// After: Eager Loading
const users = await User.findAll({
  include: [{
    model: Order,
    as: 'orders'
  }]
});

// 페이지네이션 최적화
const { count, rows } = await User.findAndCountAll({
  limit: 20,
  offset: page * 20,
  order: [['createdAt', 'DESC']]
});
```

### 2. 캐싱 전략
```javascript
// Redis 캐싱 구현
const redis = require('redis');
const client = redis.createClient();

// 캐시 래퍼 함수
async function cacheWrapper(key, fetchFunction, ttl = 3600) {
  try {
    // 캐시에서 데이터 조회
    const cached = await client.get(key);
    if (cached) {
      return JSON.parse(cached);
    }
    
    // 캐시 미스 시 데이터 조회
    const data = await fetchFunction();
    
    // 캐시에 저장
    await client.setex(key, ttl, JSON.stringify(data));
    
    return data;
  } catch (error) {
    console.error('캐시 오류:', error);
    // 캐시 실패 시 원본 데이터 반환
    return await fetchFunction();
  }
}

// 사용 예시
app.get('/api/users/:id', async (req, res) => {
  const userId = req.params.id;
  const cacheKey = `user:${userId}`;
  
  const user = await cacheWrapper(
    cacheKey,
    () => User.findByPk(userId),
    1800 // 30분 캐시
  );
  
  res.json(user);
});

// 캐시 무효화
async function invalidateUserCache(userId) {
  await client.del(`user:${userId}`);
}
```

### 3. 비동기 처리 최적화
```javascript
// Promise.all을 활용한 병렬 처리
async function getUserDashboardData(userId) {
  const [user, orders, notifications, stats] = await Promise.all([
    User.findByPk(userId),
    Order.findAll({ where: { userId }, limit: 10 }),
    Notification.findAll({ where: { userId, read: false } }),
    getUserStats(userId)
  ]);
  
  return { user, orders, notifications, stats };
}

// 스트림을 활용한 대용량 데이터 처리
const fs = require('fs');
const csv = require('csv-parser');

function processLargeCSV(filePath) {
  return new Promise((resolve, reject) => {
    const results = [];
    let processedCount = 0;
    
    fs.createReadStream(filePath)
      .pipe(csv())
      .on('data', (data) => {
        // 배치 처리
        results.push(data);
        processedCount++;
        
        if (results.length >= 1000) {
          processBatch(results.splice(0, 1000));
        }
      })
      .on('end', () => {
        if (results.length > 0) {
          processBatch(results);
        }
        resolve(processedCount);
      })
      .on('error', reject);
  });
}
```

## 성능 모니터링

### 1. APM (Application Performance Monitoring)
```javascript
// New Relic 연동
const newrelic = require('newrelic');

// 커스텀 메트릭 추가
function trackCustomMetric(name, value) {
  newrelic.recordMetric(name, value);
}

// 트랜잭션 추적
async function processOrder(orderId) {
  return newrelic.startWebTransaction('/api/orders/process', async () => {
    const startTime = Date.now();
    
    try {
      const result = await orderService.process(orderId);
      
      // 성공 메트릭
      trackCustomMetric('Custom/OrderProcessing/Success', 1);
      trackCustomMetric('Custom/OrderProcessing/Duration', Date.now() - startTime);
      
      return result;
    } catch (error) {
      // 실패 메트릭
      trackCustomMetric('Custom/OrderProcessing/Error', 1);
      throw error;
    }
  });
}
```

### 2. 실시간 성능 대시보드
```javascript
// Prometheus 메트릭 수집
const client = require('prom-client');

// 커스텀 메트릭 정의
const httpRequestDuration = new client.Histogram({
  name: 'http_request_duration_seconds',
  help: 'HTTP 요청 처리 시간',
  labelNames: ['method', 'route', 'status_code'],
  buckets: [0.1, 0.5, 1, 2, 5]
});

const activeConnections = new client.Gauge({
  name: 'active_connections',
  help: '활성 연결 수'
});

// 미들웨어로 메트릭 수집
const metricsMiddleware = (req, res, next) => {
  const start = Date.now();
  
  res.on('finish', () => {
    const duration = (Date.now() - start) / 1000;
    httpRequestDuration
      .labels(req.method, req.route?.path || req.url, res.statusCode)
      .observe(duration);
  });
  
  next();
};
```

## 성능 테스트

### 1. 부하 테스트 (Load Testing)
```javascript
// Artillery.js 설정
// artillery.yml
config:
  target: 'http://localhost:3000'
  phases:
    - duration: 60
      arrivalRate: 10
    - duration: 120
      arrivalRate: 50
    - duration: 60
      arrivalRate: 100

scenarios:
  - name: "사용자 로그인 및 대시보드 조회"
    flow:
      - post:
          url: "/api/login"
          json:
            email: "test@example.com"
            password: "password"
      - get:
          url: "/api/dashboard"

// 실행 명령
// artillery run artillery.yml
```

### 2. 벤치마킹
```javascript
// Benchmark.js를 활용한 성능 비교
const Benchmark = require('benchmark');

const suite = new Benchmark.Suite();

// 테스트할 함수들
function forLoop(arr) {
  let sum = 0;
  for (let i = 0; i < arr.length; i++) {
    sum += arr[i];
  }
  return sum;
}

function reduceMethod(arr) {
  return arr.reduce((sum, num) => sum + num, 0);
}

const testArray = Array.from({ length: 10000 }, (_, i) => i);

suite
  .add('for loop', () => forLoop(testArray))
  .add('reduce method', () => reduceMethod(testArray))
  .on('cycle', (event) => {
    console.log(String(event.target));
  })
  .on('complete', function() {
    console.log('가장 빠른 방법: ' + this.filter('fastest').map('name'));
  })
  .run({ async: true });
```

## 성능 최적화 체크리스트

### 프론트엔드
- [ ] 번들 크기 분석 및 최적화
- [ ] 이미지 최적화 (WebP, 지연 로딩)
- [ ] 코드 스플리팅 적용
- [ ] 메모이제이션 활용
- [ ] 가상화 구현 (대용량 리스트)

### 백엔드
- [ ] 데이터베이스 쿼리 최적화
- [ ] 인덱스 적절성 검토
- [ ] 캐싱 전략 구현
- [ ] 비동기 처리 최적화
- [ ] 커넥션 풀 설정

### 인프라
- [ ] CDN 활용
- [ ] 로드 밸런싱 구성
- [ ] 캐시 헤더 설정
- [ ] 압축 활성화 (gzip, brotli)
- [ ] HTTP/2 적용
