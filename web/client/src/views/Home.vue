<template>
  <div class="dashboard-container">
    <!-- 1. 좌측: 자룡모빌리티솔루션 사내 대시보드 (금호HT 기업 정보 스타일) -->
    <div class="dashboard-main">
      <header class="company-header">
        <div class="header-title">
          <h1>자룡모빌리티솔루션 대시보드</h1>
          <span class="subtitle">Jaryong Mobility Solutions Intranet</span>
        </div>
        <span class="status-badge">세계로 뻗어나가는 차세대 임베디드 모빌리티 SW & HW</span>
      </header>

      <!-- 1. 기업 개요 -->
      <section class="card-section">
        <h3 class="card-title">📌 1. 기업 개요 (Company Profile)</h3>
        <div class="profile-grid">
          <div class="profile-item"><span>설립일</span> <strong>1968년 03월 15일</strong></div>
          <div class="profile-item"><span>창립자</span> <strong>이자룡</strong></div>
          <div class="profile-item"><span>현임 회장</span> <strong>이승원</strong></div>
        </div>
        <div class="business-box">
          <strong>주요 사업 영역</strong>
          <ul>
            <li>차량용 BMS(Battery Management System) ECU H/W 설계 및 S/W 개발</li>
            <li>AUTOSAR Classic / Adaptive 기반 BSW 모듈 이식 및 검증</li>
            <li>CAN / CAN-FD / LIN 통신 분석 및 모니터링 툴체인 구축</li>
            <li><span class="tag-new">NEW</span> 임베디드 엔지니어 지원용 AI 코파일럿(Copilot) 시스템 구축</li>
          </ul>
        </div>
      </section>

      <!-- 2. 주요 부서 현황 -->
      <section class="card-section">
        <h3 class="card-title">⚙️ 2. 주요 부서 및 업무 현황 (Department Status)</h3>
        <table class="dashboard-table">
          <thead>
            <tr>
              <th>부서명</th>
              <th>주요 담당 업무</th>
              <th>대표 MCU / 프로토콜</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td><strong>제어SW1팀</strong></td>
              <td>BMS 셀 밸런싱 알고리즘 개발 및 SoC/SoH 추정 로직 구현</td>
              <td><span class="tech-chip">TriCore TC397</span> <span class="tech-chip">CAN-FD</span></td>
            </tr>
            <tr>
              <td><strong>제어SW2팀</strong></td>
              <td>모터 제어(MCU) 인버터 FOC 알고리즘 및 PWM 드라이버 구축</td>
              <td><span class="tech-chip">S32K144</span> <span class="tech-chip">SPI / PWM</span></td>
            </tr>
            <tr>
              <td><strong>BSW팀</strong></td>
              <td>AUTOSAR MCAL, PduR, CanIf, Dem/Dtm 모듈 모듈화 및 컴파일</td>
              <td><span class="tech-chip">NXP S32K</span> <span class="tech-chip">MCAL</span></td>
            </tr>
            <tr>
              <td><strong>HW검증팀</strong></td>
              <td>배터리 팩 열관리, 셀 전압/전류 로깅 및 HILs 테스트 데이터 분석</td>
              <td><span class="tech-chip">pyserial</span> <span class="tech-chip">CANoe</span></td>
            </tr>
          </tbody>
        </table>
      </section>

      <!-- 3. 분기별 매출 실적 -->
      <section class="card-section">
        <h3 class="card-title">📈 3. 2020 - 2026년 분기별 매출 및 실적</h3>
        <div class="sales-cards">
          <div class="sales-card">
            <span class="period">2020 - 2022년</span>
            <p class="desc">레거시 8/16비트 MCU 기반 BMS 모듈 납품</p>
            <span class="amount">평균 분기 45억 원</span>
          </div>
          <div class="sales-card">
            <span class="period">2023 - 2024년</span>
            <p class="desc">AUTOSAR R20-11 준수 BSW 및 CAN-FD 고속 통신 양산</p>
            <span class="amount">평균 분기 120억 원</span>
          </div>
          <div class="sales-card highlight">
            <span class="period">2025 - 2026년</span>
            <p class="desc">차세대 TriCore 기반 가상화 BMS ECU 해외 OEM 수출</p>
            <span class="amount">평균 분기 210억 원</span>
          </div>
        </div>
      </section>
    </div>


  </div>
</template>

<script setup>
import { ref, nextTick } from 'vue';
import axios from 'axios';

const userInput = ref('');
const messages = ref([
  { role: 'ai', text: '안녕하세요, master! 자룡모빌리티솔루션 AI Copilot입니다. 무엇을 도와드릴까요?' }
]);
const chatBox = ref(null);

const sendMessage = async () => {
  if (!userInput.value.trim()) return;

  const text = userInput.value;
  messages.value.push({ role: 'user', text: text });
  userInput.value = '';

  await scrollToBottom();

  try {
    // 백엔드(8000번) 호출
    const res = await axios.post('http://localhost:8000/api/chat', { 
      message: text 
    });
    messages.value.push({ role: 'ai', text: res.data.reply });
  } catch (error) {
    messages.value.push({ role: 'ai', text: '응답을 받아오지 못했습니다.' });
  }

  await scrollToBottom();
};

const scrollToBottom = async () => {
  await nextTick();
  if (chatBox.value) {
    chatBox.value.scrollTop = chatBox.value.scrollHeight;
  }
};
</script>

<style scoped>
.dashboard-container {
  display: flex;
  gap: 20px;
  height: 100%;
}

/* 좌측 메인 대시보드 */
.dashboard-main {
  flex: 1.3;
  display: flex;
  flex-direction: column;
  gap: 16px;
  overflow-y: auto;
  padding-right: 6px;
}

.company-header {
  background: white;
  padding: 20px;
  border-radius: 12px;
  border: 1px solid #e2e8f0;
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.company-header h1 { margin: 0; font-size: 22px; color: #0f172a; }
.subtitle { font-size: 13px; color: #64748b; font-weight: 600; display: block; margin-top: 4px; }
.status-badge {
  background: #eff6ff; color: #2563eb; padding: 6px 12px; border-radius: 20px; font-size: 12px; font-weight: bold; border: 1px solid #bfdbfe;
}

.card-section {
  background: white;
  padding: 20px;
  border-radius: 12px;
  border: 1px solid #e2e8f0;
}
.card-title { margin: 0 0 14px 0; font-size: 15px; color: #1e293b; border-bottom: 2px solid #f1f5f9; padding-bottom: 8px; }

.profile-grid {
  display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin-bottom: 14px;
}
.profile-item {
  background: #f8fafc; padding: 10px 14px; border-radius: 8px; border: 1px solid #f1f5f9; font-size: 13px;
}
.profile-item span { display: block; color: #64748b; font-size: 11px; margin-bottom: 2px; }

.business-box { font-size: 13px; color: #334155; }
.business-box ul { margin: 6px 0 0 0; padding-left: 20px; }
.business-box li { margin-bottom: 4px; }
.tag-new { background: #ef4444; color: white; font-size: 10px; padding: 2px 5px; border-radius: 4px; font-weight: bold; }

.dashboard-table { width: 100%; border-collapse: collapse; font-size: 13px; }
.dashboard-table th, .dashboard-table td { padding: 10px 12px; text-align: left; border-bottom: 1px solid #f1f5f9; }
.dashboard-table th { background: #f8fafc; color: #475569; font-weight: 600; }
.tech-chip { background: #e2e8f0; color: #334155; font-size: 11px; padding: 2px 6px; border-radius: 4px; font-weight: 500; }

.sales-cards { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; }
.sales-card {
  background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 12px; font-size: 12px;
}
.sales-card.highlight { background: #f0fdf4; border-color: #bbf7d0; }
.sales-card .period { font-weight: bold; color: #1e293b; }
.sales-card .desc { color: #64748b; margin: 6px 0; font-size: 11px; min-height: 32px; }
.sales-card .amount { font-size: 13px; font-weight: bold; color: #16a34a; display: block; }

/* 우측 AI 대시보드 패널 */
.dashboard-ai-panel {
  flex: 0.7;
  background: white;
  border-radius: 12px;
  border: 1px solid #e2e8f0;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  height: calc(100vh - 40px);
}
.ai-header {
  background: #0f172a; color: white; padding: 14px 16px; display: flex; justify-content: space-between; align-items: center;
}
.ai-header h3 { margin: 0; font-size: 15px; }
.online-indicator { background: #22c55e; color: white; font-size: 10px; padding: 2px 8px; border-radius: 10px; font-weight: bold; }

.chat-box { flex: 1; padding: 16px; overflow-y: auto; background: #f8fafc; }
.message { margin-bottom: 10px; padding: 10px 12px; border-radius: 8px; max-width: 85%; font-size: 13px; line-height: 1.4; white-space: pre-wrap; }
.message.user { background: #2563eb; color: white; margin-left: auto; }
.message.ai { background: white; color: #0f172a; border: 1px solid #e2e8f0; margin-right: auto; }

.input-area { display: flex; padding: 12px; border-top: 1px solid #e2e8f0; background: white; }
.input-area input { flex: 1; padding: 8px 12px; font-size: 13px; border: 1px solid #cbd5e1; border-radius: 6px; }
.input-area button { margin-left: 8px; padding: 0 16px; background: #2563eb; color: white; border: none; border-radius: 6px; cursor: pointer; font-weight: bold; }
</style>