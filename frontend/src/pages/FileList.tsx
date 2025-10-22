
import React, { useEffect, useState } from 'react'
import axios from 'axios'

export default function FileList(){
  const [items, setItems] = useState<any[]>([])
  const [selected, setSelected] = useState<Record<string,boolean>>({})

  useEffect(()=>{
    axios.get('/api/files').then(r=> setItems(r.data.items))
  },[])

  const toggle = (id:string)=> setSelected(s=> ({...s, [id]: !s[id]}))
  const bulkDelete = async ()=>{
    const ids = Object.keys(selected).filter(k=>selected[k])
    if(ids.length===0) return alert('Seçim yok')
    if(!confirm(`${ids.length} dosyayı silmek istiyor musunuz?`)) return
    await axios.post('/api/files/bulk-delete', { ids })
    location.reload()
  }

  return (
    <div>
      <div style={{display:'flex', justifyContent:'space-between', marginBottom:8}}>
        <h2>Dosya Listesi</h2>
        <button onClick={bulkDelete}>Seçili Sil</button>
      </div>
      <table width='100%' border={1} cellPadding={6}>
        <thead>
          <tr>
            <th></th><th>SIRA</th><th>BORÇLU</th><th>DOSYA NO</th><th>DOSYA BORCU</th><th>DURUM</th>
          </tr>
        </thead>
        <tbody>
          {items.map(f=>(
            <tr key={f.id}>
              <td><input type='checkbox' checked={!!selected[f.id]} onChange={()=>toggle(f.id)} /></td>
              <td>{f.sequence_no ?? '-'}</td>
              <td>{f.debtor_name}</td>
              <td>{f.file_no ?? '-'}</td>
              <td>{f.original_debt}</td>
              <td>{f.status}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
