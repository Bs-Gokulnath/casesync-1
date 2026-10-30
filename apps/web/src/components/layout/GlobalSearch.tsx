"use client";

import { useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import { AnimatePresence, motion } from "motion/react";
import { Search, Building2, FileText, Loader2 } from "lucide-react";
import { apiFetch } from "@/lib/api/browser-client";
import type { Complaint, Institution, Page } from "@/types/api";

export function GlobalSearch() {
  const router = useRouter();
  const [query, setQuery] = useState("");
  const [open, setOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [institutions, setInstitutions] = useState<Institution[]>([]);
  const [complaints, setComplaints] = useState<Complaint[]>([]);
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (query.trim().length < 2) {
      return;
    }
    const handle = setTimeout(async () => {
      setLoading(true);
      try {
        const [i, c] = await Promise.all([
          apiFetch<Page<Institution>>(`/institutions?q=${encodeURIComponent(query)}&page_size=4`),
          apiFetch<Page<Complaint>>(`/complaints?q=${encodeURIComponent(query)}&page_size=4`),
        ]);
        setInstitutions(i.items);
        setComplaints(c.items);
      } catch {
        setInstitutions([]);
        setComplaints([]);
      } finally {
        setLoading(false);
      }
    }, 300);
    return () => clearTimeout(handle);
  }, [query]);

  useEffect(() => {
    function onClickOutside(e: MouseEvent) {
      if (containerRef.current && !containerRef.current.contains(e.target as Node)) {
        setOpen(false);
      }
    }
    document.addEventListener("mousedown", onClickOutside);
    return () => document.removeEventListener("mousedown", onClickOutside);
  }, []);

  const hasResults = institutions.length > 0 || complaints.length > 0;
  const showPanel = open && query.trim().length >= 2;

  function go(path: string) {
    setOpen(false);
    setQuery("");
    router.push(path);
  }

  return (
    <div ref={containerRef} className="relative w-full max-w-md">
      <div className="relative">
        <Search className="text-muted-foreground pointer-events-none absolute top-1/2 left-3 size-4 -translate-y-1/2" />
        <input
          value={query}
          onChange={(e) => {
            setQuery(e.target.value);
            setOpen(true);
          }}
          onFocus={() => setOpen(true)}
          placeholder="Search institutions or cases..."
          className="border-input bg-input/40 placeholder:text-muted-foreground focus:ring-ring/50 h-9 w-full rounded-full border pr-3 pl-9 text-sm text-white transition-all outline-none focus:ring-2"
        />
        {loading && (
          <Loader2 className="text-muted-foreground absolute top-1/2 right-3 size-3.5 -translate-y-1/2 animate-spin" />
        )}
      </div>

      <AnimatePresence>
        {showPanel && (
          <motion.div
            initial={{ opacity: 0, y: -6, scale: 0.98 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: -6, scale: 0.98 }}
            transition={{ duration: 0.15 }}
            className="glass absolute top-11 left-0 z-50 max-h-96 w-[28rem] overflow-y-auto rounded-2xl p-2 shadow-2xl"
          >
            {!hasResults && !loading && (
              <p className="text-muted-foreground px-3 py-6 text-center text-sm">
                No matches for &quot;{query}&quot;
              </p>
            )}
            {institutions.length > 0 && (
              <div className="mb-1">
                <p className="text-muted-foreground px-3 py-1.5 text-[11px] font-semibold tracking-wide uppercase">
                  Institutions
                </p>
                {institutions.map((inst) => (
                  <button
                    key={inst.id}
                    onClick={() => go(`/institutions/${inst.id}`)}
                    className="hover:bg-accent/10 flex w-full items-center gap-3 rounded-xl px-3 py-2 text-left text-sm transition-colors"
                  >
                    <Building2 className="text-accent size-4 shrink-0" />
                    <span className="truncate">{inst.name}</span>
                    <span className="text-muted-foreground ml-auto font-mono text-xs">
                      {inst.institution_code}
                    </span>
                  </button>
                ))}
              </div>
            )}
            {complaints.length > 0 && (
              <div>
                <p className="text-muted-foreground px-3 py-1.5 text-[11px] font-semibold tracking-wide uppercase">
                  Complaints
                </p>
                {complaints.map((c) => (
                  <button
                    key={c.id}
                    onClick={() => go(`/complaints/${c.id}`)}
                    className="hover:bg-primary/10 flex w-full items-center gap-3 rounded-xl px-3 py-2 text-left text-sm transition-colors"
                  >
                    <FileText className="size-4 shrink-0 text-[#7c6cff]" />
                    <span className="truncate">{c.subject}</span>
                    <span className="text-muted-foreground ml-auto font-mono text-xs">
                      {c.case_reference}
                    </span>
                  </button>
                ))}
              </div>
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
