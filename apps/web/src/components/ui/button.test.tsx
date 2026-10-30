import { describe, expect, it, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { Button } from "@/components/ui/button";

describe("Button", () => {
  it("renders its label and responds to clicks", async () => {
    const onClick = vi.fn();
    render(<Button onClick={onClick}>Save complaint</Button>);

    const button = screen.getByRole("button", { name: "Save complaint" });
    await userEvent.click(button);

    expect(onClick).toHaveBeenCalledOnce();
  });

  it("disables interaction when disabled", () => {
    render(<Button disabled>Save complaint</Button>);
    expect(screen.getByRole("button", { name: "Save complaint" })).toBeDisabled();
  });
});
