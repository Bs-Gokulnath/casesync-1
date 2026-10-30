import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Search } from "lucide-react";

export function SearchForm({
  action,
  defaultValue,
  placeholder,
  children,
}: {
  action: string;
  defaultValue?: string;
  placeholder?: string;
  children?: React.ReactNode;
}) {
  return (
    <form
      action={action}
      method="GET"
      className="flex flex-col gap-2 sm:flex-row sm:flex-wrap sm:items-center"
    >
      <div className="relative w-full sm:max-w-sm sm:flex-1">
        <Search className="text-muted-foreground pointer-events-none absolute top-1/2 left-2.5 size-4 -translate-y-1/2" />
        <Input
          type="search"
          name="q"
          defaultValue={defaultValue}
          placeholder={placeholder ?? "Search..."}
          className="pl-8"
        />
      </div>
      {children}
      <Button type="submit" variant="secondary">
        Search
      </Button>
    </form>
  );
}
