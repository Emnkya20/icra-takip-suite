
import React, { useState } from 'react'
import axios from 'axios'

export default function BulkUpload(){
  const [report, setReport] = useState<any>(null)
  const onFile = async (e:any) => {
    const file = e.target.files[0]
    const fd = new FormData()
    fd.append('upload', file)
    const r = await axios.post('/api/files/import-csv', fd)
    setReport(r.data)
  }
  return (
    <div>
      <h2>Toplu Yükleme (CSV)</h2>
      <input type='file' accept='.csv' onChange={onFile} />
      {report && <pre>{JSON.stringify(report,null,2)}</pre>}
      <p>CSV başlık örneği: sequence_no,debtor_name,icra_dairesi,file_no,original_debt,status</p>
    </div>
  )
}
