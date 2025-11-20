import api from './index'

export const login = (data) => {
  return api.post('/auth/login', data)
}

export const logout = (token) => {
  return api.post('/auth/logout', null, {
    params: { token }
  })
}

export const checkAuth = (token) => {
  return api.get('/auth/check-auth', {
    params: { token }
  })
}

