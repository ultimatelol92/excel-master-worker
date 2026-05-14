import React from 'react'
import { FileSpreadsheet, X } from 'lucide-react'

export default function FileUploadIndicator({ fileName, onRemove }) {
  return (
    <div className="upload-indicator">
      <FileSpreadsheet size={18} color="#217346" />
      <span>Attached: <strong>{fileName}</strong></span>
      <button className="remove-btn" onClick={onRemove} title="Remove file">
        <X size={16} />
      </button>
    </div>
  )
}
