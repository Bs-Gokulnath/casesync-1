"use client";

import Link from "next/link";
import { flexRender, getCoreRowModel, useReactTable, type ColumnDef } from "@tanstack/react-table";
import { Badge } from "@/components/ui/badge";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import type { Institution, Region } from "@/types/api";

export function InstitutionsTable({
  institutions,
  regions,
}: {
  institutions: Institution[];
  regions: Region[];
}) {
  const regionNameById = new Map(regions.map((r) => [r.id, r.name]));

  const columns: ColumnDef<Institution>[] = [
    {
      accessorKey: "institution_code",
      header: "Code",
      cell: ({ row }) => (
        <span className="text-muted-foreground font-mono text-xs">
          {row.original.institution_code}
        </span>
      ),
    },
    {
      accessorKey: "name",
      header: "Institution",
      cell: ({ row }) => (
        <Link
          href={`/institutions/${row.original.id}`}
          className="font-medium text-white hover:text-[#9b8dff] hover:underline"
        >
          {row.original.name}
        </Link>
      ),
    },
    {
      accessorKey: "region_id",
      header: "Region",
      cell: ({ row }) => regionNameById.get(row.original.region_id) ?? "—",
    },
    {
      accessorKey: "aicte_permanent_id",
      header: "AICTE Permanent ID",
      cell: ({ row }) => row.original.aicte_permanent_id ?? "—",
    },
    {
      accessorKey: "is_active",
      header: "Status",
      cell: ({ row }) => (
        <Badge variant={row.original.is_active ? "default" : "secondary"}>
          {row.original.is_active ? "Active" : "Inactive"}
        </Badge>
      ),
    },
  ];

  const table = useReactTable({ data: institutions, columns, getCoreRowModel: getCoreRowModel() });

  if (institutions.length === 0) {
    return (
      <div className="text-muted-foreground rounded-2xl border border-dashed border-white/15 p-10 text-center text-sm">
        No institutions match your search.
      </div>
    );
  }

  return (
    <div className="glass overflow-hidden rounded-2xl">
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
