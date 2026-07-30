<template>
  <div class="page-container">
    <div class="header-section">
      <h2>🔋 BMS 셀 로그 분석</h2>
      <button class="refresh-btn" @click="fetchBmsLogs">🔄 로그 동기화</button>
    </div>

    <div v-if="loading" class="loading-state">로그 데이터를 분석하는 중입니다...</div>
    <div v-else-if="error" class="error-state">{{ error }}</div>

    <div v-else class="table-card">
      <table class="data-table">
        <thead>
          <tr>
            <th>타임스탬프 (Timestamp)</th>
            <th>팩 ID (Pack ID)</th>
            <th>최소 전압 (V)</th>
            <th>최대 전압 (V)</th>
            <th>전압 편차 (mV)</th>
            <th>온도 (°C)</th>
            <th>진단 상태</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(log, idx) in bmsLogs" :key="idx">
            <td>{{ log.timestamp }}</td>
            <td><strong>{{ log.pack_id }}</strong></td>
            <td>{{ log.cell_volt_min }} V</td>
            <td>{{ log.cell_volt_max }} V</td>
            <td :class="{'danger-text': log.disparity_mv >= 100}">
              <strong>{{ log.disparity_mv }} mV</strong>
            </td>
            <td>{{ log.temp_celsius }} °C</td>
            <td>
              <span :class="['status-chip', log.status.toLowerCase()]">
                {{ log.status }}
              </span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import axios from 'axios';

const bmsLogs = ref([]);
const loading = ref(true);
const error = ref(null);

const fetchBmsLogs = async () => {
  loading.value = true;
  error.value = null;
  try {
    const res = await axios.get('http://localhost:8000/api/bms-logs');
    bmsLogs.value = res.data;
  } catch (err) {
    error.value = 'BMS 로그 데이터를 읽어오지 못했습니다.';
  } finally {
    loading.value = false;
  }
};

onMounted(fetchBmsLogs);
</script>

<style scoped>
.page-container { display: flex; flex-direction: column; gap: 16px; }
.header-section {
  display: flex; justify-content: space-between; align-items: center; background: white; padding: 16px 20px; border-radius: 12px; border: 1px solid #e2e8f0;
}
.header-section h2 { margin: 0; font-size: 20px; color: #0f172a; }
.refresh-btn { background: #10b981; color: white; border: none; padding: 8px 14px; border-radius: 6px; cursor: pointer; font-weight: bold; }

.table-card { background: white; border-radius: 12px; border: 1px solid #e2e8f0; overflow: hidden; }
.data-table { width: 100%; border-collapse: collapse; font-size: 14px; }
.data-table th, .data-table td { padding: 12px 16px; text-align: left; border-bottom: 1px solid #f1f5f9; }
.data-table th { background: #f8fafc; color: #475569; font-weight: 600; }

.danger-text { color: #dc2626; }
.status-chip { padding: 4px 8px; border-radius: 4px; font-size: 11px; font-weight: bold; }
.status-chip.normal { background: #dcfce7; color: #15803d; }
.status-chip.warning { background: #fef9c3; color: #a16207; }
.status-chip.critical { background: #fee2e2; color: #b91c1c; }

.loading-state, .error-state { background: white; padding: 40px; text-align: center; border-radius: 12px; border: 1px solid #e2e8f0; color: #64748b; }
</style>