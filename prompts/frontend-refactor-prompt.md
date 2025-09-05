# 프론트엔드 리팩토링 프롬프트 (Frontend Refactoring Prompt)

## React 컴포넌트 리팩토링 전략

### 1. 컴포넌트 분리 기준
```javascript
// Before: 거대한 컴포넌트
function UserDashboard() {
  // 200+ 줄의 복잡한 로직
  return (
    <div>
      {/* 사용자 정보, 통계, 설정, 알림 등 모든 기능 */}
    </div>
  );
}

// After: 책임별 분리
function UserDashboard() {
  return (
    <div>
      <UserProfile />
      <UserStats />
      <UserSettings />
      <NotificationPanel />
    </div>
  );
}
```

### 2. 커스텀 훅 추출
```javascript
// Before: 컴포넌트 내 복잡한 로직
function UserList() {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    // 복잡한 데이터 페칭 로직
  }, []);

  return (/* JSX */);
}

// After: 커스텀 훅으로 분리
function useUsers() {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // 데이터 페칭 로직
  return { users, loading, error };
}

function UserList() {
  const { users, loading, error } = useUsers();
  return (/* JSX */);
}
```

## 성능 최적화 리팩토링

### 1. 메모이제이션 적용
```javascript
// Before: 불필요한 리렌더링
function ExpensiveComponent({ data, onUpdate }) {
  const processedData = processData(data); // 매번 실행
  
  return (
    <div>
      {processedData.map(item => (
        <Item key={item.id} data={item} onClick={onUpdate} />
      ))}
    </div>
  );
}

// After: 메모이제이션 적용
const ExpensiveComponent = memo(({ data, onUpdate }) => {
  const processedData = useMemo(() => processData(data), [data]);
  const handleUpdate = useCallback(onUpdate, [onUpdate]);
  
  return (
    <div>
      {processedData.map(item => (
        <Item key={item.id} data={item} onClick={handleUpdate} />
      ))}
    </div>
  );
});
```

### 2. 코드 스플리팅
```javascript
// Before: 모든 컴포넌트를 한 번에 로드
import UserDashboard from './UserDashboard';
import AdminPanel from './AdminPanel';
import Reports from './Reports';

// After: 지연 로딩 적용
const UserDashboard = lazy(() => import('./UserDashboard'));
const AdminPanel = lazy(() => import('./AdminPanel'));
const Reports = lazy(() => import('./Reports'));

function App() {
  return (
    <Suspense fallback={<Loading />}>
      <Routes>
        <Route path="/dashboard" element={<UserDashboard />} />
        <Route path="/admin" element={<AdminPanel />} />
        <Route path="/reports" element={<Reports />} />
      </Routes>
    </Suspense>
  );
}
```

## 상태 관리 리팩토링

### 1. Context API 최적화
```javascript
// Before: 단일 거대한 Context
const AppContext = createContext();

// After: 도메인별 Context 분리
const UserContext = createContext();
const ThemeContext = createContext();
const NotificationContext = createContext();

// Context 분리로 불필요한 리렌더링 방지
```

### 2. 상태 정규화
```javascript
// Before: 중첩된 상태 구조
const [state, setState] = useState({
  users: [
    { id: 1, name: 'John', posts: [{ id: 1, title: 'Post 1' }] }
  ]
});

// After: 정규화된 상태 구조
const [state, setState] = useState({
  users: { 1: { id: 1, name: 'John', postIds: [1] } },
  posts: { 1: { id: 1, title: 'Post 1', userId: 1 } }
});
```

## CSS 리팩토링

### 1. CSS-in-JS 최적화
```javascript
// Before: 인라인 스타일
function Button({ primary }) {
  return (
    <button
      style={{
        backgroundColor: primary ? '#007bff' : '#6c757d',
        color: 'white',
        padding: '8px 16px',
        border: 'none',
        borderRadius: '4px'
      }}
    >
      Click me
    </button>
  );
}

// After: styled-components 활용
const StyledButton = styled.button`
  background-color: ${props => props.primary ? '#007bff' : '#6c757d'};
  color: white;
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
`;
```

### 2. CSS 모듈화
```css
/* Before: 전역 CSS */
.button {
  padding: 10px;
}

.button-primary {
  background: blue;
}

/* After: CSS Modules */
.button {
  padding: 10px;
}

.primary {
  composes: button;
  background: blue;
}
```

## 번들 최적화

### 1. Tree Shaking 적용
```javascript
// Before: 전체 라이브러리 import
import _ from 'lodash';
import * as utils from './utils';

// After: 필요한 함수만 import
import { debounce } from 'lodash';
import { formatDate } from './utils';
```

### 2. 웹팩 설정 최적화
```javascript
// webpack.config.js
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
      },
    },
  },
};
```

## 접근성 개선

### 1. 시맨틱 HTML 적용
```javascript
// Before: div 남용
<div onClick={handleClick}>Click me</div>

// After: 적절한 시맨틱 태그
<button onClick={handleClick}>Click me</button>
```

### 2. ARIA 속성 추가
```javascript
// Before: 접근성 정보 부족
<div onClick={toggleMenu}>Menu</div>

// After: ARIA 속성 추가
<button
  onClick={toggleMenu}
  aria-expanded={isMenuOpen}
  aria-controls="menu-list"
>
  Menu
</button>
```

## 테스트 개선

### 1. 테스트 가능한 컴포넌트 구조
```javascript
// Before: 테스트하기 어려운 구조
function UserProfile() {
  const [user, setUser] = useState(null);
  
  useEffect(() => {
    fetch('/api/user').then(res => res.json()).then(setUser);
  }, []);
  
  return user ? <div>{user.name}</div> : <div>Loading...</div>;
}

// After: 의존성 주입으로 테스트 용이성 향상
function UserProfile({ userService = defaultUserService }) {
  const { user, loading } = useUser(userService);
  
  return loading ? <div>Loading...</div> : <div>{user.name}</div>;
}
```

## 리팩토링 체크리스트

### 성능 관련
- [ ] 불필요한 리렌더링 제거
- [ ] 메모이제이션 적용
- [ ] 코드 스플리팅 구현
- [ ] 번들 크기 최적화

### 코드 품질
- [ ] 컴포넌트 책임 분리
- [ ] 커스텀 훅 추출
- [ ] 상태 관리 최적화
- [ ] 타입 안정성 확보

### 사용자 경험
- [ ] 접근성 개선
- [ ] 로딩 상태 처리
- [ ] 에러 바운더리 구현
- [ ] 반응형 디자인 적용
