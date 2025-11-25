import { format, formatDistanceToNow } from 'date-fns';

export const formatFileSize = (bytes) => {
  if (!bytes || bytes === 0) return '0 Bytes';
  
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  
  return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
};

export const formatDate = (dateString) => {
  if (!dateString) return 'N/A';
  try {
    const date = new Date(dateString);
    const localDate = new Date(date.getTime() - date.getTimezoneOffset() * 60000);
    return format(localDate, 'MMM dd, yyyy HH:mm');
  } catch (error) {
    return 'Invalid date';
  }
};

export const formatRelativeTime = (dateString) => {
  if (!dateString) return 'N/A';
  try {
    const date = new Date(dateString);
    return formatDistanceToNow(date, { addSuffix: true });
  } catch (error) {
    return 'Invalid date';
  }
};

export const getFileExtension = (filename) => {
  if (!filename) return '';
  const parts = filename.split('.');
  return parts.length > 1 ? parts[parts.length - 1].toLowerCase() : '';
};

export const getFileIcon = (filename) => {
  const ext = getFileExtension(filename);
  const iconMap = {
    pdf: '📄',
    doc: '📝',
    docx: '📝',
    txt: '📃',
    odt: '📝',
    rtf: '📝',
    
    xls: '📊',
    xlsx: '📊',
    csv: '📊',
    ods: '📊',
    
    ppt: '📽️',
    pptx: '📽️',
    odp: '📽️',
    
    jpg: '🖼️',
    jpeg: '🖼️',
    png: '🖼️',
    gif: '🖼️',
    bmp: '🖼️',
    svg: '🖼️',
    webp: '🖼️',
    
    mp4: '🎥',
    avi: '🎥',
    mkv: '🎥',
    mov: '🎥',
    wmv: '🎥',
    
    mp3: '🎵',
    wav: '🎵',
    flac: '🎵',
    aac: '🎵',
    ogg: '🎵',
    
    zip: '📦',
    rar: '📦',
    '7z': '📦',
    tar: '📦',
    gz: '📦',
    
    js: '💻',
    py: '💻',
    java: '💻',
    cpp: '💻',
    c: '💻',
    html: '💻',
    css: '💻',
    json: '💻',
    xml: '💻',
  };
  
  return iconMap[ext] || '📎';
};

export const truncateFilename = (filename, maxLength = 30) => {
  if (!filename || filename.length <= maxLength) return filename;
  
  const ext = getFileExtension(filename);
  const nameWithoutExt = filename.substring(0, filename.lastIndexOf('.'));
  
  if (nameWithoutExt.length <= maxLength - ext.length - 4) {
    return filename;
  }
  
  const truncatedName = nameWithoutExt.substring(0, maxLength - ext.length - 4);
  return `${truncatedName}...${ext ? '.' + ext : ''}`;
};

export const validateFileSize = (file, maxSizeMB = 100) => {
  const maxSizeBytes = maxSizeMB * 1024 * 1024;
  return file.size <= maxSizeBytes;
};

export const sortFiles = (files, sortBy) => {
  const sorted = [...files];
  
  switch (sortBy) {
    case 'name_asc':
      return sorted.sort((a, b) => a.filename.localeCompare(b.filename));
    case 'name_desc':
      return sorted.sort((a, b) => b.filename.localeCompare(a.filename));
    case 'date_asc':
      return sorted.sort((a, b) => new Date(a.uploaded_at) - new Date(b.uploaded_at));
    case 'date_desc':
      return sorted.sort((a, b) => new Date(b.uploaded_at) - new Date(a.uploaded_at));
    case 'size_asc':
      return sorted.sort((a, b) => (a.size || 0) - (b.size || 0));
    case 'size_desc':
      return sorted.sort((a, b) => (b.size || 0) - (a.size || 0));
    default:
      return sorted;
  }
};
