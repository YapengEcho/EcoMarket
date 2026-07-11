<template>
  <div class="publish">
    <div class="page-header">
      <p class="page-eyebrow">发布商品</p>
      <h1 class="page-title">让闲置<span class="title-accent">找到</span>新主人</h1>
      <p class="page-sub">填写商品信息，AI 可帮你生成定价与描述。</p>
    </div>

    <div class="form-card">
      <div class="field-group">
        <label class="field-label">商品名称</label>
        <div class="title-row">
          <el-input v-model="form.title" placeholder="例：高等数学第七版 同济大学" size="large" />
          <button class="btn-ai" :disabled="aiLoading" @click="aiGenerate">
            <span v-if="aiLoading" class="ai-pulse"></span>
            {{ aiLoading ? "AI 生成中…" : "✦ AI 帮我填" }}
          </button>
        </div>
      </div>

      <div class="field-row">
        <div class="field-group">
          <label class="field-label">售价 ¥</label>
          <el-input v-model="form.price" placeholder="AI 自动生成或手动输入" size="large" />
        </div>
        <div class="field-group">
          <label class="field-label">原价 ¥</label>
          <el-input v-model="form.original_price" placeholder="选填" size="large" />
        </div>
      </div>

      <div class="field-row">
        <div class="field-group">
          <label class="field-label">分类</label>
          <el-select v-model="form.category_id" placeholder="选择分类" clearable size="large" style="width:100%">
            <el-option v-for="c in categories" :key="c.category_id" :label="c.name" :value="c.category_id" />
          </el-select>
        </div>
        <div class="field-group">
          <label class="field-label">成色</label>
          <div class="condition-toggle">
            <button
              type="button"
              class="cond-btn"
              :class="{ active: form.condition === 0 }"
              @click="form.condition = 0"
            >
              全新
            </button>
            <button
              type="button"
              class="cond-btn"
              :class="{ active: form.condition === 1 }"
              @click="form.condition = 1"
            >
              闲置
            </button>
          </div>
        </div>
      </div>

      <div class="field-group">
        <label class="field-label">商品描述</label>
        <el-input
          v-model="form.description"
          type="textarea"
          :rows="5"
          placeholder="AI 自动生成或手动输入商品描述…"
        />
      </div>

      <div class="field-group">
        <label class="field-label">上传图片</label>
        <el-upload
          :http-request="onUpload"
          :show-file-list="true"
          list-type="picture-card"
          accept="image/*"
        >
          <el-icon><Plus /></el-icon>
        </el-upload>
      </div>

      <div class="form-actions">
        <button class="btn-submit" :disabled="submitting" @click="submit">
          {{ submitting ? "发布中…" : "发布商品" }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Plus } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { itemsApi } from '@/api/items'
import { aiApi } from '@/api/ai'
import { uploadsApi } from '@/api/uploads'
import client from '@/api/client'

const router = useRouter()
const aiLoading = ref(false)
const submitting = ref(false)
const categories = ref<any[]>([])
const imageUrls = ref<string[]>([])

const form = reactive({
  title: '', price: '', original_price: '', category_id: null as number | null,
  condition: 0, description: '', images: '',
})

async function aiGenerate() {
  if (!form.title) { ElMessage.warning('请先输入商品名称'); return }
  aiLoading.value = true
  try {
    const res = await aiApi.generate(form.title)
    const d = res.data.data
    if (d.price) form.price = String(d.price)
    if (d.description) form.description = d.description
    ElMessage.success('AI 生成成功，请确认信息')
  } catch {} finally {
    aiLoading.value = false
  }
}

async function onUpload(opt: any) {
  try {
    const res = await uploadsApi.uploadImage(opt.file)
    const url = res.data.data.url
    imageUrls.value.push(url)
    ElMessage.success('上传成功')
  } catch {}
}

async function loadCategories() {
  const res = await client.get('/categories/')
  categories.value = res.data.data
}

async function submit() {
  if (!form.title || !form.price) { ElMessage.warning('请填写商品名称和价格'); return }
  submitting.value = true
  try {
    await itemsApi.create({
      title: form.title,
      price: Number(form.price),
      original_price: form.original_price ? Number(form.original_price) : undefined,
      category_id: form.category_id || undefined,
      condition: form.condition,
      description: form.description,
      images: imageUrls.value.join(','),
    })
    ElMessage.success('发布成功')
    router.push('/my-items')
  } finally {
    submitting.value = false
  }
}

onMounted(loadCategories)
</script>

<style scoped>
.publish {
  max-width: 760px;
  margin: 0 auto;
}

.page-header {
  margin-bottom: 40px;
}

.page-eyebrow {
  font-family: var(--font-body);
  font-size: 12px;
  font-weight: 600;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: var(--accent);
  margin-bottom: 12px;
}

.page-title {
  font-family: var(--font-body);
  font-size: 40px;
  font-weight: 700;
  line-height: 1.1;
  letter-spacing: -0.02em;
  color: var(--text-primary);
  margin-bottom: 12px;
}

.title-accent {
  font-style: italic;
  font-weight: 300;
  color: var(--accent);
}

.page-sub {
  font-size: 15px;
  color: var(--text-secondary);
}

.form-card {
  background: var(--bg-card);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-lg);
  padding: 32px;
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.field-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
  flex: 1;
}

.field-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

.field-label {
  font-family: var(--font-body);
  font-size: 13px;
  font-weight: 500;
  color: var(--text-secondary);
}

.title-row {
  display: flex;
  gap: 12px;
}
.title-row .el-input {
  flex: 1;
}

.btn-ai {
  font-family: var(--font-body);
  font-size: 14px;
  font-weight: 600;
  color: var(--color-success);
  background: var(--accent-soft);
  border: 1px solid var(--color-success);
  padding: 0 20px;
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: all 0.2s;
  white-space: nowrap;
  display: flex;
  align-items: center;
  gap: 8px;
}
.btn-ai:hover:not(:disabled) {
  background: var(--color-success);
  color: var(--bg-base);
}
.btn-ai:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.ai-pulse {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: currentColor;
  animation: pulse 1s infinite;
}

.condition-toggle {
  display: flex;
  gap: 0;
  border: 1px solid var(--border-strong);
  border-radius: var(--radius-sm);
  overflow: hidden;
  height: 40px;
}

.cond-btn {
  flex: 1;
  font-family: var(--font-body);
  font-size: 14px;
  font-weight: 500;
  color: var(--text-secondary);
  background: transparent;
  border: none;
  cursor: pointer;
  transition: all 0.2s;
}
.cond-btn.active {
  background: var(--accent);
  color: var(--bg-base);
}
.cond-btn:not(.active):hover {
  background: var(--bg-elevated);
  color: var(--text-primary);
}

.form-actions {
  margin-top: 8px;
}

.btn-submit {
  width: 100%;
  font-family: var(--font-body);
  font-size: 15px;
  font-weight: 600;
  color: var(--bg-base);
  background: var(--accent);
  border: none;
  padding: 16px;
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: all 0.2s;
}
.btn-submit:hover:not(:disabled) {
  background: #ff8d3a;
  transform: translateY(-1px);
  box-shadow: var(--shadow-card);
}
.btn-submit:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

@keyframes pulse {
  0%, 100% { opacity: 0.3; }
  50% { opacity: 1; }
}

@media (max-width: 768px) {
  .field-row {
    grid-template-columns: 1fr;
  }
  .page-title {
    font-size: 30px;
  }
  .form-card {
    padding: 20px;
  }
}
</style>
