<template>
  <div class="admin-page">
    <div class="page-toolbar">
      <el-button type="primary" @click="openCreate">+ 新建分类</el-button>
    </div>

    <el-table :data="list" v-loading="loading" stripe border>
      <el-table-column prop="category_id" label="ID" width="70" align="center" />
      <el-table-column prop="name" label="分类名称" min-width="200" />
      <el-table-column prop="parent_id" label="父分类ID" width="120" align="center" />
      <el-table-column prop="sort_order" label="排序" width="80" align="center" />
      <el-table-column label="操作" width="180" fixed="right">
        <template #default="{ row }">
          <el-button size="small" @click="openEdit(row)">编辑</el-button>
          <el-button size="small" type="danger" @click="del(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="dialogVisible" :title="editing ? '编辑分类' : '新建分类'" width="400px">
      <el-form label-width="80px">
        <el-form-item label="名称">
          <el-input v-model="form.name" placeholder="分类名称" />
        </el-form-item>
        <el-form-item label="父分类">
          <el-input-number v-model="form.parent_id" :min="0" controls-position="right" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="save">确认</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { adminApi } from '@/api/admin'

const list = ref<any[]>([])
const loading = ref(false)
const dialogVisible = ref(false)
const editing = ref<any>(null)
const form = reactive({ name: '', parent_id: 0 })

async function load() {
  loading.value = true
  try {
    const res = await adminApi.listCategories()
    list.value = res.data.data
  } finally {
    loading.value = false
  }
}

function openCreate() {
  editing.value = null
  form.name = ''
  form.parent_id = 0
  dialogVisible.value = true
}

function openEdit(row: any) {
  editing.value = row
  form.name = row.name
  form.parent_id = row.parent_id || 0
  dialogVisible.value = true
}

async function save() {
  if (!form.name.trim()) {
    ElMessage.warning('请输入分类名称')
    return
  }
  if (editing.value) {
    await adminApi.updateCategory(editing.value.category_id, form.name)
  } else {
    await adminApi.createCategory(form.name, form.parent_id)
  }
  ElMessage.success('保存成功')
  dialogVisible.value = false
  load()
}

async function del(row: any) {
  await ElMessageBox.confirm(`确定要删除分类「${row.name}」吗？`, '删除', { type: 'warning' })
  await adminApi.deleteCategory(row.category_id)
  ElMessage.success('已删除')
  load()
}

onMounted(load)
</script>

<style scoped>
.admin-page { background: #fff; padding: 20px; border-radius: 8px; }
.page-toolbar { margin-bottom: 16px; }
</style>
