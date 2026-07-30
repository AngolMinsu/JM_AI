<template>
  <div class="gemini-ui-container">
    <!-- 좌측 대화 기록 히스토리 (Gemini의 사이드바 역할) -->
    <div class="chat-sidebar">
      <button class="new-chat-btn">⊕ 새로운 대화</button>
      <div class="history-list">
        <p class="history-title">최근 대화</p>
        <ul>
          <li>TC397 보드레이트 설정법</li>
          <li>제어SW1팀 3분기 실적 분석</li>
          <li>배터리 셀 전압 로그 요약</li>
        </ul>
      </div>
    </div>

    <!-- 우측 메인 대화 영역 -->
    <div class="chat-main">
      <div class="chat-messages">
        <!-- AI 환영 메시지 -->
        <div class="message ai-message">
          <div class="avatar">🤖</div>
          <div class="content">
            안녕하세요. 자룡모빌리티 코파일럿입니다. <br>
            사내 DB 조회, ECU 노드 제어, 문서 요약 등 필요한 작업을 말씀해 주세요.
          </div>
        </div>
      </div>

      <!-- 하단 입력창 (프롬프트 입력) -->
      <div class="input-area-wrapper">
        <div class="input-box">
          <input type="text" placeholder="여기에 프롬프트를 입력하세요..." />
          <button class="send-btn">➤</button>
        </div>
        <p class="disclaimer">AI는 부정확한 정보를 제공할 수 있으므로, HILs 테스트 전 반드시 교차 검증하시기 바랍니다.</p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.gemini-ui-container {
  display: flex;
  height: 100%; /* 부모(content)의 높이를 꽉 채움 */
  background-color: white;
}

/* 대화 기록 사이드바 */
.chat-sidebar {
  width: 260px;
  background-color: #f9fafb;
  border-right: 1px solid #e5e7eb;
  padding: 20px;
  display: flex;
  flex-direction: column;
}
.new-chat-btn {
  background-color: white;
  border: 1px solid #d1d5db;
  padding: 12px;
  border-radius: 8px;
  font-weight: bold;
  cursor: pointer;
  margin-bottom: 20px;
}
.new-chat-btn:hover { background-color: #f3f4f6; }
.history-title { font-size: 12px; color: #6b7280; font-weight: bold; margin-bottom: 10px; }
.history-list ul { list-style: none; padding: 0; margin: 0; }
.history-list li {
  padding: 10px;
  font-size: 14px;
  color: #374151;
  cursor: pointer;
  border-radius: 6px;
}
.history-list li:hover { background-color: #e5e7eb; }

/* 메인 대화창 */
.chat-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  position: relative;
}
.chat-messages {
  flex: 1;
  padding: 40px;
  overflow-y: auto;
}
.message { display: flex; gap: 15px; margin-bottom: 30px; max-width: 800px; margin-left: auto; margin-right: auto; }
.message .avatar { font-size: 24px; }
.message .content { padding-top: 5px; line-height: 1.6; color: #111827; }

/* 입력창 */
.input-area-wrapper {
  padding: 20px 40px;
  background: white;
  display: flex;
  flex-direction: column;
  align-items: center;
}
.input-box {
  display: flex;
  width: 100%;
  max-width: 800px;
  background: #f3f4f6;
  border-radius: 24px;
  padding: 10px 20px;
  box-shadow: 0 2px 6px rgba(0,0,0,0.05);
}
.input-box input {
  flex: 1; border: none; background: transparent; outline: none; font-size: 16px; padding: 10px;
}
.send-btn { background: none; border: none; font-size: 20px; cursor: pointer; color: #3b82f6; }
.disclaimer { font-size: 12px; color: #9ca3af; margin-top: 10px; }
</style>