export function formatPrice(v: number | string): string {
  const n = Number(v)
  return isNaN(n) ? '0.00' : n.toFixed(2)
}

export function formatImage(imgs: string | string[] | undefined): string {
  if (!imgs) return ''
  const arr = typeof imgs === 'string' ? imgs.split(',') : imgs
  return arr[0] || ''
}

export function statusText(status: number): string {
  return ['在售', '已预订', '已售出', '已下架'][status] || '未知'
}

export function statusTagType(status: number): string {
  return ['success', 'warning', 'info', 'danger'][status] || 'info'
}
