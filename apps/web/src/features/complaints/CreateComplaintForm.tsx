"use client";

import { useRouter } from "next/navigation";
import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import { Loader2 } from "lucide-react";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
  FormDescription,
} from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { apiFetch } from "@/lib/api/browser-client";
import type { Bureau, Complaint, ComplaintCategory, Institution } from "@/types/api";
import {
  complaintFormSchema,
  type ComplaintFormInput,
  type ComplaintFormValues,
} from "@/features/complaints/schema";

const PRIORITIES = ["low", "medium", "high", "critical"] as const;
const SOURCES = ["portal", "email", "letter", "phone", "walk_in", "other"] as const;

export function CreateComplaintForm({
  institutions,
  categories,
  bureaus,
  showBureauSelect,
}: {
  institutions: Institution[];
  categories: ComplaintCategory[];
  bureaus: Bureau[];
  showBureauSelect: boolean;
}) {
  const router = useRouter();

  const form = useForm<ComplaintFormInput, unknown, ComplaintFormValues>({
    resolver: zodResolver(complaintFormSchema),
    defaultValues: {
      subject: "",
      description: "",
      priority: "medium",
      source: "portal",
    },
  });

  async function onSubmit(values: ComplaintFormValues) {
    try {
      const complaint = await apiFetch<Complaint>("/complaints", {
        method: "POST",
        body: JSON.stringify(values),
      });
      toast.success(`Complaint ${complaint.case_reference} registered`);
      router.push(`/complaints/${complaint.id}`);
      router.refresh();
    } catch {
      toast.error("Could not create complaint");
    }
  }

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)} className="max-w-2xl space-y-5" noValidate>
        <FormField
          control={form.control}
          name="institution_id"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Institution</FormLabel>
              <Select
                onValueChange={field.onChange}
                value={field.value ? String(field.value) : undefined}
              >
                <FormControl>
                  <SelectTrigger className="w-full">
                    <SelectValue placeholder="Select institution" />
                  </SelectTrigger>
                </FormControl>
                <SelectContent>
                  {institutions.map((inst) => (
                    <SelectItem key={inst.id} value={String(inst.id)}>
                      {inst.name} ({inst.institution_code})
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              <FormMessage />
            </FormItem>
          )}
        />

        <FormField
          control={form.control}
          name="category_id"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Category</FormLabel>
              <Select
                onValueChange={field.onChange}
                value={field.value ? String(field.value) : undefined}
              >
                <FormControl>
                  <SelectTrigger className="w-full">
                    <SelectValue placeholder="Select category" />
                  </SelectTrigger>
                </FormControl>
                <SelectContent>
                  {categories.map((cat) => (
                    <SelectItem key={cat.id} value={String(cat.id)}>
                      {cat.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              <FormMessage />
            </FormItem>
          )}
        />

        {showBureauSelect && (
          <FormField
            control={form.control}
            name="bureau_id"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Handling bureau</FormLabel>
                <Select
                  onValueChange={field.onChange}
                  value={field.value ? String(field.value) : undefined}
                >
                  <FormControl>
                    <SelectTrigger className="w-full">
                      <SelectValue placeholder="Select bureau" />
                    </SelectTrigger>
                  </FormControl>
                  <SelectContent>
                    {bureaus.map((bureau) => (
                      <SelectItem key={bureau.id} value={String(bureau.id)}>
                        {bureau.name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                <FormDescription>
                  Your role isn&apos;t tied to one bureau, so pick the one handling this case.
                </FormDescription>
                <FormMessage />
              </FormItem>
            )}
          />
        )}

        <FormField
          control={form.control}
          name="subject"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Subject</FormLabel>
              <FormControl>
                <Input {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        <FormField
          control={form.control}
          name="description"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Description</FormLabel>
              <FormControl>
                <Textarea rows={5} {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        <div className="grid grid-cols-2 gap-4">
          <FormField
            control={form.control}
            name="priority"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Priority</FormLabel>
                <Select onValueChange={field.onChange} defaultValue={field.value}>
                  <FormControl>
                    <SelectTrigger className="w-full">
                      <SelectValue />
                    </SelectTrigger>
                  </FormControl>
                  <SelectContent>
                    {PRIORITIES.map((p) => (
                      <SelectItem key={p} value={p}>
                        {p[0].toUpperCase() + p.slice(1)}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                <FormMessage />
              </FormItem>
            )}
          />
          <FormField
            control={form.control}
            name="source"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Source</FormLabel>
                <Select onValueChange={field.onChange} defaultValue={field.value}>
                  <FormControl>
                    <SelectTrigger className="w-full">
                      <SelectValue />
                    </SelectTrigger>
                  </FormControl>
                  <SelectContent>
                    {SOURCES.map((s) => (
                      <SelectItem key={s} value={s}>
                        {s.replace("_", " ")}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                <FormMessage />
              </FormItem>
            )}
          />
        </div>

        <Button type="submit" disabled={form.formState.isSubmitting}>
          {form.formState.isSubmitting && <Loader2 className="size-4 animate-spin" />}
          Register complaint
        </Button>
      </form>
    </Form>
  );
}
