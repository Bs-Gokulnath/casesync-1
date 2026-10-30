"use client";

import { useId, useState } from "react";
import { useRouter } from "next/navigation";
import { Loader2, Plus } from "lucide-react";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { apiFetch, ApiError } from "@/lib/api/browser-client";

interface Entity {
  id: number;
  code: string;
  name: string;
  description?: string | null;
  is_active: boolean;
}

export function ReferenceEntityManager({
  title,
  basePath,
  items,
  hasDescription = false,
}: {
  title: string;
  basePath: string;
  items: Entity[];
  hasDescription?: boolean;
}) {
  const router = useRouter();
  const instanceId = useId();
  const codeId = `${instanceId}-code`;
  const nameId = `${instanceId}-name`;
  const descriptionId = `${instanceId}-description`;
  const [code, setCode] = useState("");
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [submitting, setSubmitting] = useState(false);

  async function handleCreate(e: React.FormEvent) {
    e.preventDefault();
    setSubmitting(true);
    try {
      await apiFetch(basePath, {
        method: "POST",
        body: JSON.stringify({
          code,
          name,
          ...(hasDescription ? { description: description || null } : {}),
        }),
      });
      toast.success(`${title.slice(0, -1)} created`);
      setCode("");
      setName("");
      setDescription("");
      router.refresh();
    } catch (error) {
      toast.error(error instanceof ApiError ? error.message : "Could not create");
    } finally {
      setSubmitting(false);
    }
  }

  async function toggleActive(item: Entity) {
    try {
      await apiFetch(`${basePath}/${item.id}`, {
        method: "PATCH",
        body: JSON.stringify({ is_active: !item.is_active }),
      });
      router.refresh();
    } catch {
      toast.error("Could not update status");
    }
  }

  return (
    <div className="space-y-3">
      <h2 className="font-display text-sm font-semibold text-white">{title}</h2>
      <form onSubmit={handleCreate} className="flex flex-wrap items-end gap-2">
        <div>
          <Label htmlFor={codeId} className="text-muted-foreground text-xs">
            Code
          </Label>
          <Input
            id={codeId}
            value={code}
            onChange={(e) => setCode(e.target.value)}
            className="w-28"
            required
          />
        </div>
        <div>
          <Label htmlFor={nameId} className="text-muted-foreground text-xs">
            Name
          </Label>
          <Input
            id={nameId}
            value={name}
            onChange={(e) => setName(e.target.value)}
            className="w-56"
            required
          />
        </div>
        {hasDescription && (
          <div>
            <Label htmlFor={descriptionId} className="text-muted-foreground text-xs">
              Description
            </Label>
            <Input
              id={descriptionId}
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              className="w-64"
            />
          </div>
        )}
        <Button type="submit" size="sm" disabled={submitting}>
          {submitting ? <Loader2 className="size-4 animate-spin" /> : <Plus className="size-4" />}
          Add
        </Button>
      </form>

      <div className="glass overflow-hidden rounded-2xl">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Code</TableHead>
              <TableHead>Name</TableHead>
              <TableHead>Status</TableHead>
              <TableHead />
            </TableRow>
          </TableHeader>
          <TableBody>
            {items.map((item) => (
              <TableRow key={item.id}>
                <TableCell className="font-mono text-xs">{item.code}</TableCell>
                <TableCell className="text-sm">{item.name}</TableCell>
                <TableCell>
                  <Badge variant={item.is_active ? "default" : "secondary"}>
                    {item.is_active ? "Active" : "Inactive"}
                  </Badge>
                </TableCell>
                <TableCell>
                  <Button variant="ghost" size="sm" onClick={() => toggleActive(item)}>
                    {item.is_active ? "Deactivate" : "Activate"}
                  </Button>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>
    </div>
  );
}
