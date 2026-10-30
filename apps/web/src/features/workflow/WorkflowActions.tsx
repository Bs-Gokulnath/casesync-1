"use client";

import { useEffect, useState } from "react";
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
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { apiFetch, ApiError } from "@/lib/api/browser-client";
import type { Bureau, Complaint, ComplaintStatus, Officer } from "@/types/api";

function useRefreshOnSuccess() {
  const router = useRouter();
  return () => {
    router.refresh();
  };
}

async function runAction(
  path: string,
  body: Record<string, unknown>,
  onSuccess: () => void,
  successMessage: string,
) {
  try {
    await apiFetch(path, { method: "POST", body: JSON.stringify(body) });
    toast.success(successMessage);
    onSuccess();
  } catch (error) {
    if (error instanceof ApiError) {
      toast.error(error.message || "Action failed");
    } else {
      toast.error("Action failed");
    }
  }
}

function ReasonDialog({
  trigger,
  title,
  description,
  requireReason,
  onConfirm,
}: {
  trigger: React.ReactNode;
  title: string;
  description: string;
  requireReason: boolean;
  onConfirm: (reason: string) => Promise<void>;
}) {
  const [open, setOpen] = useState(false);
  const [reason, setReason] = useState("");
  const [pending, setPending] = useState(false);

  async function handleConfirm() {
    setPending(true);
    try {
      await onConfirm(reason);
      setOpen(false);
      setReason("");
    } finally {
      setPending(false);
    }
  }

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>{trigger}</DialogTrigger>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>{title}</DialogTitle>
          <DialogDescription>{description}</DialogDescription>
        </DialogHeader>
        <div className="space-y-2">
          <Label htmlFor="reason">Reason{requireReason ? "" : " (optional)"}</Label>
          <Textarea
            id="reason"
            value={reason}
            onChange={(e) => setReason(e.target.value)}
            rows={3}
          />
        </div>
        <DialogFooter>
          <Button
            onClick={handleConfirm}
            disabled={pending || (requireReason && reason.trim().length < 3)}
          >
            {pending && <Loader2 className="size-4 animate-spin" />}
            Confirm
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}

const SIMPLE_TRANSITIONS: Record<ComplaintStatus, { to: ComplaintStatus; label: string }[]> = {
  received: [{ to: "under_review", label: "Start Review" }],
  under_review: [
    { to: "under_process", label: "Move to Processing" },
    { to: "pending_information", label: "Request Information" },
  ],
  under_process: [{ to: "pending_information", label: "Request Information" }],
  pending_information: [{ to: "under_process", label: "Resume Processing" }],
  transferred: [{ to: "under_review", label: "Acknowledge & Review" }],
  escalated: [{ to: "under_process", label: "Resume Processing" }],
  disposed: [],
};

export function WorkflowActions({
  complaint,
  bureaus,
  permissions,
}: {
  complaint: Complaint;
  bureaus: Bureau[];
  permissions: string[];
}) {
  const refresh = useRefreshOnSuccess();
  const can = (p: string) => permissions.includes(p);

  const canTransfer = can("complaint:transfer") && complaint.status !== "disposed";
  const canEscalate =
    can("complaint:escalate") &&
    ["under_review", "under_process", "pending_information"].includes(complaint.status);
  const canDispose =
    can("complaint:dispose") &&
    ["under_review", "under_process", "pending_information", "escalated"].includes(
      complaint.status,
    );
  const canReopen = can("complaint:reopen") && complaint.status === "disposed";
  const canAssign = can("complaint:assign") && complaint.status !== "disposed";
  const canTransition = can("complaint:transition");

  const simpleMoves = SIMPLE_TRANSITIONS[complaint.status] ?? [];

  return (
    <div className="flex flex-wrap gap-2">
      {canTransition &&
        simpleMoves.map((move) => (
          <ReasonDialog
            key={move.to}
            trigger={
              <Button variant="outline" size="sm">
                {move.label}
              </Button>
            }
            title={move.label}
            description={`Move this case to "${move.to.replace("_", " ")}".`}
            requireReason={false}
            onConfirm={(reason) =>
              runAction(
                `/complaints/${complaint.id}/transition`,
                { to_status: move.to, reason: reason || null },
                refresh,
                "Status updated",
              )
            }
          />
        ))}

      {canTransfer && <TransferDialog complaint={complaint} bureaus={bureaus} onDone={refresh} />}

      {canEscalate && (
        <ReasonDialog
          trigger={
            <Button variant="outline" size="sm">
              Escalate
            </Button>
          }
          title="Escalate case"
          description="Escalations are recorded on the case history and visible to senior management."
          requireReason
          onConfirm={(reason) =>
            runAction(`/complaints/${complaint.id}/escalate`, { reason }, refresh, "Case escalated")
          }
        />
      )}

      {canDispose && <DisposeDialog complaint={complaint} onDone={refresh} />}

      {canReopen && (
        <ReasonDialog
          trigger={
            <Button variant="outline" size="sm">
              Reopen
            </Button>
          }
          title="Reopen disposed case"
          description="Reopening is an explicitly authorized, audited action."
          requireReason
          onConfirm={(reason) =>
            runAction(`/complaints/${complaint.id}/reopen`, { reason }, refresh, "Case reopened")
          }
        />
      )}

      {canAssign && <AssignDialog complaint={complaint} onDone={refresh} />}
    </div>
  );
}

function TransferDialog({
  complaint,
  bureaus,
  onDone,
}: {
  complaint: Complaint;
  bureaus: Bureau[];
  onDone: () => void;
}) {
  const [open, setOpen] = useState(false);
  const [bureauId, setBureauId] = useState<string | undefined>();
  const [reason, setReason] = useState("");
  const [pending, setPending] = useState(false);

  const otherBureaus = bureaus.filter((b) => b.id !== complaint.bureau_id);

  async function handleConfirm() {
    if (!bureauId) return;
    setPending(true);
    try {
      await runAction(
        `/complaints/${complaint.id}/transfer`,
        { to_bureau_id: Number(bureauId), reason },
        () => {
          onDone();
          setOpen(false);
          setReason("");
          setBureauId(undefined);
        },
        "Case transferred",
      );
    } finally {
      setPending(false);
    }
  }

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button variant="outline" size="sm">
          Transfer
        </Button>
      </DialogTrigger>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Transfer case</DialogTitle>
          <DialogDescription>
            Moves this case to another bureau and clears the current assignment.
          </DialogDescription>
        </DialogHeader>
        <div className="space-y-4">
          <div className="space-y-2">
            <Label id="transfer-bureau-label">Target bureau</Label>
            <Select value={bureauId} onValueChange={setBureauId}>
              <SelectTrigger className="w-full" aria-labelledby="transfer-bureau-label">
                <SelectValue placeholder="Select bureau" />
              </SelectTrigger>
              <SelectContent>
                {otherBureaus.map((b) => (
                  <SelectItem key={b.id} value={String(b.id)}>
                    {b.name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          <div className="space-y-2">
            <Label htmlFor="transfer-reason">Reason</Label>
            <Textarea
              id="transfer-reason"
              value={reason}
              onChange={(e) => setReason(e.target.value)}
              rows={3}
            />
          </div>
        </div>
        <DialogFooter>
          <Button
            onClick={handleConfirm}
            disabled={pending || !bureauId || reason.trim().length < 3}
          >
            {pending && <Loader2 className="size-4 animate-spin" />}
            Transfer
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}

function DisposeDialog({ complaint, onDone }: { complaint: Complaint; onDone: () => void }) {
  const [open, setOpen] = useState(false);
  const [note, setNote] = useState("");
  const [pending, setPending] = useState(false);

  async function handleConfirm() {
    setPending(true);
    try {
      await runAction(
        `/complaints/${complaint.id}/dispose`,
        { disposal_note: note },
        () => {
          onDone();
          setOpen(false);
          setNote("");
        },
        "Case disposed",
      );
    } finally {
      setPending(false);
    }
  }

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button size="sm">Dispose</Button>
      </DialogTrigger>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Dispose case</DialogTitle>
          <DialogDescription>
            Record the resolution. Disposed cases can only be reopened by a system administrator.
          </DialogDescription>
        </DialogHeader>
        <div className="space-y-2">
          <Label htmlFor="disposal-note">Disposal note</Label>
          <Textarea
            id="disposal-note"
            value={note}
            onChange={(e) => setNote(e.target.value)}
            rows={4}
          />
        </div>
        <DialogFooter>
          <Button onClick={handleConfirm} disabled={pending || note.trim().length < 3}>
            {pending && <Loader2 className="size-4 animate-spin" />}
            Confirm disposal
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}

function AssignDialog({ complaint, onDone }: { complaint: Complaint; onDone: () => void }) {
  const [open, setOpen] = useState(false);
  // null = not yet loaded for this dialog session; avoids a synchronous
  // setState(true) at the top of the effect (react-hooks/set-state-in-effect).
  const [officers, setOfficers] = useState<Officer[] | null>(null);
  const [officerId, setOfficerId] = useState<string | undefined>();
  const [pending, setPending] = useState(false);
  const loading = open && officers === null;

  useEffect(() => {
    if (!open) return;
    let cancelled = false;
    apiFetch<Officer[]>(`/reference/officers?bureau_id=${complaint.bureau_id}`)
      .then((result) => {
        if (!cancelled) setOfficers(result);
      })
      .catch(() => {
        if (!cancelled) toast.error("Could not load officers");
      });
    return () => {
      cancelled = true;
    };
  }, [open, complaint.bureau_id]);

  async function handleConfirm() {
    if (!officerId) return;
    setPending(true);
    try {
      await runAction(
        `/complaints/${complaint.id}/assign`,
        { officer_id: Number(officerId) },
        () => {
          onDone();
          setOpen(false);
          setOfficerId(undefined);
        },
        "Officer assigned",
      );
    } finally {
      setPending(false);
    }
  }

  return (
    <Dialog
      open={open}
      onOpenChange={(next) => {
        setOpen(next);
        if (!next) setOfficers(null);
      }}
    >
      <DialogTrigger asChild>
        <Button variant="outline" size="sm">
          Assign
        </Button>
      </DialogTrigger>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Assign officer</DialogTitle>
          <DialogDescription>
            Assign this case to an officer in the handling bureau.
          </DialogDescription>
        </DialogHeader>
        <div className="space-y-2">
          <Label id="assign-officer-label">Officer</Label>
          <Select value={officerId} onValueChange={setOfficerId} disabled={loading}>
            <SelectTrigger className="w-full" aria-labelledby="assign-officer-label">
              <SelectValue placeholder={loading ? "Loading..." : "Select officer"} />
            </SelectTrigger>
            <SelectContent>
              {(officers ?? []).map((o) => (
                <SelectItem key={o.id} value={String(o.id)}>
                  {o.full_name} ({o.employee_code})
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
        <DialogFooter>
          <Button onClick={handleConfirm} disabled={pending || !officerId}>
            {pending && <Loader2 className="size-4 animate-spin" />}
            Assign
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
