import { z } from "zod";

export const institutionFormSchema = z.object({
  name: z.string().min(2, "Name must be at least 2 characters").max(300),
  region_id: z.coerce.number({ error: "Select a region" }).int().positive(),
  aicte_permanent_id: z.string().max(64).optional().or(z.literal("")),
  address: z.string().max(500).optional().or(z.literal("")),
  contact_email: z.string().email("Enter a valid email").optional().or(z.literal("")),
  contact_phone: z.string().max(32).optional().or(z.literal("")),
});

// z.coerce fields have a different input type (unknown, pre-coercion) than
// output type (number, post-coercion); react-hook-form's resolver needs both.
export type InstitutionFormInput = z.input<typeof institutionFormSchema>;
export type InstitutionFormValues = z.output<typeof institutionFormSchema>;
