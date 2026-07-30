<template>
  <div class="page-container">
    <div class="header-section">
      <h2>📊 ECU 노드 현황 (SQLite DB)</h2>
      <button class="refresh-btn" @click="fetchEcuNodes">🔄 새로고침</button>
    </div>

    <div v-if="loading" class="loading-state">데이터를 읽어오는 중입니다...</div>
    <div v-else-if="error" class="error-state">{{ error }}</div>

    <div v-else class="table-card">
      <table class="data-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>노드명 (Node Name)</th>
            <th>MCU 모델</th>
            <th>CAN Baudrate</th>
            <th>FW 버전</th>
            <th>상태 (Status)</th>
            <th>등록일시</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="node in ecuNodes" :key="node.node_id">
            <td>{{ node.node_id }}</td>
            <td><strong>{{ node.node_name }}</strong></td>
            <td><span class="mcu-chip">{{ node.mcu_model }}</span></td>
            <td>{{ (node.can_baudrate / 1000).toLocaleString() }} Kbps</td>
            <td>{{ node.fw_version }}</td>
            <td>
              <span :class="['status-badge', node.status.toLowerCase()]">
                {{ node.status }}
              </span>
            </td>
            <td>{{ node.created_at }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import axios from 'axios';

const ecuNodes = ref([]);
const loading = ref(true);
const error = ref(null);

const fetchEcuNodes = async () => {
  loading.value = true;
  error.value = null;
  try {
    const res = await axios.get('http://localhost:8000/api/ecu-nodes');
    ecuNodes.value = res.data;
  } catch (err) {
    error.value = 'DB 데이터를 가져오지 못했습니다. 백엔드 연결을 확인하세요.';
  } finally {
    loading.value = false;
  }
};

onMounted(fetchEcuNodes);
</script>

<style scoped>
.page-container {
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.header-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: white;
  padding: 16px 20px;
  border-radius: 12px;
  border: 1px solid #e2e8f0;
}
.header-section h2 { margin: 0; font-size: 20px; color: #0f172a; }
.refresh-btn {
  background: #2563eb; color: white; border: none; padding: 8px 14px; border-radius: 6px; cursor: pointer; font-weight: bold;
}

.table-card {
  background: white; border-radius: 12px; border: 1px solid #e2e8f0; overflow: hidden;
}
.data-table { width: 100%; border-collapse: collapse; font-size: 14px; }
.data-table th, .data-table td { padding: 12px 16px; text-align: left; border-bottom: 1px solid #f1f5f9; }
.data-table th { background: #f8fafc; color: #475569; font-weight: 600; }

.mcu-chip { background: #e2e8f0; padding: 2px 8px; border-radius: 4px; font-weight: bold; color: #334155; font-size: 12px; }
.status-badge { padding: 4px 8px; border-radius: 12px; font-size: 11px; font-weight: bold; }
.status-badge.active { background: #dcfce7; color: #15803d; }
.status-badge.testing { background: #fef9c3; color: #a16207; }
.status-badge.inactive { background: #fee2e2; color: #b91c1c; }

.loading-state, .error-state { background: white; padding: 40px; text-align: center; border-radius: 12px; border: 1px solid #e2e8f0; color: #64748b; }
</style>