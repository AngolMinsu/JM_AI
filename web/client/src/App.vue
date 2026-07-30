<template>
  <div class="intranet-layout">
    <!-- 1. 좌측 사내 인트라넷 사이드바 -->
    <aside class="sidebar">
      <div class="logo">
        <h2>🐉 자룡모빌리티</h2>
      </div>
      <nav class="menu">
        <ul>
          <li><router-link to="/">🏠 사내 대시보드</router-link></li>
          <li>
            <router-link to="/ai-chat" class="ai-menu-item"
              >🤖 Jaryong AI Copilot</router-link
            >
          </li>
          <li><router-link to="/ecu-status">📊 ECU 노드 현황</router-link></li>
          <li><router-link to="/bms-logs">🔋 BMS 셀 로그 분석</router-link></li>
        </ul>
      </nav>
    </aside>

    <!-- 2. 중앙 컨텐츠 영역 (Router 라우팅 페이지 출력) -->
    <main class="content">
      <router-view></router-view>
    </main>

    <!-- 3. 우측 퀵메뉴 (Floating) -->
    <div class="quick-menu-container">
      <div class="quick-menu-list">
        <!-- AI 페이지로 이동하는 링크 -->
        <router-link to="/ai-chat" class="quick-link ai-link">
          ✨ Jaryong AI
        </router-link>
        <button class="quick-link">📅 사내 캘린더</button>
        <button class="quick-link">📁 자료실</button>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* 기본 인트라넷 레이아웃 */
.intranet-layout {
  display: flex;
  height: 100vh;
  background-color: #f4f6f9;
  font-family: "Pretendard", sans-serif;
}

.sidebar {
  width: 250px;
  background-color: #1e293b;
  color: white;
  flex-shrink: 0;
}
.sidebar .logo {
  padding: 20px;
  background-color: #0f172a;
  text-align: center;
}
.sidebar .menu ul {
  list-style: none;
  padding: 0;
  margin: 0;
}
.sidebar .menu li a {
  display: block;
  padding: 15px 20px;
  color: #cbd5e1;
  text-decoration: none;
  border-bottom: 1px solid #334155;
}
.sidebar .menu li a:hover,
.sidebar .menu li a.router-link-active {
  background-color: #334155;
  color: #60a5fa;
  font-weight: bold;
}

/* AI 전용 사이드바 메뉴 강조 */
.ai-menu-item {
  color: #93c5fd !important;
}

.content {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow-y: auto;
  padding: 20px;
}

/* 우측 퀵메뉴 (Floating) */
.quick-menu-container {
  position: fixed;
  right: 20px;
  top: 50%;
  transform: translateY(-50%);
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
  padding: 10px;
  z-index: 1000;
}
.quick-menu-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.quick-link {
  display: block;
  padding: 15px;
  text-align: center;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  cursor: pointer;
  text-decoration: none;
  color: #334155;
  font-weight: bold;
  transition: all 0.2s;
}
.quick-link:hover {
  background: #e2e8f0;
}
.ai-link {
  background: #eff6ff;
  border-color: #bfdbfe;
  color: #1d4ed8;
}
.ai-link:hover {
  background: #dbeafe;
}
</style>
