let currentJurisdiction = "india";
let currentPage = 1;

// PDF ka folder path decide karne wala function
function getDocumentRelativePath(docName, jurisdiction) {
  const isIntl = jurisdiction.toLowerCase() === "international";
  const folder = isIntl ? "international" : "indian";
  
  // Default files agar backend se naam na aaye
  const defaultDoc = isIntl ? "pct_international.pdf" : "patentact_1970_india.pdf";
  const finalDoc = (docName && docName.trim()) ? docName.trim() : defaultDoc;

  return `/documents/${folder}/${encodeURIComponent(finalDoc)}`;
}

let currentDocUrl = getDocumentRelativePath("patentact_1970_india.pdf", "india");
// 1. Initial Modal Action
function selectInitialJurisdiction(jurisdiction) {
  setJurisdiction(jurisdiction);
  const modal = document.getElementById("jurisdiction-modal");
  if (modal) modal.style.display = "none";
}

// 2. Jurisdiction Switcher Handler
function setJurisdiction(jurisdiction) {
  currentJurisdiction = jurisdiction;

  const btnIndia = document.getElementById("btn-jurisdiction-india");
  const btnIntl = document.getElementById("btn-jurisdiction-intl");

  if (jurisdiction === "india") {
    btnIndia.className = "px-3.5 py-1 rounded text-xs font-bold transition bg-[#c8963e] text-slate-900 shadow";
    btnIntl.className = "px-3.5 py-1 rounded text-xs font-medium text-slate-300 hover:text-white transition";
  } else {
    btnIntl.className = "px-3.5 py-1 rounded text-xs font-bold transition bg-[#c8963e] text-slate-900 shadow";
    btnIndia.className = "px-3.5 py-1 rounded text-xs font-medium text-slate-300 hover:text-white transition";
  }
}

// 3. Screen Splitting & PDF Display
function openPdfViewer(pdfUrl, title, page = 1) {
  const chatPanel = document.getElementById("chat-panel");
  const pdfPanel = document.getElementById("pdf-panel");
  const pdfFrame = document.getElementById("pdf-frame");
  const pdfTitle = document.getElementById("pdf-title");
  const pageInput = document.getElementById("pdf-page-num");

  const cleanUrl = (pdfUrl || "").split("#")[0];
  const targetPage = Number(page) || 1;

  currentDocUrl = cleanUrl;
  currentPage = targetPage;

  // Split into 50-50 view
  if (chatPanel) {
    chatPanel.classList.remove("w-full");
    chatPanel.classList.add("w-1/2");
  }

  if (pdfPanel) {
    pdfPanel.classList.remove("hidden");
  }

  if (pdfTitle) {
    pdfTitle.innerHTML = `<i class="fa-solid fa-file-pdf text-rose-500"></i> ${escapeHtml(title)}`;
  }

  if (pageInput) {
    pageInput.value = targetPage;
  }

  if (pdfFrame) {
    // Force re-render taaki page jump execute ho
    pdfFrame.src = "about:blank";
    setTimeout(() => {
      pdfFrame.src = `${cleanUrl}#page=${targetPage}&zoom=83`;
    }, 50);
  }
}

function closePdfPanel() {
  const chatPanel = document.getElementById("chat-panel");
  const pdfPanel = document.getElementById("pdf-panel");

  pdfPanel.classList.add("hidden");
  chatPanel.classList.remove("w-1/2");
  chatPanel.classList.add("w-full");
}

function nextPdfPage() {
  currentPage += 1;
  openPdfViewer(currentDocUrl, document.getElementById("pdf-title").innerText, currentPage);
}

function prevPdfPage() {
  if (currentPage > 1) {
    currentPage -= 1;
    openPdfViewer(currentDocUrl, document.getElementById("pdf-title").innerText, currentPage);
  }
}

// // 4. Query Submission & Live Assistant Card Generation
async function handleQuerySubmit(event) {
  event.preventDefault();
  const input = document.getElementById("query-input");
  const chatHistory = document.getElementById("chat-history");
  const emptyState = document.getElementById("empty-state");
  const query = input.value.trim();

  if (!query) return;

  // Clear initial empty placeholder
  if (emptyState) emptyState.remove();

  // 1. Append User Message (Exact Navy Bubble Style)
  chatHistory.innerHTML += `
    <div class="flex justify-end">
      <div class="bg-[#0b3b60] text-white text-sm font-medium rounded-lg px-5 py-3 max-w-xl shadow">
        ${escapeHtml(query)}
      </div>
    </div>
  `;

  // 2. Loading State
  const loaderId = "loader-" + Date.now();
  chatHistory.innerHTML += `
    <div id="${loaderId}" class="flex justify-start text-xs text-slate-500 italic items-center gap-2">
      <i class="fa-solid fa-circle-notch fa-spin text-[#0b3b60]"></i>
      Evaluating against ${currentJurisdiction.toUpperCase()} regulatory corpus...
    </div>
  `;
  chatHistory.scrollTop = chatHistory.scrollHeight;
  input.value = "";

  try {
    const res = await fetch("http://127.0.0.1:8000/api/v1/query", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ 
        query: query,
        jurisdiction: currentJurisdiction 
      }),
    });

   const data = await res.json();
console.log("Backend Full Response:", data);
console.log("Backend Citations:", data.citations);

    // Citations Builder with Dynamic Folder Routing
    let citationsHtml = "";
    if (data.citations && data.citations.length > 0) {
      citationsHtml = `
        <div class="pt-4 mt-4 border-t border-slate-200">
          <p class="text-[11px] font-bold text-[#0b3b60] uppercase tracking-wider mb-2.5 flex items-center gap-1.5">
            <i class="fa-solid fa-file-lines text-[#0b3b60]"></i> STATUTORY EVIDENCE CITATIONS (CLICK TO INSPECT SOURCE)
          </p>
          <div class="space-y-2.5">
            ${data.citations.map((c) => {
              const rawDoc = c.source_name || c.source_doc || "";
        let docName = "patentact_1970_india.pdf";

        const lowerDoc = rawDoc.toLowerCase();
        if (lowerDoc.includes("trade mark") || lowerDoc.includes("trademark")) {
          docName = "trade mark act_1999_india.pdf";
        } else if (lowerDoc.includes("copyright")) {
          docName = "copyrightrules_1957_india.pdf";
        } else if (lowerDoc.includes("rules") || lowerDoc.includes("2024")) {
          docName = "patent_rules_2024_india.pdf";
        } else if (lowerDoc.includes("trips")) {
          docName = "TRIPS_international.pdf";
        } else if (lowerDoc.includes("paris")) {
          docName = "Paris_Convention_international.pdf";
        } else if (lowerDoc.includes("pct")) {
          docName = "pct_international.pdf";
        } else if (currentJurisdiction === "international") {
          docName = "pct_international.pdf";
        }

        const pageNum = parseInt(c.page_number || c.page || 1, 10);
              const pdfUrl = getDocumentRelativePath(docName, currentJurisdiction);
              const sectionText = c.section || "Relevant Clause";
             const clauseText = c.highlight_text || c.text || "";
              
              return `
               <div data-url="${pdfUrl}" data-doc="${escapeHtml(docName)}" data-page="${pageNum}" onclick="openPdfViewer(this.dataset.url, this.dataset.doc, parseInt(this.dataset.page, 10))"
                     class="cursor-pointer border border-[#eab308]/60 bg-[#fffdf5] hover:bg-[#fef9e7] rounded-lg p-3.5 text-xs transition duration-150 shadow-sm">
                  <div class="flex justify-between font-bold text-[#92400e]">
                    <span class="text-[13px]">${escapeHtml(docName)}</span>
                    <span class="text-slate-800 font-semibold">Page ${pageNum}</span>
                  </div>
                  <div class="font-bold text-[#b45309] my-1 text-[12px]">${escapeHtml(sectionText)}</div>
                  <p class="italic text-slate-600 leading-relaxed font-['Noto_Sans']">
                    "${escapeHtml(clauseText)}"
                  </p>
                </div>
              `;
            }).join("")}
          </div>
        </div>
      `;

      // Automatically split screen and open first citation PDF
      const firstCite = data.citations[0];
      const firstDocName = firstCite.source_doc || (currentJurisdiction === "international" ? "pct_international.pdf" : "patentact_1970_india.pdf");
      const firstDocUrl = getDocumentRelativePath(firstDocName, currentJurisdiction);
      
      openPdfViewer(firstDocUrl, firstDocName, firstCite.page || 1);
    }

// 3. Append Deliberation Box
    document.getElementById(loaderId)?.remove();
    const confidenceHtml = getConfidenceBadge(data.confidence_score || data.confidence);

    chatHistory.innerHTML += `
      <div class="flex justify-start w-full">
        <div class="bg-white border border-slate-200 border-l-4 border-l-[#0b3b60] rounded-lg p-5 w-full shadow-sm text-[13px] text-slate-800 leading-relaxed">
          <div class="flex items-center justify-between pb-3 mb-3 border-b border-slate-100">
            <span class="text-[11px] font-bold text-[#0b3b60] tracking-wider uppercase flex items-center gap-1.5">
              <i class="fa-solid fa-scale-balanced text-[#0b3b60]"></i> STATUTORY EVALUATION VERDICT
            </span>
            ${confidenceHtml}
          </div>
          <p class="mb-2 whitespace-pre-line">${escapeHtml(data.answer)}</p>
          ${citationsHtml}
        </div>
      </div>
    `;
    chatHistory.scrollTop = chatHistory.scrollHeight;

  } catch (err) {
    document.getElementById(loaderId)?.remove();
    chatHistory.innerHTML += `
      <div class="text-rose-700 text-xs bg-rose-50 border border-rose-200 p-3 rounded-md">
        Failed to deliberate: ${escapeHtml(err.message)}
      </div>
    `;
    chatHistory.scrollTop = chatHistory.scrollHeight;
  }
}
// HTML sanitize function (Error Fix)
function escapeHtml(text) {
  if (text === null || text === undefined) return "";
  const div = document.createElement("div");
  div.textContent = String(text);
  return div.innerHTML;
}
function getConfidenceBadge(confidence) {
  const level = (confidence || "medium").toLowerCase();
  
  const config = {
    high: {
      label: "High Confidence",
      bg: "bg-emerald-50",
      text: "text-emerald-700",
      border: "border-emerald-300",
      icon: "fa-circle-check"
    },
    medium: {
      label: "Moderate Confidence",
      bg: "bg-amber-50",
      text: "text-amber-700",
      border: "border-amber-300",
      icon: "fa-triangle-exclamation"
    },
    low: {
      label: "Low Confidence (Review Required)",
      bg: "bg-rose-50",
      text: "text-rose-700",
      border: "border-rose-300",
      icon: "fa-circle-exclamation"
    }
  };

  const badge = config[level] || config.medium;

  return `
    <span class="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[11px] font-semibold border ${badge.bg} ${badge.text} ${badge.border} shadow-xs">
      <i class="fa-solid ${badge.icon} text-[10px]"></i>
      ${badge.label}
    </span>
  `;
}