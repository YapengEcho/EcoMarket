<template>
  <div class="my-orders">
    <div class="page-header">
      <p class="page-eyebrow">我的交易</p>
      <h1 class="page-title">买卖<span class="title-accent">记录</span></h1>
    </div>

    <el-tabs v-model="tab" @tab-change="load" class="order-tabs">
      <el-tab-pane label="我买的" name="buy" />
      <el-tab-pane label="我卖的" name="sell" />
    </el-tabs>

    <div class="table-card" v-loading="loading">
      <el-table :data="orders" stripe>
        <el-table-column prop="request_id" label="ID" width="70" />
        <el-table-column label="商品" min-width="200">
          <template #default="{ row }">
            <div class="item-cell" @click="$router.push(`/item/${row.item_id}`)">
              <span class="item-title">{{ row.item_title || `商品#${row.item_id}` }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="金额" width="100">
          <template #default="{ row }">
            <span class="amount">¥{{ (row.item_price || 0).toFixed(2) }}</span>
          </template>
        </el-table-column>
        <el-table-column label="交易状态" width="100">
          <template #default="{ row }">
            <el-tag :type="statusType(row.status)" size="small">{{ statusText(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="交易码" width="120">
          <template #default="{ row }">
            <span v-if="tab === 'sell' && row.trade_code" class="trade-code">{{ row.trade_code }}</span>
            <span v-else-if="tab === 'buy' && row.status === 1" class="code-hint">需输码确认</span>
            <span v-else class="text-muted">—</span>
          </template>
        </el-table-column>
        <el-table-column prop="message" label="留言" min-width="150" show-overflow-tooltip />
        <el-table-column label="操作" width="340">
          <template #default="{ row }">
            <!-- 卖家：待处理 -->
            <template v-if="tab === 'sell' && row.status === 0">
              <el-button size="small" type="success" @click="update(row.request_id, 1)">接受</el-button>
              <el-button size="small" @click="update(row.request_id, 2)">拒绝</el-button>
            </template>
            <!-- 买家：卖家已接受，输码确认 -->
            <el-button v-if="tab === 'buy' && row.status === 1"
              size="small" type="primary" @click="openConfirm(row.request_id)">
              输码确认收货
            </el-button>
            <!-- 联系对方：基于商品协商交易时间地点（已拒绝除外） -->
            <el-button v-if="row.status !== 2 && row.peer_id"
              size="small" @click="openChat(row.item_id, row.peer_id, row.peer_name)">
              联系对方
            </el-button>
            <!-- 已完成：可评价（未评价过时显示） -->
            <el-button v-if="row.status === 3 && !row.has_reviewed"
              size="small" type="warning" @click="openReview(row.request_id, row.peer_name)">
              评价
            </el-button>
            <span v-if="row.status === 3 && row.has_reviewed" class="text-muted">已评价</span>
            <span v-if="row.status === 2" class="text-muted">已拒绝</span>
          </template>
        </el-table-column>
      </el-table>

      <div v-if="!loading && orders.length === 0" class="empty">
        <span class="empty-mark">◐</span>
        <p>暂无交易记录</p>
      </div>
    </div>

    <!-- 输码确认弹窗 -->
    <el-dialog v-model="showConfirm" title="输入交易码确认收货" width="360px">
      <div class="confirm-form">
        <p class="confirm-hint">请输入卖家提供的 6 位交易码，线下见面验货后确认</p>
        <el-input v-model="inputCode" placeholder="6 位数字交易码" maxlength="6" size="large" style="text-align:center;letter-spacing:4px" />
      </div>
      <template #footer>
        <el-button @click="showConfirm = false">取消</el-button>
        <el-button type="primary" @click="doConfirm">确认收货</el-button>
      </template>
    </el-dialog>

    <!-- 站内消息弹窗：基于商品协商交易时间地点 -->
    <el-dialog v-model="showChat" :title="`联系对方：${chatPeerName}`" width="480px" @open="loadChat">
      <div class="chat-box">
        <div ref="chatScroll" class="chat-messages">
          <div v-if="chatLoading" class="chat-empty">加载中…</div>
          <div v-else-if="chatList.length === 0" class="chat-empty">
            暂无消息，发送第一条消息开始协商交易时间地点
          </div>
          <template v-else>
            <div v-for="m in chatList" :key="m.msg_id" class="chat-msg" :class="{ mine: m.is_mine }">
              <div class="chat-bubble">
                <div class="chat-meta">{{ m.is_mine ? '我' : m.sender_name }} · {{ formatChatTime(m.created_at) }}</div>
                <div class="chat-content">{{ m.content }}</div>
              </div>
            </div>
          </template>
        </div>
        <div class="chat-input">
          <el-input
            v-model="chatText"
            type="textarea"
            :rows="2"
            placeholder="输入消息，协商交易时间地点…（Ctrl+Enter 发送）"
            maxlength="500"
            show-word-limit
            @keyup.enter.ctrl="sendChat"
          />
          <el-button type="primary" :disabled="!chatText.trim()" @click="sendChat">发送</el-button>
        </div>
      </div>
    </el-dialog>

    <!-- 评价弹窗：交易完成后双方互评，更新信誉分 -->
    <el-dialog v-model="showReview" :title="`评价 ${reviewPeerName}`" width="400px">
      <div class="review-form">
        <p class="review-hint">交易已完成，请对对方进行评价（评价将影响对方信誉分）</p>
        <div class="rate-row">
          <span class="rate-label">评分</span>
          <el-rate v-model="reviewRating" :max="5" show-text :texts="['很差','较差','一般','较好','很好']" />
        </div>
        <el-input
          v-model="reviewComment"
          type="textarea"
          :rows="3"
          placeholder="留下您的评价（选填，最多 500 字）"
          maxlength="500"
          show-word-limit
        />
      </div>
      <template #footer>
        <el-button @click="showReview = false">取消</el-button>
        <el-button type="primary" :disabled="reviewRating === 0" @click="submitReview">提交评价</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import { requestsApi } from '@/api/requests'
import { messagesApi } from '@/api/messages'
import { reviewsApi } from '@/api/reviews'

const tab = ref('buy')
const orders = ref<any[]>([])
const loading = ref(false)
const showConfirm = ref(false)
const inputCode = ref('')
const confirmId = ref(0)

// 站内消息（基于商品，协商交易时间地点）
const showChat = ref(false)
const chatItemId = ref(0)
const chatPeerId = ref(0)
const chatPeerName = ref('')
const chatList = ref<any[]>([])
const chatText = ref('')
const chatLoading = ref(false)
const chatScroll = ref<HTMLElement | null>(null)

// 评价
const showReview = ref(false)
const reviewRequestId = ref(0)
const reviewPeerName = ref('')
const reviewRating = ref(0)
const reviewComment = ref('')

function statusText(s: number) { return ['待处理', '已接受', '已拒绝', '已完成'][s] || '未知' }
function statusType(s: number) { return ['warning', 'primary', 'info', 'success'][s] || 'info' }

async function load() {
  loading.value = true
  try {
    const res = await requestsApi.my(tab.value === 'buy')
    orders.value = res.data.data
  } finally {
    loading.value = false
  }
}

async function update(id: number, status: number) {
  try {
    const res = await requestsApi.updateStatus(id, status)
    ElMessage.success(res.data.message || '状态已更新')
    load()
  } catch {}
}

function openConfirm(id: number) {
  confirmId.value = id
  inputCode.value = ''
  showConfirm.value = true
}

async function doConfirm() {
  if (inputCode.value.length !== 6) {
    ElMessage.warning('请输入 6 位交易码')
    return
  }
  try {
    const res = await requestsApi.confirm(confirmId.value, inputCode.value)
    ElMessage.success(res.data.message || '交易完成')
    showConfirm.value = false
    load()
  } catch {}
}

// 打开与对方的对话弹窗（基于商品）
function openChat(itemId: number, peerId: number, peerName: string) {
  chatItemId.value = itemId
  chatPeerId.value = peerId
  chatPeerName.value = peerName || '对方'
  chatText.value = ''
  chatList.value = []
  showChat.value = true
}

async function loadChat() {
  chatLoading.value = true
  try {
    const res = await messagesApi.conversation(chatItemId.value, chatPeerId.value)
    chatList.value = res.data.data
    await nextTick()
    scrollChatToBottom()
  } catch {
    ElMessage.error('加载对话失败')
  } finally {
    chatLoading.value = false
  }
}

async function sendChat() {
  const text = chatText.value.trim()
  if (!text) return
  try {
    await messagesApi.send(chatPeerId.value, text, chatItemId.value)
    chatText.value = ''
    await loadChat()
  } catch {
    ElMessage.error('发送失败')
  }
}

function scrollChatToBottom() {
  const el = chatScroll.value
  if (el) el.scrollTop = el.scrollHeight
}

function formatChatTime(t?: string) {
  if (!t) return ''
  return t.slice(5, 16).replace('T', ' ')
}

// 打开评价弹窗
function openReview(requestId: number, peerName: string) {
  reviewRequestId.value = requestId
  reviewPeerName.value = peerName || '对方'
  reviewRating.value = 0
  reviewComment.value = ''
  showReview.value = true
}

// 提交评价
async function submitReview() {
  if (reviewRating.value < 1) {
    ElMessage.warning('请选择评分')
    return
  }
  try {
    const res = await reviewsApi.create(
      reviewRequestId.value,
      reviewRating.value,
      reviewComment.value.trim() || undefined,
    )
    ElMessage.success(res.data.message || '评价成功')
    showReview.value = false
    load() // 刷新列表，已评价后按钮会变成「已评价」
  } catch {
    ElMessage.error('评价失败')
  }
}

onMounted(load)
</script>

<style scoped>
.my-orders {
  max-width: 1000px;
  margin: 0 auto;
}

.page-header {
  margin-bottom: 24px;
}

.page-eyebrow {
  font-family: var(--font-body);
  font-size: 12px;
  font-weight: 600;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: var(--accent);
  margin-bottom: 8px;
}

.page-title {
  font-family: var(--font-body);
  font-size: 36px;
  font-weight: 700;
  letter-spacing: -0.02em;
  color: var(--text-primary);
}

.title-accent {
  font-style: italic;
  font-weight: 300;
  color: var(--accent);
}

.order-tabs {
  margin-bottom: 16px;
}

.table-card {
  background: var(--bg-card);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-lg);
  padding: 8px;
  min-height: 300px;
}

.item-cell {
  cursor: pointer;
}
.item-cell:hover .item-title {
  color: var(--accent);
}
.item-title {
  font-size: 13px;
  color: var(--text-secondary);
  transition: color 0.2s;
}

.amount {
  font-weight: 600;
  color: var(--accent);
}

.trade-code {
  font-family: var(--font-mono, monospace);
  font-size: 16px;
  font-weight: 700;
  letter-spacing: 2px;
  color: var(--accent);
  background: #f0f7ff;
  padding: 2px 8px;
  border-radius: 4px;
}

.code-hint {
  font-size: 12px;
  color: var(--accent);
}

.text-muted {
  font-size: 12px;
  color: var(--text-muted);
}

.empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  padding: 60px;
  color: var(--text-muted);
}

.empty-mark {
  font-family: var(--font-body);
  font-size: 48px;
  color: var(--border-strong);
}

.confirm-form {
  padding: 8px 0;
}

.confirm-hint {
  font-size: 13px;
  color: var(--text-muted);
  margin: 0 0 16px;
}

/* ====== 站内消息对话弹窗 ====== */
.chat-box {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.chat-messages {
  height: 320px;
  overflow-y: auto;
  padding: 12px;
  background: var(--bg-elevated, #f7f7f8);
  border: 1px solid var(--border-subtle, #e5e7eb);
  border-radius: 8px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.chat-empty {
  margin: auto;
  font-size: 13px;
  color: var(--text-muted);
  text-align: center;
  line-height: 1.8;
}

.chat-msg {
  display: flex;
}
.chat-msg.mine {
  justify-content: flex-end;
}

.chat-bubble {
  max-width: 75%;
  padding: 8px 12px;
  border-radius: 10px;
  background: #fff;
  border: 1px solid var(--border-subtle, #e5e7eb);
}
.chat-msg.mine .chat-bubble {
  background: #2563eb;
  color: #fff;
  border-color: #2563eb;
}

.chat-meta {
  font-size: 11px;
  opacity: 0.7;
  margin-bottom: 4px;
}

.chat-content {
  font-size: 14px;
  line-height: 1.6;
  word-break: break-word;
  white-space: pre-wrap;
}

.chat-input {
  display: flex;
  gap: 8px;
  align-items: flex-end;
}
.chat-input .el-button {
  flex-shrink: 0;
}

/* ====== 评价弹窗 ====== */
.review-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding: 8px 0;
}

.review-hint {
  font-size: 13px;
  color: var(--text-muted);
  margin: 0;
  line-height: 1.6;
}

.rate-row {
  display: flex;
  align-items: center;
  gap: 16px;
}

.rate-label {
  font-size: 14px;
  color: var(--text-secondary);
  flex-shrink: 0;
}
</style>
