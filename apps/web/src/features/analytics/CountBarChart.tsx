"use client";

import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import type { CountByKey } from "@/types/api";

export function CountBarChart({ title, data }: { title: string; data: CountByKey[] }) {
  const chartData = data.map((d) => ({ name: d.label, count: d.count }));
  const gradientId = `bar-gradient-${title.replace(/\s+/g, "-")}`;

  return (
    <div className="glass rounded-2xl p-5">
      <h3 className="font-display text-sm font-semibold text-white">{title}</h3>
      {chartData.length === 0 ? (
        <p className="text-muted-foreground mt-4 text-sm">No data yet.</p>
      ) : (
        <div className="mt-3 h-56">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={chartData} layout="vertical" margin={{ left: 8, right: 16 }}>
              <defs>
                <linearGradient id={gradientId} x1="0" y1="0" x2="1" y2="0">
                  <stop offset="0%" stopColor="#7c6cff" />
                  <stop offset="100%" stopColor="#22d3ee" />
                </linearGradient>
              </defs>
              <CartesianGrid horizontal={false} stroke="rgba(255,255,255,0.08)" />
              <XAxis
                type="number"
                allowDecimals={false}
                tick={{ fontSize: 12, fill: "#8d92b3" }}
                axisLine={{ stroke: "rgba(255,255,255,0.1)" }}
                tickLine={false}
              />
              <YAxis
                type="category"
                dataKey="name"
                width={120}
                tick={{ fontSize: 12, fill: "#c7cbea" }}
                axisLine={{ stroke: "rgba(255,255,255,0.1)" }}
                tickLine={false}
              />
              <Tooltip
                cursor={{ fill: "rgba(124,108,255,0.08)" }}
                contentStyle={{
                  fontSize: 12,
                  borderRadius: 12,
                  border: "1px solid rgba(255,255,255,0.1)",
                  background: "#0c0e19",
                  color: "#e7e9f7",
                }}
                labelStyle={{ color: "#e7e9f7" }}
              />
              <Bar
                dataKey="count"
                fill={`url(#${gradientId})`}
                radius={[0, 6, 6, 0]}
                maxBarSize={20}
              />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}
    </div>
  );
}
