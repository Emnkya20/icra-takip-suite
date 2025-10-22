
import React, { useEffect, useState } from 'react'
import axios from 'axios'
import Dashboard from './pages/Dashboard'
import FileList from './pages/FileList'
import BulkUpload from './pages/BulkUpload'

export default function App(){
  const [token, setToken] = useState<string | null>(null)
  const [view, setView] = useState<'dashboard'|'list'|'bulk'>('dashboard')
  const [email, setEmail] = useState('admin@akropol.com')
  const [password, setPassword] = useState('ChangeMe!123')

  useEffect(()=>{
    if(token){
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`
    }
  },[token])

  const login = async () => {
    const form = new FormData()
    form.append('username', email)
    form.append('password', password)
    const r = await axios.post('/api/auth/token', form)
    setToken(r.data.access_token)
  }

  if(!token){
    return (
      <div style={{padding:20}}>
        <h2>Giriş</h2>
        <input placeholder='Email' value={email} onChange={e=>setEmail(e.target.value)} /><br/>
        <input placeholder='Şifre' type='password' value={password} onChange={e=>setPassword(e.target.value)} /><br/>
        <button onClick={login}>Giriş Yap</button>
        <p>İpucu: .env ile ADMIN_EMAIL/ADMIN_PASSWORD değiştirilebilir.</p>
      </div>
    )
  }

  return (
    <div style={{padding:20}}>
      <h1>İcra Yönetim Sistemi</h1>
      <div style={{display:'flex', gap:8, margin:'12px 0'}}>
        <button onClick={()=>setView('dashboard')}>Dashboard</button>
        <button onClick={()=>setView('list')}>Dosyalar</button>
        <button onClick={()=>setView('bulk')}>Toplu Yükleme</button>
      </div>
      {view==='dashboard' && <Dashboard />}
      {view==='list' && <FileList />}
      {view==='bulk' && <BulkUpload />}
    </div>
  )
}
