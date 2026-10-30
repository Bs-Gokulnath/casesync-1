"use client";

import { motion } from "motion/react";
import { Radar } from "lucide-react";
import { LoginForm } from "@/features/auth/LoginForm";

export function LoginCard() {
  return (
    <motion.div
      initial={{ opacity: 0, y: 24, scale: 0.98 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      transition={{ duration: 0.6, ease: [0.16, 1, 0.3, 1] }}
      className="w-full max-w-sm"
    >
      <motion.div
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1, duration: 0.5 }}
        className="mb-8 flex flex-col items-center text-center"
      >
        <div className="glow-primary mb-4 flex size-14 items-center justify-center rounded-2xl bg-gradient-to-br from-[#7c6cff] to-[#22d3ee]">
          <Radar className="size-7 text-white" strokeWidth={2} />
        </div>
        <h1 className="font-display text-xl font-semibold tracking-tight text-white">
          AICTE CaseWatch
        </h1>
        <p className="text-muted-foreground mt-1.5 text-sm">
          Sign in to the institution complaint dashboard
        </p>
      </motion.div>

      <motion.div
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2, duration: 0.5 }}
        className="glass glow-primary rounded-2xl p-7"
      >
        <LoginForm />
      </motion.div>

      <motion.p
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.4 }}
        className="text-muted-foreground mt-5 text-center text-xs"
      >
        Demo credentials: any seeded account, password{" "}
        <code className="text-foreground">Demo@12345</code>
      </motion.p>
    </motion.div>
  );
}
