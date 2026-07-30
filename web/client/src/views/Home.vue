<template>
  <div class="home-dashboard">
    <header class="topbar">
      <h1>제어SW1팀 워크스페이스</h1>
      <div class="user-profile">KANG JU-HO (연구원)</div>
    </header>
    
    <section class="dashboard-content">
      <p>환영합니다. 우측 퀵메뉴에서 <strong>'✨ Jaryong AI'</strong>를 클릭하여 코파일럿을 실행해보세요.</p>
      
      <div class="placeholder-card">
        <h3>📊 최근 프로젝트 실적 요약</h3>
        <p>데이터 로딩 중... (추후 FastAPI 연동 시 차트가 들어갈 자리입니다)</p>
      </div>
    </section>
  </div>
</template>

<style scoped>
.home-dashboard {
  flex: 1;
  display: flex;
  flex-direction: column;
}
.topbar {
  background-color: white;
  padding: 15px 30px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid #e2e8f0;
}
.user-profile {
  font-weight: bold;
  color: #1e293b;
}
.dashboard-content {
  padding: 30px;
}
.placeholder-card {
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
  margin-top: 20px;
}
</style>