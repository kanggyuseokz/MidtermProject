import React, { useState, useEffect } from 'react';

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [activeTab, setActiveTab] = useState('users');
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [showRegister, setShowRegister] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [admins, setAdmins] = useState([]);
  const [logs, setLogs] = useState([]);
  const [currentPassword, setCurrentPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [newEmail, setNewEmail] = useState('');

  const handleLogin = async (e) => {
    e.preventDefault();
    try {
      const response = await fetch('http://localhost:5000/api/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password })
      });
      const result = await response.json();
      if (result.success) {
        setIsAuthenticated(true);
        setError('');
        fetchAdmins();
        fetchLogs();
      } else {
        setError(result.error || '로그인 실패');
      }
    } catch (err) {
      setError('서버 오류: 로그인 요청 실패');
    }
  };

  const handleRegister = async (e) => {
    e.preventDefault();
    const newAdmin = {
      name: e.target.name.value,
      username: e.target.newUsername.value,
      password: e.target.newPassword.value,
      email: e.target.email.value
    };
    try {
      const response = await fetch('http://localhost:5000/api/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newAdmin)
      });
      const result = await response.json();
      if (result.success) {
        alert('관리자 등록 완료. 승인 대기 중입니다.');
        setShowRegister(false);
      } else {
        alert(result.error || '등록 실패');
      }
    } catch (err) {
      alert('서버 오류: 관리자 등록 요청 실패');
    }
  };

  const fetchAdmins = async () => {
    try {
      const res = await fetch('http://localhost:5000/api/admins');
      const data = await res.json();
      setAdmins(data);
    } catch (err) {
      console.error('관리자 목록 불러오기 실패', err);
    }
  };

  const fetchLogs = async () => {
    try {
      const res = await fetch('http://localhost:5000/admin/logs');
      const data = await res.json();
      setLogs(data.map(log => `[${log.timestamp}] ${log.username} (${log.ip}): ${log.original} - ${log.attack_type} 탐지됨`));
    } catch (err) {
      console.error('로그 불러오기 실패', err);
    }
  };

  const updateAdminApproval = async (id, isApproved) => {
    try {
      const res = await fetch(`http://localhost:5000/api/approve/${id}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ isApproved })
      });
      const result = await res.json();
      if (result.success) {
        fetchAdmins();
      } else {
        alert(result.error || '변경 실패');
      }
    } catch (err) {
      alert('서버 오류: 승인 변경 실패');
    }
  };

  const deleteAdmin = async (id) => {
    try {
      const res = await fetch(`http://localhost:5000/api/admins/${id}`, {
        method: 'DELETE',
        headers: { 'Content-Type': 'application/json' }
      });
      const result = await res.json();
      if (result.success) {
        alert('삭제 완료');
        fetchAdmins();
      } else {
        alert(result.error || '삭제 실패');
      }
    } catch (err) {
      alert('서버 오류: 삭제 실패');
    }
  };

  const handleLogout = () => {
    setIsAuthenticated(false);
    setUsername('');
    setPassword('');
    setActiveTab('users');
    setAdmins([]);
    setLogs([]);
  };

  const handleProfileUpdate = async (e) => {
    e.preventDefault();
    try {
      const res = await fetch(`http://localhost:5000/api/admins/update`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, currentPassword, newPassword, email: newEmail })
      });
      const result = await res.json();
      if (result.success) {
        alert('정보 수정 완료');
        setCurrentPassword('');
        setNewPassword('');
        setNewEmail('');
      } else {
        alert(result.error || '정보 수정 실패');
      }
    } catch (err) {
      alert('서버 오류: 수정 실패');
    }
  };

  useEffect(() => {
    if (isAuthenticated) {
      fetchAdmins();
      fetchLogs();
    }
  }, [isAuthenticated]);

  const users = [
    { username: '강규석', ip: '192.168.0.1' },
    { username: '오정현', ip: '10.0.0.12' }
  ];

  const filteredLogs = logs.filter(log => log.includes(searchTerm));

  if (!isAuthenticated && !showRegister) {
    return (
      <div style={{ backgroundColor: '#001f3f', height: '100vh', color: 'white', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center' }}>
        <h2>🔐 보안 관리자 로그인</h2>
        <form onSubmit={handleLogin} style={{ display: 'flex', flexDirection: 'column', width: '250px', gap: '10px' }}>
          <input type="text" placeholder="아이디" value={username} onChange={(e) => setUsername(e.target.value)} required />
          <input type="password" placeholder="비밀번호" value={password} onChange={(e) => setPassword(e.target.value)} required />
          <div style={{ display: 'flex', justifyContent: 'space-between' }}>
            <button type="submit">로그인</button>
            <button type="button" onClick={() => setShowRegister(true)}>관리자 등록</button>
          </div>
        </form>
        {error && <p style={{ color: 'tomato', marginTop: '10px' }}>{error}</p>}
      </div>
    );
  }

  if (showRegister) {
    return (
      <div style={{ backgroundColor: '#001f3f', height: '100vh', color: 'white', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center' }}>
        <h2>👮 관리자 등록</h2>
        <form onSubmit={handleRegister} style={{ display: 'flex', flexDirection: 'column', width: '250px', gap: '10px' }}>
          <input name="name" placeholder="이름" required />
          <input name="newUsername" placeholder="아이디" required />
          <input name="newPassword" type="password" placeholder="비밀번호" required />
          <input name="email" type="email" placeholder="이메일" required />
          <button type="submit">등록</button>
          <button type="button" onClick={() => setShowRegister(false)}>뒤로가기</button>
        </form>
      </div>
    );
  }

  return (
    <div style={{ backgroundColor: '#001f3f', minHeight: '100vh', color: 'white', padding: '20px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h1>🔐 관리자 UI</h1>
        <button onClick={handleLogout} style={{ padding: '4px 10px', height: '32px' }}>로그아웃</button>
      </div>

      <div style={{ marginBottom: '10px' }}>
        {['users', 'logs', 'approve', 'profile'].map(tab => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            style={{
              marginRight: '6px',
              padding: '6px 10px',
              backgroundColor: activeTab === tab ? '#0074D9' : '#555',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              fontSize: '13px',
              cursor: 'pointer'
            }}
          >
            {tab === 'users' ? '👥 사용자 관리'
              : tab === 'logs' ? '📜 공격 로그'
              : tab === 'approve' ? '📋 관리자 승인'
              : '⚙️ 내 정보 수정'}
          </button>
        ))}
      </div>

      {activeTab === 'profile' && (
        <>
          <h2>⚙️ 내 정보 수정</h2>
          <form onSubmit={handleProfileUpdate} style={{ maxWidth: '400px', display: 'flex', flexDirection: 'column', gap: '10px' }}>
            <input
              type="password"
              placeholder="현재 비밀번호"
              value={currentPassword}
              onChange={(e) => setCurrentPassword(e.target.value)}
              required
            />
            <input
              type="password"
              placeholder="새 비밀번호"
              value={newPassword}
              onChange={(e) => setNewPassword(e.target.value)}
            />
            <input
              type="email"
              placeholder="새 이메일"
              value={newEmail}
              onChange={(e) => setNewEmail(e.target.value)}
            />
            <button type="submit" style={{ padding: '6px 10px', backgroundColor: '#0074D9', color: 'white', border: 'none', borderRadius: '4px' }}>정보 수정</button>
          </form>
        </>
      )}

      {activeTab === 'users' && (
        <>
          <h2>사용자 목록</h2>
          <ul>
            {users.map((u, i) => (
              <li key={i}>{u.username} - {u.ip}</li>
            ))}
          </ul>
        </>
      )}

      {activeTab === 'logs' && (
        <>
          <h2>공격 로그</h2>
          <input type="text" placeholder="검색어" value={searchTerm} onChange={(e) => setSearchTerm(e.target.value)} />
          <pre style={{ backgroundColor: '#111', padding: '10px', color: '#0f0', borderRadius: '4px' }}>
            {filteredLogs.length > 0 ? filteredLogs.join('\n') : '일치하는 로그가 없습니다.'}
          </pre>
          <button
            style={{ padding: '8px 14px', fontSize: '13px', marginTop: '10px' }}
            onClick={() => {
              const blob = new Blob([filteredLogs.join('\n')], { type: 'text/plain;charset=utf-8' });
              const url = URL.createObjectURL(blob);
              const a = document.createElement('a');
              a.href = url;
              a.download = 'logs.txt';
              a.click();
              URL.revokeObjectURL(url);
            }}
          >
            검색 로그 다운로드
          </button>
        </>
      )}

      {activeTab === 'approve' && (
        <>
          <h2>📋 관리자 승인/관리</h2>
          {admins.length === 0 && <p>등록된 관리자가 없습니다.</p>}
          {admins.map(admin => (
            <div key={admin.id} style={{ marginBottom: '12px', backgroundColor: '#003366', padding: '10px', borderRadius: '6px' }}>
              <p>아이디: <strong>{admin.username}</strong></p>
              <p>이메일: {admin.email}</p>
              <p>이름: {admin.name}</p>
              <label>
                승인 여부:
                <input
                  type="checkbox"
                  checked={admin.isApproved}
                  onChange={(e) => updateAdminApproval(admin.id, e.target.checked)}
                  style={{ marginLeft: '10px' }}
                /> {admin.isApproved ? '승인됨' : '미승인'}
              </label>
              {admin.username !== username && (
                <button onClick={() => deleteAdmin(admin.id)} style={{ marginLeft: '10px', backgroundColor: 'red', color: 'white' }}>삭제</button>
              )}
            </div>
          ))}
        </>
      )}
    </div>
  );
}

export default App;