
import React, { useEffect, useState } from 'react'
import axios from 'axios'

export default function Dashboard(){
  const [data, setData] = useState<any>(null)
  useEffect(()=>{
    axios.get('/api/dashboard/summary').then(r=> setData(r.data))
  },[])
  return (
    <div>
      <h2>Genel Bakış</h2>
      {data ? (
        <ul>
          <li>Toplam Tahsilat: {data.total_collected} ₺</li>
          <li>Toplam Borç: {data.total_debt} ₺</li>
          <li>Açık Dosya: {data.open_count}</li>
          <li>Kapalı Dosya: {data.closed_count}</li>
        </ul>
      ) : 'Yükleniyor...'}
    </div>
  )
}
