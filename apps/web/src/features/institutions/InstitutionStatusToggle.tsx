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
import { apiFetch, ApiError } from "@/lib/api/browser-client";

export function InstitutionStatusToggle({
  institutionId,
  isActive,
}: {
  institutionId: number;
  isActive: boolean;
}) {
  const router = useRouter();
  const [open, setOpen] = useState(false);
  const [reason, setReason] = useState("");
  const [pending, setPending] = useState(false);

  async function handleConfirm() {
    setPending(true);
    try {
      await apiFetch(`/institutions/${institutionId}/status`, {
        method: "PATCH",
        body: JSON.stringify({ is_active: !isActive, reason }),
      });
      toast.success(isActive ? "Institution deactivated" : "Institution activated");
      setOpen(false);
      setReason("");
      router.refresh();
    } catch (error) {
      toast.error(error instanceof ApiError ? error.message : "Could not update status");
    } finally {
      setPending(false);
    }
  }

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button variant="outline" size="sm">
          {isActive ? "Deactivate" : "Activate"}
        </Button>
      </DialogTrigger>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>{isActive ? "Deactivate" : "Activate"} institution</DialogTitle>
          <DialogDescription>
            This is recorded on the audit trail with your reason.
          </DialogDescription>
        </DialogHeader>
        <div className="space-y-2">
          <Label htmlFor="status-reason">Reason</Label>
          <Textarea
            id="status-reason"
            value={reason}
            onChange={(e) => setReason(e.target.value)}
            rows={3}
          />
        </div>
        <DialogFooter>
          <Button onClick={handleConfirm} disabled={pending || reason.trim().length < 3}>
            {pending && <Loader2 className="size-4 animate-spin" />}
            Confirm
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
