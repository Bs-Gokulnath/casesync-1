"use client";

import Link from "next/link";
import { flexRender, getCoreRowModel, useReactTable, type ColumnDef } from "@tanstack/react-table";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { StatusBadge, PriorityBadge } from "@/components/data-display/StatusBadge";
import type { Bureau, Complaint, ComplaintCategory } from "@/types/api";

export function ComplaintsTable({
  complaints,
  bureaus,
  categories,
}: {
  complaints: Complaint[];
  bureaus: Bureau[];
  categories: ComplaintCategory[];
}) {
  const bureauNameById = new Map(bureaus.map((b) => [b.id, b.name]));
  const categoryNameById = new Map(categories.map((c) => [c.id, c.name]));

  const columns: ColumnDef<Complaint>[] = [
    {
      accessorKey: "case_reference",
      header: "Case",
      cell: ({ row }) => (
        <Link
          href={`/complaints/${row.original.id}`}
          className="font-mono text-xs font-medium text-white hover:text-[#9b8dff] hover:underline"
        >
          {row.original.case_reference}
        </Link>
      ),
    },
    {
      accessorKey: "subject",
      header: "Subject",
      cell: ({ row }) => (
        <span className="text-foreground/80 line-clamp-1 max-w-xs text-sm">
          {row.original.subject}
        </span>
      ),
    },
    {
      accessorKey: "category_id",
      header: "Category",
      cell: ({ row }) => categoryNameById.get(row.original.category_id) ?? "—",
    },
    {
      accessorKey: "bureau_id",
      header: "Bureau",
      cell: ({ row }) => bureauNameById.get(row.original.bureau_id) ?? "—",
    },
    {
      accessorKey: "priority",
      header: "Priority",
      cell: ({ row }) => <PriorityBadge priority={row.original.priority} />,
    },
    {
      accessorKey: "status",
      header: "Status",
      cell: ({ row }) => <StatusBadge status={row.original.status} />,
    },
    {
      accessorKey: "received_date",
      header: "Received",
      cell: ({ row }) => new Date(row.original.received_date).toLocaleDateString("en-IN"),
    },
  ];

  const table = useReactTable({ data: complaints, columns, getCoreRowModel: getCoreRowModel() });

  if (complaints.length === 0) {
    return (
      <div className="text-muted-foreground rounded-2xl border border-dashed border-white/15 p-10 text-center text-sm">
        No complaints match your filters.
      </div>
    );
  }

  return (
    <div className="glass overflow-x-auto rounded-2xl">
      <Table>
        <TableHeader>
          {table.getHeaderGroups().map((headerGroup) => (
            <TableRow key={headerGroup.id}>
              {headerGroup.headers.map((header) => (
                <TableHead key={header.id}>
                  {flexRender(header.column.columnDef.header, header.getContext())}
                </TableHead>
              ))}
            </TableRow>
          ))}
        </TableHeader>
        <TableBody>
          {table.getRowModel().rows.map((row) => (
            <TableRow key={row.id}>
              {row.getVisibleCells().map((cell) => (
                <TableCell key={cell.id}>
                  {flexRender(cell.column.columnDef.cell, cell.getContext())}
                </TableCell>
              ))}
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  );
}
