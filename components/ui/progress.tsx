import { cn } from "../utils/cn";

interface ProgressProps {
  value: number;
  max?: number;
  variant?: "primary" | "success" | "warning" | "danger" | "info";
  size?: "sm" | "md";
  className?: string;
}

const barColors = {
  primary: "bg-primary",
  success: "bg-success",
  warning: "bg-warning",
  danger: "bg-danger",
  info: "bg-info",
};

export function Progress({
  value,
  max = 100,
  variant = "primary",
  size = "md",
  className,
}: ProgressProps) {
  const pct = Math.min(100, Math.max(0, (value / max) * 100));

  return (
    <div
      role="progressbar"
      aria-valuenow={value}
      aria-valuemin={0}
      aria-valuemax={max}
      className={cn(
        "w-full overflow-hidden rounded-full bg-muted",
        size === "sm" ? "h-1.5" : "h-2.5",
        className
      )}
    >
      <div
        className={cn("h-full rounded-full transition-all", barColors[variant])}
        style={{ width: `${pct}%` }}
      />
    </div>
  );
}
