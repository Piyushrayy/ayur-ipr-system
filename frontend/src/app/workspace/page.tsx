"use client";

import React, { useState } from "react";
import Link from "next/link";
import { MOCK_WORKSPACE_DATA, Citation } from "../../lib/mockData";

export default function WorkspacePage() {
  const [jurisdiction, setJurisdiction] = useState<"India" | "International">("India");
  const [selectedCitation, setSelectedCitation] = useState<Citation | null>(
    MOCK_WORKSPACE_DATA.india.citations[0]
  );
  const [activePage, setActivePage] = useState<number>(
    MOCK_WORKSPACE_DATA.india.citations[0].page_number
  );
  const [searchQuery, setSearchQuery] = useState(
    "Withania somnifera (Ashwagandha) + Curcumin Extract"
  );

  const activeData =
    jurisdiction === "India" ? MOCK_WORKSPACE_DATA.india : MOCK_WORKSPACE_DATA.international;

  const handleCitationClick = (citation: Citation) => {
    setSelectedCitation(citation);
    setActivePage(citation.page_number);
  };

  const handleJurisdictionChange = (newJur: "India" | "International") => {
    setJurisdiction(newJur);
    const firstCit =
      newJur === "India"
        ? MOCK_WORKSPACE_DATA.india.citations[0]
        : MOCK_WORKSPACE_DATA.international.citations[0];
    setSelectedCitation(firstCit);
    setActivePage(firstCit ? firstCit.page_number : 1);
  };

  return (
    <div className="flex flex-col h-screen w-full bg-slate-100 text-slate-800 font-sans overflow-hidden">
      {/* Top Bar: Gov Identity + Jurisdiction Switcher */}
      <header className="h-14 bg-[#16324f] text-white flex items-center justify-between px-6 border-b border-slate-700 shrink-0">
        <div className="flex items-center gap-4">
          <Link
            href="/IPSAKTI.HTML"
            className="text-xs bg-slate-800 hover:bg-slate-700 px-2.5 py-1.5 rounded border border-slate-600 transition"
          >
            ← Back to Portal
          </Link>
          <div className="flex flex-col">
            <span className="font-bold text-sm tracking-wide text-white">
              AYUSH IPR STATUTORY WORKSPACE
            </span>
            <span className="text-[10px] text-amber-300">
              Dual-Pane Evidence Engine & Regulatory Classification
            </span>
          </div>
        </div>

        {/* Jurisdiction Toggle Switch */}
        <div className="flex items-center bg-slate-900/60 p-1 rounded-lg border border-slate-600">
          <button
            onClick={() => handleJurisdictionChange("India")}
            className={`px-3 py-1 text-xs font-semibold rounded transition ${
              jurisdiction === "India"
                ? "bg-[#005a9c] text-white shadow"
                : "text-slate-300 hover:text-white"
            }`}
          >
            🇮🇳 India (Patents Act & BDA)
          </button>
          <button
            onClick={() => handleJurisdictionChange("International")}
            className={`px-3 py-1 text-xs font-semibold rounded transition ${
              jurisdiction === "International"
                ? "bg-[#005a9c] text-white shadow"
                : "text-slate-300 hover:text-white"
            }`}
          >
            🌐 International (PCT / WIPO)
          </button>
        </div>
      </header>

      {/* Main Dual-Pane Layout */}
      <main className="flex flex-1 overflow-hidden">
        {/* Left Column: Classification, Legal Assessment & Citation Cards */}
        <section className="w-1/2 flex flex-col border-r border-slate-300 bg-white overflow-y-auto">
          {/* Query Bar */}
          <div className="p-4 bg-slate-50 border-b border-slate-200">
            <label className="text-[11px] uppercase tracking-wider font-bold text-slate-500 block mb-1">
              Active Formulation / Query
            </label>
            <div className="flex gap-2">
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full text-xs px-3 py-2 border border-slate-300 rounded focus:ring-1 focus:ring-blue-600 focus:outline-none"
              />
              <button className="bg-[#16324f] text-white text-xs px-4 py-2 rounded font-semibold hover:bg-[#005a9c] shrink-0">
                Re-Assess
              </button>
            </div>
          </div>

          <div className="p-5 space-y-5">
            {/* Regulatory Classification Status */}
            <div className="p-3.5 bg-blue-50/70 border border-blue-200 rounded-lg">
              <div className="flex justify-between items-start mb-2">
                <span className="text-[11px] font-bold text-[#005a9c] uppercase">
                  Statutory Classification
                </span>
                <span className="bg-red-100 text-red-800 text-[10px] font-bold px-2 py-0.5 rounded border border-red-200">
                  {activeData.regulatory_bar}
                </span>
              </div>
              <p className="text-xs font-medium text-slate-700">
                Target Category: <strong>{activeData.product_category}</strong>
              </p>
            </div>

            {/* AI Grounded Statutory Guidance */}
            <div>
              <div className="flex items-center justify-between mb-2">
                <h3 className="text-xs font-bold text-slate-700 uppercase tracking-wider">
                  AI Statutory Assessment
                </h3>
                <span className="text-[10px] font-bold text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200">
                  Confidence: {activeData.confidence}
                </span>
              </div>
              <div className="p-4 bg-slate-50 border border-slate-200 rounded-lg text-xs leading-relaxed text-slate-800 text-justify">
                {activeData.answer}
              </div>
            </div>

            {/* Mandatory Citations Cards */}
            <div>
              <h3 className="text-xs font-bold text-slate-700 uppercase tracking-wider mb-2">
                Ground-Truth Citations (Click to inspect evidence)
              </h3>
              <div className="space-y-2.5">
                {activeData.citations.map((citation, idx) => {
                  const isSelected = selectedCitation?.text === citation.text;
                  return (
                    <div
                      key={idx}
                      onClick={() => handleCitationClick(citation)}
                      className={`p-3 rounded-lg border text-xs cursor-pointer transition ${
                        isSelected
                          ? "bg-amber-50/80 border-amber-400 shadow-sm"
                          : "bg-white border-slate-200 hover:border-blue-300"
                      }`}
                    >
                      <div className="flex justify-between items-center mb-1">
                        <span className="font-bold text-[#16324f]">
                          {citation.source_name}
                        </span>
                        <span className="bg-slate-200 text-slate-700 text-[10px] px-1.5 py-0.5 rounded font-mono font-bold">
                          p. {citation.page_number} | {citation.section}
                        </span>
                      </div>
                      <p className="text-slate-600 line-clamp-2 italic">
                        "{citation.text}"
                      </p>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>
        </section>

        {/* Right Column: PDF Evidence Viewer Shell */}
        <section className="w-1/2 flex flex-col bg-slate-200">
          {/* PDF Viewer Top Navigation Strip */}
          <div className="h-11 bg-slate-800 text-white flex items-center justify-between px-4 text-xs shrink-0 border-b border-slate-700">
            <span className="font-mono text-[11px] truncate max-w-[240px]">
              📄 {selectedCitation ? selectedCitation.source_name : "Document"}
            </span>
            <div className="flex items-center gap-3">
              <span className="bg-slate-700 px-2 py-0.5 rounded text-[11px]">
                Page: <strong>{activePage}</strong> / 84
              </span>
              <div className="flex gap-1">
                <button
                  onClick={() => setActivePage((p) => Math.max(1, p - 1))}
                  className="px-2 py-0.5 bg-slate-700 hover:bg-slate-600 rounded text-[10px]"
                >
                  ◀ Prev
                </button>
                <button
                  onClick={() => setActivePage((p) => p + 1)}
                  className="px-2 py-0.5 bg-slate-700 hover:bg-slate-600 rounded text-[10px]"
                >
                  Next ▶
                </button>
              </div>
            </div>
          </div>

          {/* PDF Document Canvas & Dynamic Coordinate BBox Highlight */}
          <div className="flex-1 overflow-auto p-6 flex justify-center items-start">
            <div className="w-[520px] min-h-[680px] bg-white shadow-xl border border-slate-300 p-8 relative flex flex-col justify-between text-slate-800">
              <div>
                <div className="border-b border-slate-200 pb-3 mb-6 flex justify-between items-center text-[10px] text-slate-400 font-mono">
                  <span>THE GAZETTE OF INDIA : EXTRAORDINARY</span>
                  <span>[PART II—SEC. 1]</span>
                </div>

                <div className="space-y-4 text-xs font-serif leading-relaxed text-slate-700 select-none">
                  <p className="text-center font-bold text-sm tracking-wide text-slate-900 uppercase">
                    {selectedCitation ? selectedCitation.section : "Section 3"}
                  </p>
                  <p className="text-justify text-slate-400">
                    The following Act of Parliament received the assent of the President
                    and is hereby published for general information. Provisions apply to all
                    formulations derived from biological materials indigenous to India...
                  </p>

                  {/* Active Highlighted Bounding Box */}
                  <div className="my-4 p-3 bg-amber-100/90 border-2 border-amber-500 rounded relative text-slate-900 shadow-sm">
                    <span className="absolute -top-2.5 right-2 bg-amber-500 text-white text-[9px] font-mono px-1 rounded uppercase tracking-wider font-bold">
                      Retrieved Ground Truth
                    </span>
                    <p className="font-semibold text-[11.5px] leading-snug">
                      {selectedCitation ? selectedCitation.text : "No citation selected."}
                    </p>
                  </div>

                  <p className="text-justify text-slate-400">
                    Provided that any extraction process involving non-obvious enzymatic or
                    chemical co-actions validated by quantitative biological assays may be
                    subject to examination in accordance with Chapter III rules...
                  </p>
                </div>
              </div>

              {/* PDF Footer Metadata */}
              <div className="border-t border-slate-200 pt-3 flex justify-between items-center text-[10px] text-slate-400 font-mono">
                <span>AYUSH IPR Corpus ID: {selectedCitation?.document_id}</span>
                <span>Page {activePage}</span>
              </div>
            </div>
          </div>
        </section>
      </main>
    </div>
  );
}