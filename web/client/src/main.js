import { createApp } from 'vue'
import App from './App.vue'
import router from './router'

const app = createApp(App)

// 라우터를 Vue 앱에 장착
app.use(router)

// id가 'app'인 HTML 요소에 화면을 렌더링
app.mount('#app')