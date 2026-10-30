"use client";

import { useRef, useState } from "react";
import { useRouter } from "next/navigation";
import { FileText, Loader2, Upload } from "lucide-react";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import { ApiError } from "@/lib/api/browser-client";

interface DocumentItem {
  id: number;
  file_name: string;
  content_type: string;
  size_bytes: number;
  uploaded_at: string;
}

function formatSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

function readCsrfCookie(): string {
  const match = document.cookie.match(/(?:^|; )casesync_csrf=([^;]*)/);
  return match ? decodeURIComponent(match[1]) : "";
}

export function DocumentsSection({
  complaintId,
  documents,
  canUpload,
}: {
  complaintId: number;
  documents: DocumentItem[];
  canUpload: boolean;
}) {
  const router = useRouter();
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [uploading, setUploading] = useState(false);

  async function handleFileChange(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;

    setUploading(true);
    try {
      const formData = new FormData();
      formData.append("file", file);
      const response = await fetch(`/api/v1/complaints/${complaintId}/documents`, {
        method: "POST",
        body: formData,
        headers: { "X-CSRF-Token": readCsrfCookie() },
        credentials: "same-origin",
      });
      if (!response.ok) {
        const body = await response.json().catch(() => null);
        throw new ApiError(response.status, body);
      }
      toast.success("Document uploaded");
      router.refresh();
    } catch (error) {
      toast.error(error instanceof ApiError ? error.message : "Could not upload document");
    } finally {
      setUploading(false);
      if (fileInputRef.current) fileInputRef.current.value = "";
    }
  }

  return (
    <section className="glass rounded-2xl p-5">
      <div className="flex items-center justify-between">
        <h2 className="font-display text-sm font-semibold text-white">Documents</h2>
        {canUpload && (
          <>
            <input
              ref={fileInputRef}
              type="file"
              className="hidden"
              accept=".pdf,.png,.jpg,.jpeg,.doc,.docx"
              onChange={handleFileChange}
            />
            <Button
              variant="outline"
              size="sm"
              disabled={uploading}
              onClick={() => fileInputRef.current?.click()}
            >
              {uploading ? (
                <Loader2 className="size-4 animate-spin" />
              ) : (
                <Upload className="size-4" />
              )}
              Upload
            </Button>
          </>
        )}
      </div>

      {documents.length === 0 ? (
        <p className="text-muted-foreground mt-3 text-sm">No documents attached.</p>
      ) : (
        <ul className="divide-border/60 mt-3 divide-y">
          {documents.map((doc) => (
            <li key={doc.id} className="flex items-center gap-2 py-2">
              <FileText className="size-4 shrink-0 text-[#22d3ee]" />
              <a
                href={`/api/v1/complaints/${complaintId}/documents/${doc.id}`}
                className="flex-1 text-sm text-white hover:text-[#9b8dff] hover:underline"
                target="_blank"
                rel="noreferrer"
              >
                {doc.file_name}
              </a>
              <span className="text-muted-foreground text-xs">{formatSize(doc.size_bytes)}</span>
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}
