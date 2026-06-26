const API_BASE = '';
const MAX_PDF_PAGES = 10;

const pdfFileInput = document.getElementById('pdf-file');
const imageFileInput = document.getElementById('image-file');
const runBtn = document.getElementById('run-btn');
const loading = document.getElementById('loading');
const warnings = document.getElementById('warnings');
const resultArea = document.getElementById('result-area');
const basicBody = document.getElementById('basic-body');
const itemsBody = document.getElementById('items-body');
const csvBtn = document.getElementById('csv-btn');
const excelBtn = document.getElementById('excel-btn');
const pdfDropZone = document.getElementById('pdf-drop-zone');
const imageDropZone = document.getElementById('image-drop-zone');
const pdfFileName = document.getElementById('pdf-file-name');
const imageFileName = document.getElementById('image-file-name');
const errorMessage = document.getElementById('error-message');
const processCard = document.getElementById('process-card');
const rateAuto = document.getElementById('rate-auto');
const rateManual = document.getElementById('rate-manual');
const rateManualInput = document.getElementById('rate-manual-input');
const exchangeRateInput = document.getElementById('exchange-rate');

let recordId = null;
let latestRows = [];
let isPdfPageCountValid = true;
let pdfValidationToken = 0;
let pdfPageErrorMessage = '';

pdfFileInput.addEventListener('change', () => handleFileChange(pdfFileInput, pdfFileName));
imageFileInput.addEventListener('change', () => handleFileChange(imageFileInput, imageFileName));
runBtn.addEventListener('click', runProcess);
csvBtn.addEventListener('click', () => downloadExport('csv'));
excelBtn.addEventListener('click', () => downloadExport('excel'));

setupDropZone(pdfDropZone, pdfFileInput, pdfFileName, 'pdf');
setupDropZone(imageDropZone, imageFileInput, imageFileName, 'image');

// 為替レートモード切り替え
[rateAuto, rateManual].forEach(radio => {
  radio.addEventListener('change', () => {
    rateManualInput.classList.toggle('hidden', rateAuto.checked);
  });
});

async function handleFileChange(input, fileNameElement) {
  fileNameElement.textContent = input.files[0]?.name || '選択されていません';

  if (input === pdfFileInput) {
    clearError();
    await validatePdfPageCount(input.files[0]);
  } else if (!pdfPageErrorMessage) {
    clearError();
  } else {
    displayError(pdfPageErrorMessage);
  }

  validateFileSelection();
}

function setupDropZone(dropZone, input, fileNameElement, fileType) {
  ['dragenter', 'dragover'].forEach((eventName) => {
    dropZone.addEventListener(eventName, (event) => {
      event.preventDefault();
      dropZone.classList.add('is-dragging');
    });
  });

  dropZone.addEventListener('dragleave', (event) => {
    if (!dropZone.contains(event.relatedTarget)) {
      dropZone.classList.remove('is-dragging');
    }
  });

  dropZone.addEventListener('drop', (event) => {
    event.preventDefault();
    dropZone.classList.remove('is-dragging');

    const file = event.dataTransfer.files[0];
    if (!file) {
      return;
    }

    if (!isAcceptedFile(file, fileType)) {
      const expected = fileType === 'pdf' ? 'PDF' : 'JPGまたはPNG画像';
      displayError(`${expected}を選択してください。`);
      return;
    }

    const transfer = new DataTransfer();
    transfer.items.add(file);
    input.files = transfer.files;
    handleFileChange(input, fileNameElement);
  });
}

function isAcceptedFile(file, fileType) {
  const fileName = file.name.toLowerCase();

  if (fileType === 'pdf') {
    return file.type === 'application/pdf' || fileName.endsWith('.pdf');
  }

  return ['image/jpeg', 'image/png'].includes(file.type)
    || /\.(jpe?g|png)$/.test(fileName);
}

function validateFileSelection() {
  const hasPdf = pdfFileInput.files.length > 0;
  const hasImage = imageFileInput.files.length > 0;

  runBtn.disabled = !(hasPdf && hasImage && isPdfPageCountValid);
}

async function validatePdfPageCount(file) {
  const token = ++pdfValidationToken;
  isPdfPageCountValid = false;
  validateFileSelection();

  if (!file) {
    isPdfPageCountValid = true;
    pdfPageErrorMessage = '';
    return;
  }

  try {
    const pageCount = await countPdfPages(file);

    if (token !== pdfValidationToken) {
      return;
    }

    if (pageCount > MAX_PDF_PAGES) {
      isPdfPageCountValid = false;
      pdfPageErrorMessage = `PDFは${MAX_PDF_PAGES}ページ以内にしてください。現在のPDFは${pageCount}ページです。`;
      displayError(pdfPageErrorMessage);
      return;
    }

    isPdfPageCountValid = true;
    pdfPageErrorMessage = '';
  } catch (error) {
    console.error(error);
    isPdfPageCountValid = false;
    pdfPageErrorMessage = 'PDFのページ数を確認できませんでした。別のPDFを選択してください。';
    displayError(pdfPageErrorMessage);
  }
}

async function countPdfPages(file) {
  const buffer = await file.arrayBuffer();
  const text = new TextDecoder('latin1').decode(buffer);
  const matches = text.match(/\/Type\s*\/Page\b/g);

  return matches ? matches.length : 0;
}

async function runProcess() {
  const pdfFile = pdfFileInput.files[0];
  const imageFile = imageFileInput.files[0];

  if (!pdfFile || !imageFile) {
    displayError('PDFファイルと画像ファイルの両方を選択してください。');
    return;
  }

  if (!isPdfPageCountValid) {
    displayError(`PDFは${MAX_PDF_PAGES}ページ以内にしてください。`);
    return;
  }

  resetResult();
  setLoading(true);

  const formData = new FormData();
  formData.append('pdf_file', pdfFile);
  formData.append('image_file', imageFile);

  // 手動入力モードの場合は為替レートを追加
  if (rateManual.checked) {
    const rate = exchangeRateInput.value;
    if (!rate) {
      displayError('為替レートを入力してください。');
      setLoading(false);
      validateFileSelection();
      return;
    }
    formData.append('exchange_rate', rate);
  }

  try {
    const data = await requestProcess(formData);

    if (data.status === 'error') {
      displayError(data.message);
      return;
    }

    recordId = data.record_id;

    showWarnings(data.warnings || []);
    renderResult(data.basic_info || [], data.items || []);

    csvBtn.disabled = !recordId;
    excelBtn.disabled = !recordId;
  } catch (error) {
    console.error(error);
    displayError(`処理に失敗しました。\n${error.message}`);
  } finally {
    setLoading(false);
    validateFileSelection();
  }
}

async function requestProcess(formData) {
  const res = await fetch(`${API_BASE}/api/process`, {
    method: 'POST',
    body: formData,
  });

  if (!res.ok) {
    const errorText = await res.text();
    throw new Error(`APIエラー: ${res.status} ${res.statusText}\n${errorText}`);
  }

  return res.json();
}

function setLoading(isLoading) {
  loading.classList.toggle('hidden', !isLoading);
  processCard.setAttribute('aria-busy', String(isLoading));
  runBtn.disabled = isLoading;
}

function resetResult() {
  recordId = null;
  latestRows = [];
  basicBody.innerHTML = '';
  itemsBody.innerHTML = '';
  resultArea.classList.add('hidden');
  warnings.classList.add('hidden');
  warnings.innerHTML = '';
  clearError();
  csvBtn.disabled = true;
  excelBtn.disabled = true;
}

function displayError(message) {
  errorMessage.textContent = message;
  errorMessage.classList.remove('hidden');
  errorMessage.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

function clearError() {
  errorMessage.textContent = '';
  errorMessage.classList.add('hidden');
}

function showWarnings(warningList) {
  if (warningList.length === 0) {
    warnings.classList.add('hidden');
    warnings.innerHTML = '';
    return;
  }

  warnings.innerHTML = warningList
    .map((warning) => `<div>⚠ ${escapeHtml(String(warning))}</div>`)
    .join('');
  warnings.classList.remove('hidden');
}

function renderResult(basicInfo, items) {
  // 上部：基礎情報
  basicBody.innerHTML = basicInfo
    .map((row) => `
      <tr>
        <td>${escapeHtml(String(row.key ?? ''))}</td>
        <td>${escapeHtml(String(row.value ?? ''))}</td>
        <td>${escapeHtml(String(row.source ?? ''))}</td>
      </tr>
    `).join('');

  // 下部：品目明細（カラムを動的に生成）
  if (items.length > 0) {
    const itemKeys = Object.keys(items[0]);

    // ヘッダーを動的生成
    const thead = document.querySelector('#items-table thead tr');
    thead.innerHTML = itemKeys.map(k => `<th>${escapeHtml(k)}</th>`).join('');

    // 行を動的生成
    itemsBody.innerHTML = items.map(item =>
      `<tr>${itemKeys.map(k => `<td>${escapeHtml(formatValue(k, item[k]))}</td>`).join('')}</tr>`
    ).join('');
  } else {
    itemsBody.innerHTML = '<tr><td colspan="11">品目明細なし</td></tr>';
  }

  resultArea.classList.remove('hidden');

  // モックのlatestRows互換
  latestRows = basicInfo.map(r => ({ key: r.key, value: r.value, source: r.source }));
}

async function downloadExport(type) {
  if (!recordId) {
    displayError('先にOCR解析・計算を実行してください。');
    return;
  }

  const endpoint = type === 'excel' ? 'excel' : 'csv';
  const defaultFileName = type === 'excel' ? 'export.xlsx' : 'export.csv';

  try {
    const res = await fetch(`${API_BASE}/api/export/${endpoint}/${recordId}`);

    if (!res.ok) {
      const errorText = await res.text();
      throw new Error(`APIエラー: ${res.status} ${res.statusText}\n${errorText}`);
    }

    const blob = await res.blob();
    const fileName = getFileNameFromResponse(res) || defaultFileName;
    await saveOrDownloadBlob(blob, fileName, type);
  } catch (error) {
    if (error.name === 'AbortError') {
      return;
    }

    console.error(error);
    displayError(`ファイル出力に失敗しました。\n${error.message}`);
  }
}

function downloadBlob(blob, fileName) {
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');

  a.href = url;
  a.download = fileName;
  document.body.appendChild(a);
  a.click();
  a.remove();

  URL.revokeObjectURL(url);
}

async function saveOrDownloadBlob(blob, fileName, type) {
  if ('showSaveFilePicker' in window) {
    const fileTypes = {
      csv: {
        description: 'CSVファイル',
        accept: { 'text/csv': ['.csv'] },
      },
      excel: {
        description: 'Excelファイル',
        accept: { 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'] },
      },
    };

    try {
      const handle = await window.showSaveFilePicker({
        suggestedName: fileName,
        types: [fileTypes[type] || fileTypes.csv],
      });
      const writable = await handle.createWritable();
      await writable.write(blob);
      await writable.close();
      return;
    } catch (err) {
      // キャンセル時は何もしない
      if (err.name === 'AbortError') return;
    }
  }

  downloadBlob(blob, fileName);
}

function getFileNameFromResponse(res) {
  const disposition = res.headers.get('Content-Disposition');

  if (!disposition) {
    return null;
  }

  const utf8FileNameMatch = disposition.match(/filename\*=UTF-8''([^;]+)/i);
  if (utf8FileNameMatch) {
    return decodeURIComponent(utf8FileNameMatch[1]);
  }

  const fileNameMatch = disposition.match(/filename="?([^";]+)"?/i);
  if (fileNameMatch) {
    return fileNameMatch[1];
  }

  return null;
}


// 金額系キーにカンマ区切りを適用
const AMOUNT_KEYS = ['unit_price', 'total_amount', 'total_cny', 'total_jpy', 'import_total_jpy'];

function formatValue(key, value) {
  if (value === null || value === undefined || value === '') return '抽出できず';
  // 整形済み文字列（例: "11,000,000円"）はそのまま返す
  if (typeof value === 'string' && value.includes('円')) return value;
  if (AMOUNT_KEYS.some(k => key.toLowerCase().includes(k))) {
    const num = parseFloat(String(value).replace(/,/g, ''));
    if (!isNaN(num)) return num.toLocaleString();
  }
  return String(value);
}

function escapeHtml(value) {
  return value
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}
