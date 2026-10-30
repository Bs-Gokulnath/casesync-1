"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Loader2 } from "lucide-react";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { apiFetch, ApiError } from "@/lib/api/browser-client";
import type { OverlapAlert, OverlapAlertStatus } from "@/types/api";

const DECISION_OPTIONS: { value: OverlapAlertStatus; label: string }[] = [
  { value: "confirmed", label: "Confirmed — same underlying issue, bureaus should coordinate" },
  { value: "dismissed", label: "Dismissed — false positive" },
  { value: "resolved", label: "Resolved — coordination complete" },
];

export function OverlapDecisionDialog({ alert }: { alert: OverlapAlert }) {
  const router = useRouter();
  const [open, setOpen] = useState(false);
  const [status, setStatus] = useState<OverlapAlertStatus | undefined>();
  const [reason, setReason] = useState("");
  const [pending, setPending] = useState(false);

  async function handleConfirm() {
    if (!status) return;
    setPending(true);
    try {
      await apiFetch(`/overlaps/${alert.id}/decision`, {
        method: "POST",
        body: JSON.stringify({ status, reason }),
      });
      toast.success("Decision recorded");
      setOpen(false);
      router.refresh();
    } catch (error) {
      toast.error(error instanceof ApiError ? error.message : "Could not record decision");
    } finally {
      setPending(false);
    }
  }

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button size="sm">Review</Button>
      </DialogTrigger>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Review overlap alert</DialogTitle>
          <DialogDescription>
            This never merges or changes the underlying cases — it only records your review decision
            for coordination purposes.
          </DialogDescription>
        </DialogHeader>
        <div className="space-y-4">
          <div className="bg-muted/50 text-foreground/80 rounded-xl p-3 text-sm">
            {alert.rationale}
          </div>
          <div className="space-y-2">
            <Label id="overlap-decision-label">Decision</Label>
            <Select value={status} onValueChange={(v) => setStatus(v as OverlapAlertStatus)}>
              <SelectTrigger className="w-full" aria-labelledby="overlap-decision-label">
                <SelectValue placeholder="Select a decision" />
              </SelectTrigger>
              <SelectContent>
                {DECISION_OPTIONS.map((opt) => (
                  <SelectItem key={opt.value} value={opt.value}>
                    {opt.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          <div className="space-y-2">
            <Label htmlFor="decision-reason">Reason</Label>
            <Textarea
              id="decision-reason"
              value={reason}
              onChange={(e) => setReason(e.target.value)}
              rows={3}
            />
          </div>
        </div>
        <DialogFooter>
          <Button onClick={handleConfirm} disabled={pending || !status || reason.trim().length < 3}>
            {pending && <Loader2 className="size-4 animate-spin" />}
            Save decision
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
