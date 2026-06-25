const API_BASE = '';
const MOCK_DELAY_MS = 1000;

const pdfFileInput = document.getElementById('pdf-file');
const imageFileInput = document.getElementById('image-file');
const runBtn = document.getElementById('run-btn');
const loading = document.getElementById('loading');
const warnings = document.getElementById('warnings');
const resultTable = document.getElementById('result-table');
const resultBody = document.getElementById('result-body');
const csvBtn = document.getElementById('csv-btn');
const excelBtn = document.getElementById('excel-btn');
const mockModeInput = document.getElementById('mock-mode');
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

pdfFileInput.addEventListener('change', () => handleFileChange(pdfFileInput, pdfFileName));
imageFileInput.addEventListener('change', () => handleFileChange(imageFileInput, imageFileName));
runBtn.addEventListener('click', runProcess);
csvBtn.addEventListener('click', () => downloadExport('csv'));
excelBtn.addEventListener('click', () => downloadExport('excel'));
mockModeInput.addEventListener('change', resetResult);

setupDropZone(pdfDropZone, pdfFileInput, pdfFileName, 'pdf');
setupDropZone(imageDropZone, imageFileInput, imageFileName, 'image');

// 為替レートモード切り替え
[rateAuto, rateManual].forEach(radio => {
  radio.addEventListener('change', () => {
    rateManualInput.classList.toggle('hidden', rateAuto.checked);
  });
});

function handleFileChange(input, fileNameElement) {
  fileNameElement.textContent = input.files[0]?.name || '選択されていません';
  clearError();
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

  runBtn.disabled = !(hasPdf && hasImage);
}

async function runProcess() {
  const pdfFile = pdfFileInput.files[0];
  const imageFile = imageFileInput.files[0];

  if (!pdfFile || !imageFile) {
    displayError('PDFファイルと画像ファイルの両方を選択してください。');
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
    const data = mockModeInput.checked
      ? await runMockProcess(pdfFile, imageFile)
      : await requestProcess(formData);

    if (data.status === 'error') {
      displayError(data.message);
      return;
    }

    recordId = data.record_id;

    showWarnings(data.warnings || []);
    renderResultTable(data.fields || [], data.calculations || []);

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

async function runMockProcess(pdfFile, imageFile) {
  await delay(MOCK_DELAY_MS);

  return {
    record_id: `mock-${Date.now()}`,
    status: 'ok',
    warnings: ['モックデータを表示しています。実際のOCR処理は行われていません。'],
    fields: [
      { key: 'pdf_file_name', value: pdfFile.name, source: 'pdf' },
      { key: 'image_file_name', value: imageFile.name, source: 'image' },
      { key: 'item_name', value: 'サンプル商品', source: 'pdf' },
      { key: 'quantity', value: 100, source: 'image' },
      { key: 'unit_price_cny', value: 50, source: 'pdf' },
      { key: 'exchange_rate', value: 20.5, source: 'pdf' },
    ],
    calculations: [
      { key: 'total_cny', value: 5000, formula: 'quantity * unit_price_cny' },
      { key: 'total_jpy', value: 102500, formula: 'total_cny * exchange_rate' },
      { key: 'import_total_jpy', value: 110625, formula: 'total_jpy + shipping_jpy + tariff_jpy' },
    ],
  };
}

function delay(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

function setLoading(isLoading) {
  loading.classList.toggle('hidden', !isLoading);
  processCard.setAttribute('aria-busy', String(isLoading));
  runBtn.disabled = isLoading;
}

function resetResult() {
  recordId = null;
  latestRows = [];
  resultBody.innerHTML = '';
  resultTable.classList.add('hidden');
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

function renderResultTable(fields, calculations) {
  const rows = [];

  fields.forEach((field) => {
    rows.push({
      key: field.key,
      value: field.value,
      source: field.source,
    });
  });

  calculations.forEach((calculation) => {
    rows.push({
      key: calculation.key,
      value: calculation.value,
      source: 'calculated',
    });
  });

  latestRows = rows;

  resultBody.innerHTML = rows
    .map((row) => `
      <tr>
        <td>${escapeHtml(String(row.key ?? ''))}</td>
        <td>${escapeHtml(String(row.value ?? ''))}</td>
        <td>${escapeHtml(String(row.source ?? ''))}</td>
      </tr>
    `)
    .join('');

  resultTable.classList.toggle('hidden', rows.length === 0);
}

async function downloadExport(type) {
  if (!recordId) {
    displayError('先にOCR解析・計算を実行してください。');
    return;
  }

  const endpoint = type === 'excel' ? 'excel' : 'csv';
  const defaultFileName = type === 'excel' ? 'export.xlsx' : 'export.csv';

  try {
    if (mockModeInput.checked) {
      await downloadMockExport(type);
      return;
    }

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

async function downloadMockExport(type) {
  const header = ['項目名', '値', '抽出元'];

  if (type === 'csv') {
    const csv = [header, ...latestRows.map((row) => [row.key, row.value, row.source])]
      .map((row) => row.map(escapeCsvValue).join(','))
      .join('\r\n');
    await saveOrDownloadBlob(
      new Blob([`\uFEFF${csv}`], { type: 'text/csv;charset=utf-8' }),
      'mock-export.csv',
      type,
    );
    return;
  }

  const tableRows = [header, ...latestRows.map((row) => [row.key, row.value, row.source])]
    .map((row) => `<tr>${row.map((value) => `<td>${escapeHtml(String(value ?? ''))}</td>`).join('')}</tr>`)
    .join('');
  const excelHtml = `<html><head><meta charset="UTF-8"></head><body><table>${tableRows}</table></body></html>`;
  await saveOrDownloadBlob(
    new Blob([excelHtml], { type: 'application/vnd.ms-excel;charset=utf-8' }),
    'mock-export.xls',
    type,
  );
}

function escapeCsvValue(value) {
  const text = String(value ?? '');
  return `"${text.replace(/"/g, '""')}"`;
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

function escapeHtml(value) {
  return value
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}
