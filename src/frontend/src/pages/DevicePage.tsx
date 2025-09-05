import React, { useState, useEffect } from 'react';
import toast from 'react-hot-toast';

const DevicePage: React.FC = () => {
  const [userCode, setUserCode] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [message, setMessage] = useState('');

  // URL에서 user_code 파라미터 가져오기
  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search);
    const code = urlParams.get('user_code');
    if (code) {
      setUserCode(code);
    }
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!userCode.trim()) {
      setMessage('코드를 입력해주세요.');
      return;
    }

    setIsLoading(true);
    setMessage('');

    try {
      const response = await fetch('/api/v1/auth/device/approve', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ user_code: userCode }),
      });

      if (response.ok) {
        const result = await response.json();
        setMessage('✅ 디바이스 인증이 완료되었습니다! VS Code로 돌아가세요.');
        toast.success('디바이스 인증 완료!');
      } else {
        const error = await response.json();
        setMessage(`❌ 인증에 실패했습니다: ${error.error || '알 수 없는 오류'}`);
        toast.error('인증 실패');
      }
    } catch (error) {
      setMessage('❌ 네트워크 오류가 발생했습니다. 다시 시도해주세요.');
      toast.error('네트워크 오류');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div>
          <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
            TeamSync Pro
          </h2>
          <p className="mt-2 text-center text-sm text-gray-600">
            VS Code Extension 디바이스 인증
          </p>
        </div>
        
        <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
          <div>
            <label htmlFor="user-code" className="block text-sm font-medium text-gray-700">
              인증 코드
            </label>
            <input
              id="user-code"
              name="user-code"
              type="text"
              value={userCode}
              onChange={(e) => setUserCode(e.target.value.toUpperCase())}
              placeholder="예: ABC123"
              className="mt-1 appearance-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm"
              required
            />
          </div>

          <div>
            <button
              type="submit"
              disabled={isLoading}
              className="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50"
            >
              {isLoading ? '인증 중...' : '디바이스 인증'}
            </button>
          </div>

          {message && (
            <div className={`text-center text-sm ${message.includes('✅') ? 'text-green-600' : 'text-red-600'}`}>
              {message}
            </div>
          )}
        </form>

        <div className="text-center">
          <p className="text-xs text-gray-500">
            VS Code Extension에서 표시된 코드를 입력하세요
          </p>
        </div>
      </div>
    </div>
  );
};

export default DevicePage;
