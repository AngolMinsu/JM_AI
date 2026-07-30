<template>
  <div class="intranet-layout">
    <!-- 1. 좌측 사내 인트라넷 사이드바 (모든 페이지 공통 적용 가능) -->
    <aside class="sidebar">
      <div class="logo">
        <h2>🐉 자룡모빌리티</h2>
      </div>
      <nav class="menu">
        <ul>
          <li><router-link to="/">🏠 사내 대시보드</router-link></li>
          <li><a href="#">📊 ECU 노드 현황</a></li>
          <li><a href="#">🔋 BMS 셀 로그 분석</a></li>
        </ul>
      </nav>
    </aside>

    <!-- 2. 중앙 컨텐츠 영역 (Router를 통해 페이지가 바뀜) -->
    <main class="content">
      <router-view></router-view>
    </main>

    <!-- 3. 우측 퀵메뉴 (사내 AI 링크 포함) -->
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
  font-family: 'Pretendard', sans-serif;
}

.sidebar {
  width: 250px;
  background-color: #1e293b;
  color: white;
}
.sidebar .logo { padding: 20px; background-color: #0f172a; text-align: center; }
.sidebar .menu ul { list-style: none; padding: 0; margin: 0; }
.sidebar .menu li a {
  display: block; padding: 15px 20px; color: #cbd5e1; text-decoration: none; border-bottom: 1px solid #334155;
}
.sidebar .menu li a:hover { background-color: #334155; color: white; }

.content {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

/* 우측 퀵메뉴 (Floating) */
.quick-menu-container {
  position: fixed;
  right: 20px;
  top: 50%;
  transform: translateY(-50%);
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 15px rgba(0,0,0,0.1);
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
.quick-link:hover { background: #e2e8f0; }
.ai-link {
  background: #eff6ff;
  border-color: #bfdbfe;
  color: #1d4ed8;
}
.ai-link:hover { background: #dbeafe; }
</style>