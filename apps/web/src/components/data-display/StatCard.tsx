"use client";

import { useEffect, useRef } from "react";
import { motion, useInView, useMotionValue, useSpring } from "motion/react";
import { cn } from "@/lib/utils";

interface StatCardProps {
  label: string;
  value: string | number;
  hint?: string;
  tone?: "default" | "warning" | "danger";
  icon?: React.ReactNode;
}

const TONE_STYLES: Record<
  NonNullable<StatCardProps["tone"]>,
  { text: string; glow: string; bar: string }
> = {
  default: {
    text: "text-white",
    glow: "shadow-[0_0_30px_-12px_#7c6cff]",
    bar: "from-[#7c6cff] to-[#9b6cff]",
  },
  warning: {
    text: "text-[#fbbf24]",
    glow: "shadow-[0_0_30px_-12px_#fbbf24]",
    bar: "from-[#fbbf24] to-[#f59e0b]",
  },
  danger: {
    text: "text-[#fb4570]",
    glow: "shadow-[0_0_30px_-12px_#fb4570]",
    bar: "from-[#fb4570] to-[#ec4899]",
  },
};

function AnimatedNumber({ value }: { value: number }) {
  const ref = useRef<HTMLSpanElement>(null);
  const inView = useInView(ref, { once: true });
  const motionValue = useMotionValue(0);
  const spring = useSpring(motionValue, { duration: 1200, bounce: 0.15 });

  useEffect(() => {
    if (inView) motionValue.set(value);
  }, [inView, value, motionValue]);

  useEffect(
    () =>
      spring.on("change", (latest) => {
        if (ref.current) ref.current.textContent = Math.round(latest).toLocaleString("en-IN");
      }),
    [spring],
  );

  return <span ref={ref}>0</span>;
}

export function StatCard({ label, value, hint, tone = "default", icon }: StatCardProps) {
  const styles = TONE_STYLES[tone];
  const isNumeric = typeof value === "number";

  return (
    <motion.div
      whileHover={{ y: -3 }}
      transition={{ type: "spring", stiffness: 300, damping: 24 }}
      className={cn("glass group relative overflow-hidden rounded-2xl p-5", styles.glow)}
    >
      <div className={cn("absolute inset-x-0 top-0 h-[2px] bg-gradient-to-r", styles.bar)} />
      <div className="flex items-start justify-between">
        <p className="text-muted-foreground text-xs font-medium tracking-wider uppercase">
          {label}
        </p>
        {icon && <div className="text-muted-foreground/60">{icon}</div>}
      </div>
      <p className={cn("font-display mt-2 text-3xl font-semibold tabular-nums", styles.text)}>
        {isNumeric ? <AnimatedNumber value={value} /> : value}
      </p>
      {hint && <p className="text-muted-foreground mt-1 text-xs">{hint}</p>}
    </motion.div>
  );
}
