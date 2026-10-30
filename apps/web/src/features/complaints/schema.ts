import { z } from "zod";

export const complaintFormSchema = z.object({
  institution_id: z.coerce.number({ error: "Select an institution" }).int().positive(),
  category_id: z.coerce.number({ error: "Select a category" }).int().positive(),
  subject: z.string().min(3, "Subject must be at least 3 characters").max(300),
  description: z.string().min(10, "Please provide more detail (at least 10 characters)"),
  priority: z.enum(["low", "medium", "high", "critical"]),
  source: z.enum(["portal", "email", "letter", "phone", "walk_in", "other"]),
  bureau_id: z.coerce.number().int().positive().optional(),
});

// z.coerce fields have a different input type (unknown, pre-coercion) than
// output type (number, post-coercion); react-hook-form's resolver needs both.
export type ComplaintFormInput = z.input<typeof complaintFormSchema>;
export type ComplaintFormValues = z.output<typeof complaintFormSchema>;
