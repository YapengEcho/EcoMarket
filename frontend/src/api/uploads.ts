import client from './client'

export const uploadsApi = {
  uploadImage: (file: File) => {
    const form = new FormData()
    form.append('file', file)
    return client.post('/uploads/image', form, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
  },
}
